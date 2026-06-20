from pathlib import Path

import requests


class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path, **kwargs):
        return self.session.get(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs
        )

    def post(self, path, **kwargs):
        return self.session.post(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs
        )

    def patch(self, path, **kwargs):
        return self.session.patch(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs
        )

    def delete(self, path, **kwargs):
        return self.session.delete(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs
        )

    def login(self, phone, code):
        return self.post("/auth/login", json={"phone": phone, "code": code})

    def get_auth_me(self):
        return self.get("/auth/me")

    def get_chats(self):
        return self.get("/chats")

    def get_messages(self, chat_id, limit=1):
        return self.get(f"/chats/{chat_id}/messages", params={"limit": limit})

    def create_direct_chat(self, phone_participant):
        return self.post("/chats/direct", json={"phone": phone_participant})

    def create_group_chat(self, title, phone_participants=None):
        body = {"title": title}

        if phone_participants is not None:
            body["participantsPhones"] = phone_participants

        return self.post("/chats/group", json=body)

    def delete_chat(self, chat_id):
        return self.delete(f"/chats/{chat_id}")

    def send_message(self, chat_id, text=None, attachments=None):
        body = {}

        if text is not None:
            body["text"] = text

        if attachments is not None:
            body["attachments"] = attachments

        return self.post(f"/chats/{chat_id}/messages", json=body)

    def delete_message(self, message_id):
        return self.delete(f"/messages/{message_id}")

    def get_user_profile(self):
        return self.get("/users/me")

    def get_whitelist(self):
        return self.get("/auth/admin/whitelist")

    def get_contacts(self):
        return self.get("/contacts")

    def update_chat_title(self, chat_id, title):
        return self.patch(f"/chats/{chat_id}", json={"title": title})

    def add_chat_member(self, chat_id, phone_participant):
        return self.post(f"/chats/{chat_id}/members", json={"phone": phone_participant})

    def delete_chat_member(self, chat_id, user_id):
        return self.delete(f"/chats/{chat_id}/members/{user_id}")

    def upload_file(self, file_path, mime_type="application/octet-stream"):
        path = Path(file_path)

        with path.open("rb") as file:
            return self.post(
                "/files/upload", files={"file": (path.name, file, mime_type)}
            )
