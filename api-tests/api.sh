#!/usr/bin/env bash

set -u

RESULTS_DIR="${RESULTS_DIR:-allure-results}"
REPORT_DIR="${REPORT_DIR:-allure-report}"
CONFIG_FILE="${CONFIG_FILE:-allurerc.mjs}"
TEST_PATH="${TEST_PATH:-tests}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTEST_ARGS="${PYTEST_ARGS:-}"
OPEN_REPORT="${OPEN_REPORT:-true}"

write_environment() {
  local base_url
  base_url="$(awk -F= '$1 == "BASE_URL" {print substr($0, index($0, "=") + 1)}' .env 2>/dev/null | tail -n 1)"
  base_url="${base_url:-not_set}"

  {
    printf 'Project=Zapaska\n'
    printf 'Suite=API Tests\n'
    printf 'Base_URL=%s\n' "$base_url"
    printf 'Python=%s\n' "$("$PYTHON_BIN" --version 2>&1)"
    printf 'Pytest=%s\n' "$("$PYTHON_BIN" -m pytest --version 2>/dev/null | head -n 1)"
    printf 'Allure=%s\n' "$(npx allure --version 2>/dev/null)"
    printf 'OS=%s\n' "$(uname -srm)"
    printf 'Run_Date_UTC=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  } > "$RESULTS_DIR/environment.properties"
}

rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"
mkdir -p .allure
write_environment

if [ "$(uname -s)" = "Darwin" ] && command -v arch >/dev/null 2>&1; then
  # shellcheck disable=SC2086
  arch -arm64 "$PYTHON_BIN" -m pytest "$TEST_PATH" $PYTEST_ARGS "$@" --alluredir="$RESULTS_DIR"
else
  # shellcheck disable=SC2086
  "$PYTHON_BIN" -m pytest "$TEST_PATH" $PYTEST_ARGS "$@" --alluredir="$RESULTS_DIR"
fi
PYTEST_EXIT=$?

rm -rf "$REPORT_DIR"
npx allure generate "$RESULTS_DIR" --config "$CONFIG_FILE" -o "$REPORT_DIR"
ALLURE_EXIT=$?

if [ "$ALLURE_EXIT" -ne 0 ]; then
  exit "$ALLURE_EXIT"
fi

if [ "$OPEN_REPORT" = "true" ]; then
  npx allure open "$REPORT_DIR"
fi

exit "$PYTEST_EXIT"
