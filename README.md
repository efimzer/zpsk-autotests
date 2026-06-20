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
- GitHub Pages report publishing;
- Allure history cache.

GitHub cron uses UTC, so 10:00 MSK is configured as 07:00 UTC.
The workflow starts every day at 07:00 UTC, then a guard step skips every second day.

## Required GitHub Secrets

Add these in repository settings:

```text
BASE_URL
PHONE
CODE
NAME
PHONE_PARTICIPANT
PHONE_PARTICIPANT_2
PHONE_PARTICIPANT_3
GROUP_PARTICIPANTS_PHONES
GROUP_ADD_MEMBER_PHONE
ZAPASKA_NOTIFY_BOT_PHONE
ZAPASKA_NOTIFY_BOT_CODE
ZAPASKA_NOTIFY_RECIPIENT_PHONE
```

`NAME`, `PHONE_PARTICIPANT_2`, `PHONE_PARTICIPANT_3`,
`GROUP_PARTICIPANTS_PHONES`, and `GROUP_ADD_MEMBER_PHONE` are mainly needed
for the API suite.

Notification secrets:

- `ZAPASKA_NOTIFY_BOT_PHONE`: phone of a separate Zapaska bot/test user;
- `ZAPASKA_NOTIFY_BOT_CODE`: login code for that bot/test user;
- `ZAPASKA_NOTIFY_RECIPIENT_PHONE`: phone of the user who receives reports.

The notification job logs in as the bot user, opens a direct chat with the
recipient phone, and sends the GitHub Actions run status with separate API/UI
report links.

## Reports

GitHub Actions uploads:

- `api-allure-report`
- `ui-allure-report`

GitHub Pages publishes:

- `/api/`: API Allure report;
- `/ui/`: UI Allure report.

For UI failures, the report can include screenshots, Playwright traces, and videos.

In repository settings, set GitHub Pages source to `GitHub Actions`.
