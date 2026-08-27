#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

html_validate="$repo_root/node_modules/.bin/html-validate"
stylelint="$repo_root/node_modules/.bin/stylelint"
eslint="$repo_root/node_modules/.bin/eslint"
shellcheck="$(command -v shellcheck || true)"

for tool in "$html_validate" "$stylelint" "$eslint"; do
    if [[ ! -x "$tool" ]]; then
        echo "Missing local validator: $tool"
        echo "Run 'npm install' in the repository root first."
        exit 1
    fi
done

if [[ -z "$shellcheck" ]]; then
    echo "Missing local validator: shellcheck"
    echo "Install shellcheck before running validation."
    exit 1
fi

validate_html() {
    echo "[HTML] html/*.html"
    "$html_validate" html/*.html
}

validate_whitespace() {
    echo "[DIFF] staged whitespace"
    git diff --check --cached -- .
}

validate_css() {
    echo "[CSS] html/css/style.css"
    "$stylelint" html/css/style.css
}

validate_js() {
    echo "[JS] html/js/*.js html/data/*.js"
    "$eslint" html/js/*.js html/data/*.js
}

validate_shell() {
    local file
    while IFS= read -r -d '' file; do
        echo "[SH] $file"
        "$shellcheck" "$file"
    done < <(find .githooks scripts -maxdepth 1 -type f -name '*.sh' -print0 | sort -z)
}

validate_python() {
    local file
    while IFS= read -r file; do
        echo "[PY] $file"
        python3 -m py_compile "$file"
    done < <(git ls-files '*.py')
}

validate_whitespace
validate_html
validate_css
validate_js
validate_shell
validate_python

echo "Validation passed."
