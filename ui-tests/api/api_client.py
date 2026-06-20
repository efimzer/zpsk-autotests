import requests


class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def post(self, path, **kwargs):
        return self.session.post(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )

    def delete(self, path, **kwargs):
        return self.session.delete(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )

    def login(self, phone, code):
        return self.post(
            "/auth/login",
            json={
                "phone": phone,
                "code": code,
            },
        )

    def create_direct_chat(self, phone_participant):
        return self.post(
            "/chats/direct",
            json={
                "phone": phone_participant,
            },
        )

    def send_message(self, chat_id, text):
        return self.post(
            f"/chats/{chat_id}/messages",
            json={
                "text": text,
            },
        )

    def delete_chat(self, chat_id):
        return self.delete(f"/chats/{chat_id}")
