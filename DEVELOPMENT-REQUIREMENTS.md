# Development Requirements

This repository uses a mixed toolchain. The items below cover the full local development setup.

## Core tools

- `git`
- `bash`
- `make`
- `node`
- `npm`
- `python3`
- `shellcheck`

## Frontend validation and linting

Installed through `npm install` from [package.json](package.json):

- `eslint`
- `html-validate`
- `stylelint`
- `stylelint-config-standard`

## Python tooling

The current Python scripts only use the standard library, so there are no third-party Python packages to install yet.

Validation still uses:

- `python3 -m py_compile`

If Python dependencies are added later, capture them in a dedicated `requirements.txt` file.

## Documentation and diagram tooling

Needed for docs generation via the Makefile:

- `plantuml`
- `graphviz`
- `asciidoctor-pdf`

Optional container-based alternatives are documented in the `Makefile`.

## Install sequence

1. Install system tools: `git`, `make`, `bash`, `node`, `npm`, `python3`, `shellcheck`.
2. Run `npm install` to fetch the frontend validators.
3. Install docs tooling if you work on `docs/`: `plantuml`, `graphviz`, `asciidoctor-pdf`.
4. Enable the repository hooks with `make hooks-install`.
