import json
import os
import sys
from http.cookiejar import CookieJar
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener


def required_env(name):
    value = os.getenv(name)
    if not value:
        missing.append(name)
    return value


def request_json(opener, method, base_url, path, body=None):
    data = None
    headers = {"Content-Type": "application/json"}

    if body is not None:
        data = json.dumps(body).encode("utf-8")

    request = Request(
        urljoin(base_url, path),
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with opener.open(request, timeout=15) as response:
            response_body = response.read().decode("utf-8")
            if not response_body:
                return {}
            return json.loads(response_body)
    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {error.code} for {method} {path}: {response_body}"
        ) from error
    except URLError as error:
        raise RuntimeError(f"Request failed for {method} {path}: {error}") from error


def build_message():
    repository = os.getenv("GITHUB_REPOSITORY", "unknown repository")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repository}/actions/runs/{run_id}" if run_id else ""

    api_result = os.getenv("API_RESULT", "unknown")
    ui_result = os.getenv("UI_RESULT", "unknown")
    overall = (
        "success"
        if api_result in {"success", "skipped"}
        and ui_result
        in {
            "success",
            "skipped",
        }
        else "failed"
    )

    lines = [
        "Zapaska autotests",
        f"Status: {overall}",
        f"API: {api_result}",
        f"UI: {ui_result}",
        f"Pages: {os.getenv('PAGES_RESULT', 'unknown')}",
        f"Suite: {os.getenv('SUITE', 'all')}",
        f"Browser: {os.getenv('BROWSER', 'chromium')}",
        f"Event: {os.getenv('GITHUB_EVENT_NAME', 'unknown')}",
        f"Branch: {os.getenv('GITHUB_REF_NAME', 'unknown')}",
    ]

    api_report_url = os.getenv("API_REPORT_URL")
    ui_report_url = os.getenv("UI_REPORT_URL")

    if api_report_url:
        lines.append(f"API report: {api_report_url}")

    if ui_report_url:
        lines.append(f"UI report: {ui_report_url}")

    if run_url:
        lines.append(f"Run: {run_url}")

    return "\n".join(lines)


missing = []


def main():
    base_url = required_env("ZAPASKA_NOTIFY_BASE_URL")
    bot_phone = required_env("ZAPASKA_NOTIFY_BOT_PHONE")
    bot_code = required_env("ZAPASKA_NOTIFY_BOT_CODE")
    recipient_phone = required_env("ZAPASKA_NOTIFY_RECIPIENT_PHONE")

    if missing:
        print(f"Zapaska notification skipped. Missing env: {', '.join(missing)}")
        return 0

    base_url = base_url.rstrip("/") + "/"
    opener = build_opener(HTTPCookieProcessor(CookieJar()))

    request_json(
        opener,
        "POST",
        base_url,
        "auth/login",
        {"phone": bot_phone, "code": bot_code},
    )
    chat = request_json(
        opener,
        "POST",
        base_url,
        "chats/direct",
        {"phone": recipient_phone},
    )

    chat_id = chat.get("id")
    if not chat_id:
        raise RuntimeError(f"Direct chat response has no id: {chat}")

    request_json(
        opener,
        "POST",
        base_url,
        f"chats/{chat_id}/messages",
        {"text": build_message()},
    )

    print("Zapaska notification sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
