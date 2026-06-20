# Zapaska autotests

Demo repository for Zapaska API and UI autotests.

## Local run

API:

```bash
cd api-tests
./api
```

UI:

```bash
cd ui-tests
./ui
```

Run without opening the Allure report:

```bash
OPEN_REPORT=false ./ui
OPEN_REPORT=false ./api
```

## GitHub Actions

Workflow: `.github/workflows/zapaska-tests.yml`.

It supports:

- manual run through `workflow_dispatch`;
- scheduled run every other day at 10:00 MSK;
- separate API/UI jobs;
- Allure report artifacts;
- Allure history cache.

## Reports

GitHub Actions uploads:

- `api-allure-report`
- `ui-allure-report`

For UI failures, the report can include screenshots, Playwright traces, and videos.
