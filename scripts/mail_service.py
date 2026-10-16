import html
import re
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr


ALLOWED_TEXT_TAGS = {"p", "br", "strong", "b", "em", "i", "ul", "ol", "li", "a", "span", "blockquote"}


def extract_email_address(value: str | None) -> str:
    """Extract the actual email address from a From header value like 'Name <user@example.org>'."""
    if not value:
        return ""

    cleaned = value.strip()
    if not cleaned:
        return ""

    parsed_name, parsed_email = parseaddr(cleaned)
    if parsed_email:
        return parsed_email.strip().lower()
    return cleaned.lower()


def load_allowlist_from_text(text: str) -> set[str]:
    """Load trusted senders from text, ignoring comments and blank lines."""
    if not text:
        return set()

    allowlist = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        allowlist.add(extract_email_address(line))
    return {value for value in allowlist if value}


def load_allowlist(path: str) -> set[str]:
    """Load the allowlist from a plain-text config file."""
    with open(path, "r", encoding="utf-8") as handle:
        return load_allowlist_from_text(handle.read())


def is_valid_image_name(name: str | None) -> bool:
    """Accept valid image extensions regardless of case, but reject non-image file types."""
    if not name:
        return False

    filename = str(name).strip()
    if not filename:
        return False

    suffix = filename.rsplit(".", 1)[-1].upper() if "." in filename else ""
    return suffix in {"PNG", "JPG", "JPEG", "GIF", "WEBP", "BMP", "TIFF"}


def is_allowed_sender(sender: str, allowlist: set[str] | list[str] | None) -> bool:
    """Return True when the sender matches an approved email address."""
    if not sender or not allowlist:
        return False

    normalized_sender = extract_email_address(sender)
    if not normalized_sender:
        return False

    allowed = {extract_email_address(value) for value in allowlist}
    return normalized_sender in allowed


def normalize_title(value: str | None) -> str:
    """Trim and normalize title spacing so leading/trailing spaces do not break matching."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def parse_post_command(about_field: str | None) -> str | None:
    """Parse a new-post instruction from a title/about field like 'post My Post'."""
    if not about_field:
        return None

    matched = re.match(r"(?is)^\s*post\s+(.+?)\s*$", about_field.strip())
    if not matched:
        return None

    title = normalize_title(matched.group(1))
    if not title:
        return None
    return title


def parse_delete_command(about_field: str | None) -> str | None:
    """Parse a delete instruction from a title/about field like 'del My Post'."""
    if not about_field:
        return None

    matched = re.match(r"(?is)^\s*(?:del(?:ete)?|remove)\s+(.+?)\s*$", about_field.strip())
    if not matched:
        return None

    title = normalize_title(matched.group(1))
    if not title:
        return None
    return title


def parse_mail_title_command(about_field: str | None) -> tuple[str, str] | None:
    """Return ('post', title) or ('delete', title) when the about/subject is valid."""
    if not about_field:
        return None

    normalized = about_field.strip()
    if not normalized:
        return None

    post_title = parse_post_command(normalized)
    if post_title:
        return ("post", post_title)

    delete_title = parse_delete_command(normalized)
    if delete_title:
        return ("delete", delete_title)

    return None


def delete_aktuelles_posts_by_title(html_document: str, title: str) -> str:
    """Remove only upload-card articles whose h3 header matches the normalized title exactly."""
    if not html_document or not title:
        return html_document

    plain_title = normalize_title(title)
    if not plain_title:
        return html_document

    article_pattern = re.compile(
        r"(?is)<article\b(?=[^>]*\bclass=(?:\"[^\"]*\bupload-card\b[^\"]*\"|'[^']*\bupload-card\b[^']*'|[^\s>]*\bupload-card\b[^\s>]*))[^>]*>.*?</article>"
    )

    def remove_matching_article(match: re.Match[str]) -> str:
        article_html = match.group(0)
        heading_match = re.search(r"(?is)<h3\b[^>]*>(.*?)</h3>", article_html)
        if not heading_match:
            return article_html

        heading_text = normalize_title(re.sub(r"<[^>]+>", " ", heading_match.group(1)))
        if heading_text == plain_title:
            return ""
        return article_html

    return article_pattern.sub(remove_matching_article, html_document)


def collapse_repeated_text_block(text: str) -> str:
    """Collapse a repeated text block like 'foo foo' or 'foo bar foo bar' down to a single instance."""
    cleaned = sanitize_text(text)
    if not cleaned:
        return ""

    for block_size in range(len(cleaned) // 2, 0, -1):
        block = cleaned[:block_size].strip()
        if not block:
            continue
        pattern = rf"(?:\s*{re.escape(block)}\s*)+"
        if re.fullmatch(pattern, cleaned):
            return block
    return cleaned


def extract_message_parts(raw_message: str | bytes, allowlist: set[str] | list[str] | None) -> dict:
    """Parse a raw MIME email, validate sender, and return extracted text and image bytes."""
    if isinstance(raw_message, str):
        message_bytes = raw_message.encode("utf-8")
    else:
        message_bytes = raw_message

    message = BytesParser(policy=policy.default).parsebytes(message_bytes)
    sender = message.get("From", "")
    if not is_allowed_sender(sender, allowlist):
        raise PermissionError(f"Sender not allowed: {sender}")

    about_value = message.get("Subject") or message.get("About") or ""
    mail_command = parse_mail_title_command(about_value)
    if not mail_command:
        raise ValueError("Invalid about/subject: must start with 'post <title>' or 'del <title>'")

    action, title = mail_command
    if action == "delete":
        return {
            "sender": sender,
            "title": title,
            "delete_title": title,
            "text": "",
            "image_bytes": b"",
            "image_name": "",
            "is_delete_command": True,
        }

    text_chunks: list[str] = []
    seen_text: set[str] = set()
    image_bytes = b""
    image_name = ""

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            filename = part.get_filename() or ""
            if content_type.startswith("text/") and part.get_content_disposition() != "attachment":
                decoded = part.get_content()
                cleaned = collapse_repeated_text_block(str(decoded))
                if not cleaned:
                    continue
                key = cleaned.lower()
                if key in seen_text:
                    continue
                seen_text.add(key)
                text_chunks.append(cleaned)
            elif content_type.startswith("image/") and not image_bytes:
                image_bytes = part.get_payload(decode=True) or b""
                image_name = filename or "mail-upload-image"
    else:
        content_type = message.get_content_type()
        if content_type.startswith("text/"):
            decoded = message.get_content()
            cleaned = collapse_repeated_text_block(str(decoded))
            if cleaned:
                key = cleaned.lower()
                if key not in seen_text:
                    seen_text.add(key)
                    text_chunks.append(cleaned)
        elif content_type.startswith("image/"):
            image_bytes = message.get_payload(decode=True) or b""
            image_name = message.get_filename() or "mail-upload-image"

    text = sanitize_text("\n".join(text_chunks))
    if not text:
        raise ValueError("No text content found in the message.")
    if not image_bytes:
        raise ValueError("No image attachment found in the message.")
    if not is_valid_image_name(image_name):
        raise ValueError(f"Invalid image file extension for upload: {image_name}")

    return {
        "sender": sender,
        "title": title,
        "text": text,
        "image_bytes": image_bytes,
        "image_name": image_name,
        "delete_title": None,
        "is_delete_command": False,
    }


def sanitize_text(text: str) -> str:
    """Remove dangerous HTML and normalize incoming textual content."""
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"<script.*?</script>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</?(?:" + "|".join(ALLOWED_TEXT_TAGS) + r")[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\n+", "\n", cleaned)
    cleaned = re.sub(r"\s+\n\s+", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    parts = [line.strip() for line in cleaned.split("\n") if line.strip()]
    normalized = " ".join(parts)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def paragraphs_to_html(text: str) -> str:
    """Convert text paragraphs into HTML paragraphs."""
    cleaned = sanitize_text(text)
    if not cleaned:
        raise ValueError("Text content is required.")

    paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n|\.\s+", cleaned) if segment.strip()]
    if not paragraphs:
        paragraphs = [cleaned]

    html_parts = []
    for paragraph in paragraphs:
        html_parts.append(f"<p>{html.escape(paragraph, quote=False)}</p>")
    return "\n".join(html_parts)


def build_aktuelles_post(title: str, text: str, image_src: str, alt_text: str, tag: str = "To be posted", date: str | None = None) -> str:
    """Build a fixed news card in the same structure as the current Aktuelles page."""
    if not title or not text or not image_src:
        raise ValueError("Title, text and image source are required.")

    article_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    safe_title = html.escape(title, quote=False)
    safe_alt = html.escape(alt_text or title, quote=False)
    safe_tag = html.escape(tag, quote=False)
    safe_image = html.escape(image_src, quote=False)
    body = paragraphs_to_html(text)

    return (
        '<article class="upload-card">\n'
        '    <div class="upload-media">\n'
        f'        <img src="{safe_image}" alt="{safe_alt}">\n'
        '    </div>\n'
        '    <div class="upload-copy">\n'
        f'        <span class="upload-tag">{safe_tag}</span>\n'
        f'        <h3>{safe_title}</h3>\n'
        f'        <p><strong>{article_date}</strong></p>\n'
        f'{body}\n'
        '    </div>\n'
        '</article>'
    )


def insert_aktuelles_block(html_document: str, block_html: str, insertion_marker: str = "<div class=\"upload-parent-box\">") -> str:
    """Insert a generated post block before the upload box container."""
    if insertion_marker not in html_document:
        raise ValueError("Insertion marker not found in Aktuelles HTML.")
    return html_document.replace(insertion_marker, f"{block_html}\n{insertion_marker}", 1)
