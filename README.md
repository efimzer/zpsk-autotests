# Demo autotests for Webmessenger

Demo project with API and UI autotests.

The repository shows a basic QA automation setup: pytest, API fixtures,
Playwright UI tests, Allure reports, and GitHub Actions.

## Structure

```text
api-tests/   API tests and API client
ui-tests/    UI tests, Playwright fixtures, and UI setup client
scripts/     CI helper scripts
```

## Configuration

Create local environment files from examples:

```bash
cp api-tests/.env.example api-tests/.env
cp ui-tests/.env.example ui-tests/.env
```

## Run Locally

```bash
cd api-tests
./api
```

```bash
cd ui-tests
./ui
```

## GitHub Actions

Workflow file:

```text
.github/workflows/zapaska-tests.yml
```

The workflow supports manual runs and scheduled runs. API and UI suites run as
separate jobs. Reports are generated with Allure and can be published to GitHub
Pages.

Tests and notifications use separate environments:

```text
TEST_BASE_URL              test environment for API/UI checks
ZAPASKA_NOTIFY_BASE_URL    production environment for report notifications
```

API and UI jobs use separate test accounts:

```text
PHONE, CODE, PHONE_PARTICIPANT
UI_PHONE, UI_CODE, UI_PHONE_PARTICIPANT
```

## Reports

Local reports are generated in:

```text
api-tests/allure-report/
ui-tests/allure-report/
```

CI reports are uploaded as GitHub Actions artifacts.
