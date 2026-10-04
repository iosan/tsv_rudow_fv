#!/usr/bin/env python3
import hashlib
import html
import os
import re
import sys
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from pathlib import Path

BASE_DIR = Path('/opt/aktuelles-mail-service')
STORAGE_DIR = BASE_DIR / 'storage'
SITE_ROOT = Path('/var/www/tsv_rudow_fv')
SITE_HTML = SITE_ROOT / 'html' / 'aktuelles.html'
SITE_IMAGES = SITE_ROOT / 'html' / 'images'
INSERT_MARKER = '<div class="upload-parent-box">'


def load_allowlist(path: Path):
    allowed = set()
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            cleaned = line.strip()
            if cleaned and not cleaned.startswith('#'):
                allowed.add(cleaned.lower())
    return allowed


def normalize_title(value: str | None) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def parse_post_command(about_field: str | None):
    if not about_field:
        return None
    match = re.match(r'(?is)^\s*post\s+(.+?)\s*$', about_field.strip())
    if not match:
        return None
    title = normalize_title(match.group(1))
    return title or None


def parse_delete_command(about_field: str | None):
    if not about_field:
        return None
    match = re.match(r'(?is)^\s*(?:del(?:ete)?|remove)\s+(.+?)\s*$', about_field.strip())
    if not match:
        return None
    title = normalize_title(match.group(1))
    return title or None


def parse_title_command(about_field: str | None):
    if not about_field:
        return None
    normalized = about_field.strip()
    if not normalized:
        return None
    post_title = parse_post_command(normalized)
    if post_title:
        return ('post', post_title)
    delete_title = parse_delete_command(normalized)
    if delete_title:
        return ('delete', delete_title)
    return None


def safe_name(name: str) -> str:
    clean = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')
    return clean or 'mail-upload'


def sanitize_text(value: str) -> str:
    value = value.replace('\r\n', '\n').replace('\r', '\n')
    value = re.sub(r'<script.*?</script>', ' ', value, flags=re.I | re.S)
    value = re.sub(r'<style.*?</style>', ' ', value, flags=re.I | re.S)
    value = re.sub(r'<[^>]+>', ' ', value)
    value = html.unescape(value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def collapse_repeated_text_block(value: str) -> str:
    cleaned = sanitize_text(value)
    if not cleaned:
        return ''

    for block_size in range(len(cleaned) // 2, 0, -1):
        block = cleaned[:block_size].strip()
        if not block:
            continue
        pattern = rf'(?:\s*{re.escape(block)}\s*)+'
        if re.fullmatch(pattern, cleaned):
            return block
    return cleaned


def build_article(title: str, text: str, image_src: str, alt_text: str, date_str: str) -> str:
    safe_title = re.sub(r'<.*?>', '', title).strip() or 'Neues aus dem Verein'
    safe_text = sanitize_text(text)
    safe_alt = re.sub(r'<.*?>', '', alt_text).strip() or safe_title
    return (
        '<article class="upload-card">\n'
        '    <div class="upload-media">\n'
        f'        <img src="{image_src}" alt="{safe_alt}">\n'
        '    </div>\n'
        '    <div class="upload-copy">\n'
        '        <span class="upload-tag">To be posted</span>\n'
        f'        <h3>{safe_title}</h3>\n'
        f'        <p><strong>{date_str}</strong></p>\n'
        f'        <p>{safe_text}</p>\n'
        '    </div>\n'
        '</article>'
    )


def delete_matching_posts(html_document: str, title: str) -> str:
    if not html_document or not title:
        return html_document
    plain_title = normalize_title(title)
    if not plain_title:
        return html_document

    pattern = re.compile(
        r'(?is)<article\b(?=[^>]*\bclass=(?:\"[^\"]*\bupload-card\b[^\"]*\"|\'[^\']*\bupload-card\b[^\']*\'|[^\s>]*\bupload-card\b[^\s>]*))[^>]*>.*?</article>'
    )

    def remove_matching_article(match: re.Match[str]) -> str:
        article_html = match.group(0)
        heading_match = re.search(r'(?is)<h3\b[^>]*>(.*?)</h3>', article_html)
        if not heading_match:
            return article_html

        heading_text = normalize_title(re.sub(r'<[^>]+>', ' ', heading_match.group(1)))
        if heading_text == plain_title:
            return ''
        return article_html

    return pattern.sub(remove_matching_article, html_document)


def find_raw_messages():
    return sorted(STORAGE_DIR.glob('raw-*.eml'), key=lambda path: path.stat().st_mtime)


def process_raw_message(raw_file: Path):
    raw_email = raw_file.read_bytes()
    message = BytesParser(policy=policy.default).parsebytes(raw_email)
    sender = message.get('From', '').strip()
    allowlist = load_allowlist(BASE_DIR / 'config' / 'allowlist.txt')
    if sender.lower() not in allowlist:
        raw_file.unlink(missing_ok=True)
        raise PermissionError(f'Sender not allowed: {sender}')

    about_field = message.get('Subject') or message.get('About') or ''
    mail_command = parse_title_command(about_field)
    if mail_command is None:
        raw_file.unlink(missing_ok=True)
        raise ValueError("Ignored mail: about/subject must start with 'post <title>' or 'del <title>'")

    action, title = mail_command
    if action == 'delete':
        html_document = SITE_HTML.read_text(encoding='utf-8')
        updated_html = delete_matching_posts(html_document, title)
        SITE_HTML.write_text(updated_html, encoding='utf-8')
        os.chmod(SITE_HTML, 0o644)
        raw_file.unlink(missing_ok=True)
        print(f'Deleted posts titled: {title}')
        return title

    text_parts = []
    seen_text = set()
    image_name = None
    image_bytes = None
    for part in message.walk():
        if part.get_content_maintype() == 'text' and part.get_content_disposition() != 'attachment':
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or 'utf-8'
                decoded = payload.decode(charset, errors='replace')
                normalized = collapse_repeated_text_block(decoded)
                if not normalized:
                    continue
                dedupe_key = normalized.lower()
                if dedupe_key in seen_text:
                    continue
                seen_text.add(dedupe_key)
                text_parts.append(normalized)
        if part.get_content_maintype() == 'image' and image_bytes is None:
            image_name = part.get_filename() or 'mail-upload.png'
            image_bytes = part.get_payload(decode=True) or b''

    if not text_parts or not image_bytes or not image_name:
        raw_file.unlink(missing_ok=True)
        raise ValueError('Ignored mail: missing valid text and image content')

    text = sanitize_text('\n'.join(text_parts))
    if not text:
        raw_file.unlink(missing_ok=True)
        raise ValueError('Ignored mail: no valid mail text found')

    message_hash = hashlib.sha256(raw_email).hexdigest()[:16]
    image_filename = f'{message_hash}-{safe_name(image_name)}'
    SITE_IMAGES.mkdir(parents=True, exist_ok=True)
    image_path = SITE_IMAGES / image_filename
    image_path.write_bytes(image_bytes)
    os.chmod(image_path, 0o644)

    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    article = build_article(
        title=title,
        text=text,
        image_src=f'images/{image_filename}',
        alt_text=title,
        date_str=date_str,
    )

    html_document = SITE_HTML.read_text(encoding='utf-8')
    if INSERT_MARKER not in html_document:
        raw_file.unlink(missing_ok=True)
        raise ValueError('Aktuelles insertion marker missing')

    updated_html = html_document.replace(INSERT_MARKER, f'{article}\n{INSERT_MARKER}', 1)
    SITE_HTML.write_text(updated_html, encoding='utf-8')
    os.chmod(SITE_HTML, 0o644)

    raw_file.unlink(missing_ok=True)
    print(article)
    return article


def process_pending_messages():
    pending_files = find_raw_messages()
    if not pending_files:
        raise FileNotFoundError('No processed message found')

    processed = []
    for raw_file in pending_files:
        processed.append(process_raw_message(raw_file))
    return processed


if __name__ == '__main__':
    try:
        process_pending_messages()
        print('Published all queued allowlisted mails to Aktuelles')
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
