# Mail Service Specification

## Goal

This service runs on the VPS and accepts only a very small set of trusted email senders. It processes inbound mail for the static `Aktuelles` page, publishes new posts, deletes matching posts, and clears both the managed queue and the processed mail from the server after success.

The implementation is intentionally strict:

- only allowlisted senders are accepted
- valid commands must start with `post ` or `del `
- no unsupported subject text is processed
- title comparisons normalize whitespace before matching
- all matching delete titles are removed
- processed raw queue entries are deleted after action

---

## Supported senders

The allowlist is maintained in:

- `/opt/aktuelles-mail-service/config/allowlist.txt`

Current allowlisted sender:

- `schmidta1@gmx.de`

The system must reject all other senders before any parse, write, or delete action happens.

---

## Required command syntax

The command is derived from the mail subject, and the same rule also applies to the `About` field when used by the intake layer.

Valid forms:

```text
post <title>
del <title>
```

Rules:

- A message is only accepted when the subject begins with `post ` or `del `.
- The rest of the subject is variable, including additional text after the title.
- The title is parsed after the command prefix and normalized before comparison.
- Any subject that does not begin with one of the supported commands is ignored and deleted without processing.
- A `post` command requires both image and text to be valid.
- A `del` command does not require image or text to be valid; the command itself is enough.

### Whitespace normalization

The processor must normalize the title before matching or storing it.

Normalization includes:

- trimming leading and trailing whitespace
- collapsing repeated internal whitespace to a single space
- comparing titles after normalization only

Examples:

```text
post   Sommernachmittag am Platz
post Sommernachmittag    am Platz
```

must both resolve to the same title for matching purposes.

---

## Post workflow

A valid `post <title>` email is accepted only if:

1. the sender is allowlisted
2. the subject begins with `post `
3. at least one valid image attachment is present
4. there is non-empty text body content

When accepted:

1. the image is saved into the website image folder
2. the file is assigned readable web permissions
3. the post is rendered into the existing `Aktuelles` HTML structure
4. the generated card is inserted before the insertion marker in `html/aktuelles.html`
5. the raw queue file is deleted after successful processing

The HTML article uses the site’s existing card style and includes:

- title in the card heading
- date
- body text
- image reference in the media block

The server must also ensure the image is accessible via the public web path and not blocked by restrictive permissions.

---

## Delete workflow

A valid `del <title>` email is accepted if:

1. the sender is allowlisted
2. the subject begins with `del `
3. the title can be extracted

Delete mails may contain:

- no image
- no text
- no attachment data
- no content requirements beyond the command and title

The delete rule is:

- parse the title after `del `
- normalize title whitespace
- search all article cards whose heading matches the normalized title
- remove every matching post from `html/aktuelles.html`
- ignore the message body content for deletion processing
- after successful deletion, delete the processed raw email and the mail from the queue

This includes cases where multiple posts share the same title; all matching posts are removed.

---

## Message processing rules

### Reject invalid messages

Messages are rejected and not processed when:

- the sender is not allowlisted
- the subject does not start with `post ` or `del `
- a `post` message has no image or no text
- the image is not a valid supported file type
- the title is empty after command parsing
- the message is malformed beyond recovery

Rejected messages are deleted without modifying the site.

### Processed mail cleanup

After any successful action, the system must clean up both the raw queue and the actual mail storage entry.

Repeated text blocks inside a single email are normalized before publishing so a repeated paragraph is only inserted once. This prevents duplicate content in the live `Aktuelles` page when a sender repeats the same text in a single mail body.

This is required for:

- `post` messages
- `del` messages
- malformed messages that were accepted but later rejected during validation

The cleanup rule is:

- remove the raw queued `.eml` copy from the local queue
- remove the processed message from the server-side mailbox or mail spool
- do not leave stale messages behind in storage

---

## Mail structure and parsing expectations

The processor must handle the full MIME structure of a real email, including:

- multipart/form-data messages
- plain-text body parts
- HTML message parts
- inline or attachment images

For publish-type mails (`post`):

- image extraction is mandatory
- text extraction is mandatory
- the image file name is sanitized before storage
- the image is saved under the site image directory

For delete-type mails (`del`):

- image extraction is ignored
- body text is ignored
- only title matching matters

---

## File and directory layout

The live production layout is:

```text
/opt/aktuelles-mail-service/
  config/
    allowlist.txt
  logs/
  storage/
    raw-*.eml

/var/www/tsv_rudow_fv/html/
  aktuelles.html
  images/
```

The live processing scripts write to these paths and clean the raw queue after processing.

---

## Security and safety requirements

The pipeline must be defensive and safe:

- only allowlisted senders are processed
- no user-controlled shell execution from raw content
- no untrusted HTML is rendered directly into the site
- attachment names are sanitized
- files are stored with safe permissions
- the service validates the exact command prefix before acting

---

## Acceptance criteria

The feature is complete when all of the following are true:

- only `schmidta1@gmx.de` and other approved senders can publish
- subject text starting with `post ` creates a new article
- subject text starting with `del ` removes matching posts
- titles are compared with whitespace normalization
- `del` actions remove every matching title, not only the first match
- `post` action requires both image and text
- delete messages without image or text are still valid
- queue files are removed after processing
- processed mail is removed from the mail server or queue after a successful action
- the published image can be served via the public website path

---

## Operational notes

This implementation is intentionally strict to preserve a controlled editorial flow for the static site.

The important behavior is not just parsing mail content; it is enforcing a clear protocol:

- `post <title>` = create a post
- `del <title>` = delete matching posts
- anything else = ignore and delete

That protocol is the core of the current production behavior and is the contract that the mail processor enforces.
