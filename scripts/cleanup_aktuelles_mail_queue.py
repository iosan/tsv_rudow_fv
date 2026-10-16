#!/usr/bin/env python3
import re
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

BASE_DIR = Path('/opt/aktuelles-mail-service')
STORAGE_DIR = BASE_DIR / 'storage'
SITE_HTML = Path('/var/www/tsv_rudow_fv/html/aktuelles.html')


def normalize_title(value: str | None) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def parse_delete_command(about_field: str | None):
    if not about_field:
        return None
    match = re.match(r'(?is)^\s*(?:del(?:ete)?|remove)\s+(.+?)\s*$', about_field.strip())
    if not match:
        return None
    title = normalize_title(match.group(1))
    return title or None


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


def clean_queue():
    if not SITE_HTML.exists():
        raise FileNotFoundError(f'Website file missing: {SITE_HTML}')

    cleaned = 0
    pending_files = sorted(STORAGE_DIR.glob('raw-*.eml'), key=lambda path: path.stat().st_mtime)
    for raw_file in pending_files:
        raw_email = raw_file.read_bytes()
        message = BytesParser(policy=policy.default).parsebytes(raw_email)
        subject = message.get('Subject') or message.get('About') or ''
        title = parse_delete_command(subject)
        if title is None:
            raw_file.unlink(missing_ok=True)
            print(f'Ignored and removed stale queue item: {raw_file.name}')
            cleaned += 1
            continue

        current_html = SITE_HTML.read_text(encoding='utf-8')
        updated_html = delete_matching_posts(current_html, title)
        SITE_HTML.write_text(updated_html, encoding='utf-8')
        raw_file.unlink(missing_ok=True)
        print(f'Deleted posts titled: {title}')
        cleaned += 1

    return cleaned


if __name__ == '__main__':
    try:
        count = clean_queue()
        print(f'Cleaned {count} queued mail entries.')
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
