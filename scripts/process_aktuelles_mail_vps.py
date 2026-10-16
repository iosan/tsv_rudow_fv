#!/usr/bin/env python3
import hashlib
import html
import os
import re
import subprocess
import sys
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path

ALLOWLIST_PATH = Path('/opt/aktuelles-mail-service/config/allowlist.txt')
INCOMING_DIR = Path('/opt/aktuelles-mail-service/storage')
IMAGES_DIR = INCOMING_DIR / 'images'
LOG_DIR = Path('/opt/aktuelles-mail-service/logs')
SITE_HTML = Path('/var/www/tsv_rudow_fv/html/aktuelles.html')


def extract_email_address(value: str | None) -> str:
    if not value:
        return ''
    cleaned = value.strip()
    if not cleaned:
        return ''
    parsed_name, parsed_email = parseaddr(cleaned)
    if parsed_email:
        return parsed_email.strip().lower()
    return cleaned.lower()


def load_allowlist(path: Path):
    allowed = set()
    if not path.exists():
        return allowed
    for line in path.read_text(encoding='utf-8').splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith('#'):
            continue
        email = extract_email_address(cleaned)
        if email:
            allowed.add(email)
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


def is_valid_image_name(name: str | None) -> bool:
    if not name:
        return False
    filename = str(name).strip()
    if not filename:
        return False
    suffix = filename.rsplit('.', 1)[-1].upper() if '.' in filename else ''
    return suffix in {'PNG', 'JPG', 'JPEG', 'GIF', 'WEBP', 'BMP', 'TIFF'}


def is_allowed(sender: str, allowlist: set[str]) -> bool:
    if not sender:
        return False
    sender_email = extract_email_address(sender)
    if not sender_email:
        return False
    return sender_email in {extract_email_address(value) for value in allowlist}


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


def extract_text(message):
    chunks = []
    seen = set()

    def add_text_chunk(value: str):
        if not value:
            return
        cleaned = collapse_repeated_text_block(value)
        if not cleaned:
            return
        key = cleaned.lower()
        if key in seen:
            return
        seen.add(key)
        chunks.append(cleaned)

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() == 'text' and part.get_content_disposition() != 'attachment':
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                content = payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
                add_text_chunk(content)
    else:
        payload = message.get_payload(decode=True)
        if payload:
            content = payload.decode(message.get_content_charset() or 'utf-8', errors='replace')
            add_text_chunk(content)
    return '\n'.join(chunks).strip()


def extract_image(message):
    for part in message.walk():
        if part.get_content_maintype() == 'image':
            filename = part.get_filename() or 'mail-upload.png'
            payload = part.get_payload(decode=True) or b''
            if payload:
                return filename, payload
    return None, None


def safe_name(name: str) -> str:
    clean = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')
    return clean or 'mail-upload-image'


def sanitize_text(value: str) -> str:
    if not value:
        return ''
    cleaned = value.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = re.sub(r'<script.*?</script>', ' ', cleaned, flags=re.I | re.S)
    cleaned = re.sub(r'<style.*?</style>', ' ', cleaned, flags=re.I | re.S)
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


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


def main() -> int:
    msg = sys.stdin.buffer.read()
    if not msg:
        return 0

    allowlist = load_allowlist(ALLOWLIST_PATH)
    if not allowlist:
        print('No allowlist found', file=sys.stderr)
        return 1

    message = BytesParser(policy=policy.default).parsebytes(msg)
    sender = message.get('From', '')
    if not sender or not is_allowed(sender, allowlist):
        print(f'Rejected sender: {sender}', file=sys.stderr)
        return 1

    about_value = message.get('Subject') or message.get('About') or ''
    mail_command = parse_title_command(about_value)
    if mail_command is None:
        print("Rejected: about/subject must start with 'post <title>' or 'del <title>'", file=sys.stderr)
        return 1

    action, title = mail_command
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    message_hash = hashlib.sha256(msg).hexdigest()[:16]
    raw_path = INCOMING_DIR / f'raw-{message_hash}.eml'
    raw_path.write_bytes(msg)

    if action == 'delete':
        if SITE_HTML.exists():
            current_html = SITE_HTML.read_text(encoding='utf-8')
            updated_html = delete_matching_posts(current_html, title)
            if updated_html != current_html:
                SITE_HTML.write_text(updated_html, encoding='utf-8')
                os.chmod(SITE_HTML, 0o644)
        log_path = LOG_DIR / f'delete-{message_hash}.log'
        log_path.write_text(f'sender={sender}\nsubject={about_value}\ntitle={title}\n', encoding='utf-8')
        print(f'Deleted all posts titled: {title}')
        try:
            cleaned = subprocess.run(['/usr/local/bin/cleanup_aktuelles_mail_queue'], capture_output=True, text=True, check=True)
            if cleaned.stdout.strip():
                print(cleaned.stdout.strip())
            if cleaned.stderr.strip():
                print(cleaned.stderr.strip(), file=sys.stderr)
        except Exception as exc:
            print(f'Cleanup failed: {exc}', file=sys.stderr)
        return 0

    text = extract_text(message)
    image_name, image_data = extract_image(message)
    if not text or not image_name or not image_data:
        print('Rejected: missing text or image for post command', file=sys.stderr)
        return 1
    if not is_valid_image_name(image_name):
        print(f'Rejected: invalid image file extension for {image_name}', file=sys.stderr)
        return 1

    image_filename = f'{message_hash}-{safe_name(image_name)}'
    image_path = IMAGES_DIR / image_filename
    image_path.write_bytes(image_data)
    os.chmod(image_path, 0o644)
    log_path = LOG_DIR / f'received-{message_hash}.log'
    log_path.write_text(f'sender={sender}\ntext_length={len(text)}\nimage={image_filename}\n', encoding='utf-8')
    print(f'Accepted sender {sender} -> saved {image_filename}')

    try:
        published = subprocess.run(['/usr/local/bin/publish_aktuelles_mail'], capture_output=True, text=True, check=True)
        if published.stdout.strip():
            print(published.stdout.strip())
        if published.stderr.strip():
            print(published.stderr.strip(), file=sys.stderr)
    except Exception as exc:
        print(f'Publish failed: {exc}', file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
