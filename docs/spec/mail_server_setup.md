# Mail Server Setup for Aktuelles Publishing

This document describes the VPS-based mail processing setup used for the static website. The service accepts mail from a restricted sender allowlist, processes either `post <title>` or `del <title>` commands, updates the Aktuelles page, and removes processed mail from both the queue and the mail server.

## Goals

- Only trusted senders may submit content.
- Mail subjects must begin with either `post ` or `del `.
- Title matching is normalized to avoid whitespace and casing issues.
- `post` mails require both image and text content.
- `del` mails only require the command in the subject; image or text is ignored.
- Matching posts are deleted across all occurrences on the site.
- Processed mail must be removed from the queue and the mail server.

## Allowed senders

The allowlist is stored in a config file on the VPS. Only addresses in this file are accepted.

Example allowlist:

```text
schmidta1@gmx.de
```

Any sender not on the allowlist is rejected without processing.

## Message protocol

### Subject rules

The subject must begin with one of the following prefixes:

- `post `
- `del `

The rest of the subject is variable and treated as the title content. The prefix check is strict: only the beginning matters.

Examples:

- valid: `post Testtitel`
- valid: `del Testtitel`
- valid: `post   Testtitel` (the title is normalized afterwards)
- invalid: `newsletter post Testtitel`
- invalid: `new post Testtitel`
- invalid: `POST Testtitel`

### Title normalization

To avoid trailing or leading whitespace problems, all titles are normalized before comparison or insertion.

Normalization rules:

- strip leading and trailing whitespace
- collapse repeated internal whitespace to a single space
- compare case-insensitive
- trim before matching on both stored titles and incoming commands

This ensures the following all behave as the same title:

- `Testtitel`
- ` Testtitel `
- `Testtitel   123`
- ` testtitel 123 `

## Post command behavior

A mail is treated as a post when the subject begins with `post `.

Requirements:

- sender must be allowed
- subject must begin with `post `
- the title must be present after the prefix
- the mail must include both:
  - a text body
  - an image attachment
- the `about` field must contain `post <title>` exactly in normalized form for the post to be accepted
- otherwise the mail is ignored and deleted without being processed

The `about` field is not used for a content body; it is treated as a command metadata field. If the rule is violated, the mail is rejected and removed.

## Delete command behavior

A mail is treated as a delete when the subject begins with `del `.

Requirements:

- sender must be allowed
- subject must begin with `del `
- the title is extracted from the subject after the `del ` prefix
- the delete command does not require any image or text body
- it can be processed even if the mail body is empty
- the script deletes all posts matching the normalized title

Delete behavior also ignores any content in the `about` field and only matches the title from the subject. The command is processed regardless of missing text or attachment.

## Matching rules for site posts

When deleting posts from the website, all matching entries are removed, not just the first one.

Matching is based on normalized title comparison:

- case-insensitive
- whitespace-normalized
- trimmed before lookup

This means multiple posts with the same title are all removed together.

## Queue and mail cleanup

After a mail is processed successfully:

- the raw mail file is removed from the queue directory
- the corresponding queued message is deleted from the mail server or mailbox queue
- no leftover `.eml` or processed file remains in the storage directory

The cleanup step is required for both post and del operations. This prevents repeated processing and stale mail buildup.

## Live implementation layout

The live setup is a dedicated Ubuntu VPS running the static site and the inbound mail pipeline. The server is primarily responsible for two roles:

1. serving the website through nginx
2. processing inbound mail and writing content into the static site files

The overall layout is:

```text
VPS: Ubuntu Linux

Web root:
  /var/www/tsv_rudow_fv/html

Mail processing root:
  /opt/aktuelles-mail-service/
    config/
      allowlist.txt
    storage/
    logs/

Executable scripts:
  /usr/local/bin/process_aktuelles_mail
  /usr/local/bin/publish_aktuelles_mail
  /usr/local/bin/cleanup_aktuelles_mail_queue
```

The website is served by nginx from the document root:

```text
/var/www/tsv_rudow_fv/html
```

The Aktuelles page is updated in place:

```text
/var/www/tsv_rudow_fv/html/aktuelles.html
```

Images are published under a publicly served directory:

```text
/var/www/tsv_rudow_fv/html/images/
```

### Server configuration notes

- The VPS is a Linux server with direct filesystem access to the site root.
- nginx serves the static site content directly from the HTML directory.
- The mail processing scripts run locally on the same machine and write directly into the public site folders.
- The mail pipeline does not depend on a database; it works by mutating the static HTML file and writing image assets to disk.
- The system is intentionally simple and designed for a single static site, not a full CMS.

### File ownership and permissions

The generated content must be readable by the web server user. The live fix that proved necessary was:

```bash
chmod 0644 /var/www/tsv_rudow_fv/html/images/*
chmod 0644 /var/www/tsv_rudow_fv/html/aktuelles.html
```

This is critical because the image files may exist on disk but still return 404 if the permission bits are too restrictive. The site layout assumes world-readable public assets.

### Service wiring

The mail pipeline is connected to local message intake and queue processing on the VPS. In practical terms:

- inbound mail arrives in a mail-handling queue or raw spool directory
- the processor validates sender, subject, and content rules
- successful actions update the static HTML content
- queue cleanup removes processed `.eml` or raw message files
- the website is refreshed immediately from the same filesystem the webserver reads

This means the system is a lightweight, self-hosted content intake pipeline rather than a full mail server stack. The service logic lives directly on the VPS and writes published HTML into the same directories served by nginx.

### Configuration files

The main configuration is the sender allowlist:

```text
/opt/aktuelles-mail-service/config/allowlist.txt
```

All addresses in this file are accepted. Example:

```text
schmidta1@gmx.de
```

The automation also expects a raw storage directory for pending mail:

```text
/opt/aktuelles-mail-service/storage
```

And a log location such as:

```text
/opt/aktuelles-mail-service/logs
```

These directories are where queued input is staged before being processed or cleaned up.

### Deployment summary

We use an Ubuntu VPS as the host, with nginx serving the static website, and a custom local mail-processing pipeline running directly on that same server to accept, validate, and publish email-driven updates.

In one line: Ubuntu VPS + nginx + custom Python mail intake/queue/cleanup scripts + static HTML/image publishing.

### Why this architecture works well for a static site

This design avoids a database, API, and application server. The website remains static, but the content becomes updateable through a controlled, mailbox-driven publishing mechanism:

- mail arrives from a trusted source
- a strict parser validates the command
- new content is inserted directly into the HTML
- images are stored in the served image directory
- deletes remove matching cards from the static page
- the mail queue is cleaned to avoid reprocessing

This is safe, deterministic, and easy to maintain for a small publishing workflow.

## Image handling

For `post` mails, the content must include an image attachment. The image is saved to the public image directory and the HTML page is updated to include a proper card with that image.

Important operational fix:

- generated image files must be readable by the web server
- file permissions must be set to a public-readable mode such as `0644`

Without this, the image may exist on disk but return a 404 or fail to render in the browser.

## Security rules

The pipeline follows these safeguards:

- no untrusted sender is accepted
- only known command prefixes are processed
- missing image/text in a post mail causes rejection and deletion
- delete mails are tolerated without text or attachment
- all matching titles are removed, not only the first match
- queue contents are cleaned after processing
- all title comparisons are normalized for whitespace and case

## Acceptance criteria

The feature is considered working when all of the following are true:

1. A mail from an allowed sender is accepted.
2. A mail from a non-allowed sender is ignored and deleted.
3. A `post <title>` mail with text and image is added to the page.
4. A `del <title>` mail removes all posts with the same normalized title.
5. A `post` mail without text or without image is rejected.
6. A mail without a valid `post` or `del` prefix is ignored and deleted.
7. All titles are compared with normalized whitespace rules.
8. Processed mail is removed from both the queue and the mail server.
9. The image is publicly readable and rendered on the website.

## Operational notes

This system is intentionally strict. It prioritizes correctness and safety over permissive message handling. The email protocol is designed to keep the static site publication pipeline deterministic, auditable, and safe from unauthorized content.

The implementation is intentionally minimal and focused on the needs of the website: one allowed sender list, two command types, deterministic title matching, guaranteed queue cleanup, and a static-site publishing strategy that runs directly on the Ubuntu VPS.

### Summary of the live deployment model

- Host: Ubuntu VPS
- Web server: nginx
- Website root: /var/www/tsv_rudow_fv/html
- Mail processing root: /opt/aktuelles-mail-service
- Allowed senders: local allowlist file on the VPS
- Content entry: trusted email commands from the allowlist
- Site mutation: direct write to static HTML and public image folder
- Cleanup: remove both raw queue files and processed inbox entries

This provides a lightweight but operationally robust workflow for content publication without introducing a separate CMS or application database.
