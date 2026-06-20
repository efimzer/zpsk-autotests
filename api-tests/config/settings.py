import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_PATH)

BASE_URL = os.getenv("BASE_URL")
PHONE = os.getenv("PHONE")
CODE = os.getenv("CODE")
NAME = os.getenv("NAME")
PHONE_PARTICIPANT = os.getenv("PHONE_PARTICIPANT")
PHONE_PARTICIPANT_2 = os.getenv("PHONE_PARTICIPANT_2")
PHONE_PARTICIPANT_3 = os.getenv("PHONE_PARTICIPANT_3")
GROUP_PARTICIPANTS_PHONES = os.getenv("GROUP_PARTICIPANTS_PHONES", "")
GROUP_PARTICIPANTS_PHONES = [
    phone.strip()
    for phone in GROUP_PARTICIPANTS_PHONES.split(",")
    if phone.strip()
    ]
GROUP_ADD_MEMBER_PHONE = os.getenv("GROUP_ADD_MEMBER_PHONE") or PHONE_PARTICIPANT_3 or PHONE_PARTICIPANT_2
GROUP_INITIAL_PARTICIPANTS_PHONES = [
    phone
    for phone in GROUP_PARTICIPANTS_PHONES
    if phone != GROUP_ADD_MEMBER_PHONE
]
GROUP_CHAT_TITLE = os.getenv("GROUP_CHAT_TITLE", "Групповой чат")
UPDATE_CHAT_TITLE = os.getenv("UPDATE_CHAT_TITLE", "Новое имя чата")

if not PHONE:
    raise ValueError("Не задан телефон автора")

if not PHONE_PARTICIPANT:
    raise ValueError("Не задан телефон собеседника")

if not CODE:
    raise ValueError("Не задан код-пароль")

if not NAME:
    raise ValueError("Не задано имя автора")

if not BASE_URL:
    raise ValueError("Не задан BASE_URL")

if GROUP_PARTICIPANTS_PHONES and not GROUP_ADD_MEMBER_PHONE:
    raise ValueError("Не задан телефон участника для добавления в групповой чат")

if GROUP_PARTICIPANTS_PHONES and not GROUP_INITIAL_PARTICIPANTS_PHONES:
    raise ValueError("Не задан список начальных участников группового чата")
