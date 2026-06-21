import os
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_PATH)

BASE_URL = os.getenv("BASE_URL", "https://stage.zapaska.online")
PHONE = os.getenv("PHONE")
CODE = os.getenv("CODE")
UI_PHONE_PARTICIPANT = os.getenv("UI_PHONE_PARTICIPANT")

if not PHONE:
    raise ValueError("Не задана переменная окружения PHONE")

if not CODE:
    raise ValueError("Не задана переменная окружения CODE")

if not UI_PHONE_PARTICIPANT:
    raise ValueError("Не задана переменная окружения UI_PHONE_PARTICIPANT")
