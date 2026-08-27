# Contributing

Thanks for contributing to the TSV Rudow Foerderverein website.

## Scope

This repository is a content-first static website. Contributions should preserve:

- semantic HTML
- responsive behavior
- accessibility
- clear German-language content structure

## Workflow

1. Sync your local main branch.
2. Make focused changes.
3. Install local validators with `npm install`.
4. Validate locally with `make validate-content`.
5. Install the repo hooks for this clone with `make hooks-install`.
6. Open a pull request with a concise summary.

## Development Rules

- Keep HTML semantic (`header`, `nav`, `main`, `article`, `footer`).
- Prefer reusable CSS patterns over one-off inline styles.
- Keep navigation and footer consistent across pages.
- Update docs when content structure changes.

## Validation Checklist

- Test desktop, tablet, mobile layouts.
- Run `npm install` once in a fresh clone.
- Install `shellcheck` for shell script validation.
- Run `make validate-content` before committing; it also checks staged whitespace.
- Run `make diagrams` after changing .puml files.
- Run `make pdfs` after changing .adoc docs.
- Run `make validate-all`.
- Verify all main navigation links.
- Confirm no placeholder/legal text regressed.
- Confirm `robots.txt` and `sitemap.xml` still match page strategy.

## Content Updates

For Foerderverein content migration/editing:

- update source notes in `docs/content/foerderverein/`
- then apply the approved copy to `html/*.html`

## Commit Message Style

Use clear, action-oriented messages, for example:

- `docs: align README with foerderverein architecture`
- `html: fix impressum structure and legal placeholders`
- `css: improve accessibility and reduced-motion behavior`

## Release Baseline

Current baseline release: 0.1.2
