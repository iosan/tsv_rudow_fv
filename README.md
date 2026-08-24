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

## Live League Data (TSV Rudow I/II/III)

The homepage can load generated league metadata from:

- `html/data/league-data.json`

Generate/update this file with:

```bash
make league-data
```

or directly:

```bash
python3 scripts/fetch_league_data.py
```

What is included:

- standings rows for TSV Rudow I, II, III
- latest and next match metadata (date, opponent, link)

Note:

- Public score digits on fussball.de are obfuscated in HTML. The generated feed keeps reliable metadata and deep links to official match pages.

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
