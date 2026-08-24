# WebUp build automation for docs and diagrams

# Requirements (local):
#  - plantuml (and graphviz)
#  - asciidoctor-pdf (Ruby gem)
# Optional via Docker:
#  - docker (uses asciidoctor/docker-asciidoctor and plantuml/plantuml)

SHELL := /bin/bash

DOCS_DIR := docs
DIAGRAMS_SRC_DIR := $(DOCS_DIR)/diagrams
DIAGRAMS_OUT_DIR := $(DOCS_DIR)/images

ADOC_ALL := $(wildcard $(DOCS_DIR)/*.adoc)
# Do not generate a PDF for the docs index page if it's README; build PDFs for the rest
ADOC_SOURCES := $(filter-out $(DOCS_DIR)/README.adoc,$(ADOC_ALL))
PDFS := $(patsubst $(DOCS_DIR)/%.adoc,$(DOCS_DIR)/%.pdf,$(ADOC_SOURCES))

PUML_SOURCES := $(wildcard $(DIAGRAMS_SRC_DIR)/*.puml)
DIAGRAM_PNGS := $(patsubst $(DIAGRAMS_SRC_DIR)/%.puml,$(DIAGRAMS_OUT_DIR)/%.png,$(PUML_SOURCES))

.PHONY: all docs diagrams pdfs clean clean-diagrams clean-pdfs docker-diagrams docker-pdfs
.PHONY: validate-html validate-css validate-all

all: docs

# Build everything (diagrams + PDFs)
docs: diagrams pdfs

# Render PlantUML to PNGs
diagrams: $(DIAGRAM_PNGS)

$(DIAGRAMS_OUT_DIR)/%.png: $(DIAGRAMS_SRC_DIR)/%.puml
	@mkdir -p $(DIAGRAMS_OUT_DIR)
	@echo "[PlantUML] Rendering $< -> $@"
	@cd $(DIAGRAMS_SRC_DIR) && plantuml -tpng -o ../images $(notdir $<)

# Build PDFs for all AsciiDoc files (except docs/README.adoc)
pdfs: $(PDFS)

$(DOCS_DIR)/%.pdf: $(DOCS_DIR)/%.adoc
	@echo "[Asciidoctor PDF] Building $< -> $@"
	@cd $(DOCS_DIR) && asciidoctor-pdf -a toc -a icons=font $(notdir $<)

# Optional: Build diagrams using Docker (no local PlantUML/Graphviz required)
docker-diagrams:
	@mkdir -p $(DIAGRAMS_OUT_DIR)
	@echo "[Docker/PlantUML] Rendering diagrams to $(DIAGRAMS_OUT_DIR)"
	@docker run --rm -v "$$PWD/$(DOCS_DIR):/docs" -w /docs/diagrams plantuml/plantuml:latest \
		plantuml -tpng -o ../images *.puml

# Optional: Build PDFs using Docker Asciidoctor image
docker-pdfs:
	@echo "[Docker/Asciidoctor] Building PDFs in $(DOCS_DIR)"
	@docker run --rm -v "$$PWD:/documents" asciidoctor/docker-asciidoctor \
		asciidoctor-pdf -a toc -a icons=font $(ADOC_SOURCES)

clean: clean-diagrams clean-pdfs

clean-diagrams:
	@echo "[Clean] Removing generated diagram PNGs"
	@rm -f $(DIAGRAMS_OUT_DIR)/*.png

clean-pdfs:
	@echo "[Clean] Removing generated PDFs (keeps committed ones if any)"
	@find $(DOCS_DIR) -maxdepth 1 -name '*.pdf' -print -delete || true

# -------------------------------
# Validation (requires network access)
# HTML validation uses W3C Nu via curl POST; CSS uses Jigsaw API.
# -------------------------------
HTML_PAGES := $(wildcard html/*.html)

validate-html:
	@echo "[Validate HTML] Using W3C Nu HTML Checker (remote)"
	@for f in $(HTML_PAGES); do \
	  echo "-- $$f"; \
	  curl -s -H "Content-Type: text/html; charset=utf-8" --data-binary @"$$f" https://validator.w3.org/nu/?out=gnu | sed 's/^/   /'; \
	done || true

validate-css:
	@echo "[Validate CSS] Using W3C Jigsaw CSS Validator (remote)"; \
	CSS_FILE="html/css/style.css"; \
	curl -sG --data-urlencode "text=$(shell cat html/css/style.css)" --data-urlencode "profile=css3svg" --data-urlencode "output=gnu" https://jigsaw.w3.org/css-validator/validator | sed 's/^/   /'

validate-all: validate-html validate-css
