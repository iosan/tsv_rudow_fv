#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source_dir="$repo_root/html"
output_dir="${HOME}/share"
archive_name="tsv_rudow_fv_demo_site.zip"

usage() {
    cat <<'EOF'
Usage: scripts/export_website_demo.sh [options]

Create a demo zip that contains only website runtime content.

Options:
  -o, --output-dir DIR   Output directory for the zip (default: ~/share)
  -n, --name NAME.zip    Archive name (default: tsv_rudow_fv_demo_site.zip)
  -s, --source DIR       Source directory to package (default: <repo>/html)
  -h, --help             Show this help

Examples:
  scripts/export_website_demo.sh
  scripts/export_website_demo.sh --name website_demo_2026-09-02.zip
  scripts/export_website_demo.sh --output-dir /tmp
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output-dir)
            output_dir="$2"
            shift 2
            ;;
        -n|--name)
            archive_name="$2"
            shift 2
            ;;
        -s|--source)
            source_dir="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ ! -d "$source_dir" ]]; then
    echo "Source directory does not exist: $source_dir"
    exit 1
fi

if [[ "$archive_name" != *.zip ]]; then
    archive_name="${archive_name}.zip"
fi

mkdir -p "$output_dir"
archive_path="${output_dir%/}/$archive_name"

rm -f "$archive_path"

# Include only website runtime content by archiving the chosen source directory.
(
    cd "$repo_root"
    zip -r "$archive_path" "${source_dir#"$repo_root"/}"
)

if [[ ! -f "$archive_path" ]]; then
    echo "Failed to create archive: $archive_path"
    exit 1
fi

size=$(du -h "$archive_path" | awk '{print $1}')
echo "Created: $archive_path"
echo "Size: $size"
