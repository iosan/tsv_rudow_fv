# Changelog

All notable changes to this project are documented here.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [0.1.3] - 2026-09-02

### Added
- Reusable `scripts/export_website_demo.sh` helper to package website runtime content from `html/` into a demo ZIP (default target: `~/share`).

### Improved
- Export workflow now supports custom output directory, archive name, and source path through CLI options.

## [0.1.2] - 2026-08-27

### Added
- Repo-local validation workflow for HTML, CSS, JS, Python, and shell scripts with staged whitespace checks.
- Repo-managed Git hooks and a consolidated development requirements document for the full toolchain.
- Responsive mobile navigation with a hamburger dropdown that closes on selection.

### Fixed
- Restored the top navigation on tablet and desktop layouts.
- Updated the migrated philosophy and satzung pages with the source content from the legacy Foerderverein materials.

### Improved
- Aligned repository documentation with the local validation and development setup.

## [0.1.1] - 2026-08-24

### Added
- Automated league data feed integration for TSV Rudow I, II and III with generated JSON/JS artifacts.

### Fixed
- Corrected width calculation so full-row cards match the exact available parent width.
- Fixed inconsistent glow rendering by anchoring card pseudo-elements to their own card containers.

### Improved
- Refined responsive card reflow behavior across Startseite and Aktuelles.
- Harmonized parent/child glow hierarchy and introduced subtler green-red accent gradients.
- Extended full-width content-box behavior to additional watermark subpages.

## [0.1.0] - 2026-08-24

### Added
- New static website project for TSV Rudow Foerderverein.
- Five-topic information architecture: Philosophie, Satzung, Ansprechpartner, Beitrittsformular, Aktuelles.
- Modern responsive layout with accessibility-first navigation and content cards.
- Structured content migration notes in docs/content/foerderverein.
- Project documentation set in AsciiDoc and generated PDF artifacts.
- PlantUML-based architecture diagram sources and rendered images.

### Fixed
- Repaired legal page structure and normalized metadata/indexing controls.
- Removed stale legacy template naming from active project pages and screenshot assets.

### Improved
- Added reduced-motion handling and stronger keyboard focus visibility in CSS.
- Unified repository documentation to current project scope and release model.
