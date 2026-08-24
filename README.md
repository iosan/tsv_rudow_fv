# TSV Rudow Foerderverein Website

Modern static website for the TSV Rudow Foerderverein, centered on five main content areas:

- Philosophie
- Satzung
- Ansprechpartner
- Beitrittsformular
- Aktuelles

The project is intentionally lightweight (plain HTML + CSS), content-focused, accessible, and easy to deploy on any static host.

## Project Goals

- Clear information architecture with topic-first navigation
- Editorial, modern visual language
- Accessible and responsive UI on desktop/tablet/mobile
- Clean content migration path from the legacy Foerderverein pages
- Simple maintenance without framework lock-in

## Tech Stack

- HTML5 (semantic structure)
- CSS3 (design tokens, responsive layout, motion/accessibility guards)
- AsciiDoc + PlantUML for technical documentation
- Makefile automation for docs and validation tasks

## Directory Layout

```text
tsv_rudow_fv/
|-- html/
|   |-- index.html
|   |-- philosophie.html
|   |-- satzung.html
|   |-- ansprechpartner.html
|   |-- beitrittsformular.html
|   |-- aktuelles.html
|   |-- impressum.html
|   |-- about.html
|   |-- contact.html
|   |-- transparenz.html
|   |-- mitmachen.html
|   |-- robots.txt
|   |-- sitemap.xml
|   |-- humans.txt
|   |-- css/style.css
|   `-- images/
|-- docs/
|   |-- index.adoc
|   |-- README.adoc
|   |-- BUILD.adoc
|   |-- content/foerderverein/
|   `-- diagrams/
|-- Makefile
|-- CHANGELOG.md
`-- CONTRIBUTING.md
```

## Local Development

Open directly:

```bash
xdg-open html/index.html
```

Or run a local server:

```bash
cd html
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Quality Workflow

```bash
# Build docs/diagrams
make docs

# Validate HTML and CSS via W3C services
make validate-all
```

## Content Governance

Canonical migrated source content is stored in:

- `docs/content/foerderverein/`

Use this folder for editorial updates before applying changes to HTML pages.

## Deployment

Deploy the `html/` directory to any static host:

- GitHub Pages
- Netlify
- Vercel
- traditional web server

## License

MIT License. See `LICENSE`.
