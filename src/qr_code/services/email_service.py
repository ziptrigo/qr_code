from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class EmailBackend(Protocol):
    """Simple protocol for sending emails."""

    def send_email(
        self,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:  # pragma: no cover - interface
        ...


@dataclass(slots=True)
class SesEmailBackend:
    """Email backend using AWS SES."""

    region: str
    sender: str

    def send_email(
        self,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        if html_body is None:
            html_body = f"<pre>{text_body}</pre>"

        client = boto3.client("ses", region_name=self.region)

        try:
            client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [to]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
            )
        except ClientError as exc:  # pragma: no cover - network error path
            raise RuntimeError(f"Error sending email via SES: {exc}") from exc


@dataclass(slots=True)
class ConsoleEmailBackend:
    """Email backend that logs emails to stdout.

    Useful for development and tests.
    """

    def send_email(
        self,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:  # pragma: no cover - trivial
        print("=== Email ===")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("Text:")
        print(text_body)
        if html_body:
            print("HTML:")
            print(html_body)


def get_email_backend() -> EmailBackend:
    backend = getattr(settings, "EMAIL_BACKEND_KIND", "console").lower()
    if backend == "ses":
        region = getattr(settings, "SES_REGION", "us-east-1")
        sender = getattr(settings, "SES_SENDER", "no-reply@example.com")
        return SesEmailBackend(region=region, sender=sender)
    return ConsoleEmailBackend()
