"""Minimal mail helper to replace Flask-Mail dependency."""

from typing import List, Optional


class Message:
    def __init__(self, subject: str = "", recipients: Optional[List[str]] = None, html: str = ""):
        self.subject = subject
        self.recipients = recipients or []
        self.html = html
        self.body = ""
        self.attachments = []

    def attach(self, filename: str, content_type: str, data: bytes) -> None:
        self.attachments.append({
            "filename": filename,
            "content_type": content_type,
            "data": data,
        })


class Mail:
    def init_app(self, app) -> None:
        self.app = app

    def send(self, msg: Message) -> None:
        if not hasattr(self, "app"):
            print("[Mail] Mail not configured. Skipping send.")
            return
        print(f"[Mail] Skipping email send: subject={msg.subject}, recipients={msg.recipients}, attachments={len(msg.attachments)}")
