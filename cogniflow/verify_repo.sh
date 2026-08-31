#!/usr/bin/env bash
set -eu

staged_files="$(git diff --cached --name-only --diff-filter=ACMRT || true)"

sensitive_files="$(printf '%s\n' "$staged_files" | grep -E '(^|/)(\.env$|\.env\.(local|development|production)$|.*\.(pem|key|p12|secret|secrets|db|sqlite|sqlite3))$' || true)"
if [ -n "$sensitive_files" ]; then
  printf 'Sensitive files found in the staging area:\n%s\n' "$sensitive_files" >&2
  exit 1
fi

secret_matches="$(git grep --cached -n -E '(sk-[A-Za-z0-9]{20,}|gsk_[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-[0-9A-Za-z-]{10,}|LANGCHAIN_API_KEY[[:space:]]*=[[:space:]]*[^[:space:]#]{20,})' -- . ':!*.lock' || true)"
if [ -n "$secret_matches" ]; then
  printf 'Possible raw API keys found in staged content:\n%s\n' "$secret_matches" >&2
  exit 1
fi

printf 'Repository staging check passed: no sensitive files or recognizable raw API keys found.\n'
