"""Telegram Bot API helpers — send posts to UA and EN channels."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx

from pipeline.config import SOUND_ON_END, SOUND_ON_START, TG_BOT_TOKEN, TG_CHANNELS

logger = logging.getLogger(__name__)

_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"


def send_photo(
    image_path: Path,
    caption: str,
    lang: str,
    silent: bool | None = None,
) -> int:
    """Send photo with caption to a channel. Returns message_id or 0."""
    channel = TG_CHANNELS.get(lang)
    if not channel or not channel["id"]:
        logger.warning("No channel ID for lang=%s, skipping", lang)
        return 0

    if silent is None:
        silent = _is_silent_hour()

    with open(image_path, "rb") as f:
        resp = httpx.post(
            f"{_API}/sendPhoto",
            data={
                "chat_id": channel["id"],
                "caption": caption,
                "parse_mode": "HTML",
                "disable_notification": str(silent).lower(),
            },
            files={"photo": (image_path.name, f, "image/png")},
            timeout=30,
        )

    if resp.status_code != 200:
        logger.error("sendPhoto failed (%s): %s", lang, resp.text[:200])
        return 0

    msg_id = resp.json().get("result", {}).get("message_id", 0)
    logger.info("Sent photo to @%s: msg_id=%d", channel["username"], msg_id)
    return msg_id


def send_text(
    text: str,
    lang: str,
    silent: bool | None = None,
    url: str = "",
) -> int:
    """Send text message to a channel. Returns message_id or 0."""
    channel = TG_CHANNELS.get(lang)
    if not channel or not channel["id"]:
        logger.warning("No channel ID for lang=%s, skipping", lang)
        return 0

    if silent is None:
        silent = _is_silent_hour()

    payload: dict = {
        "chat_id": channel["id"],
        "text": text,
        "parse_mode": "HTML",
        "disable_notification": silent,
        "disable_web_page_preview": not bool(url),
    }

    if url:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "Read more", "url": url}]]
        }

    resp = httpx.post(f"{_API}/sendMessage", json=payload, timeout=15)
    if resp.status_code != 200:
        logger.error("sendMessage failed (%s): %s", lang, resp.text[:200])
        return 0

    msg_id = resp.json().get("result", {}).get("message_id", 0)
    logger.info("Sent text to @%s: msg_id=%d", channel["username"], msg_id)
    return msg_id


def add_reaction(msg_id: int, lang: str, emoji: str = "\U0001f525") -> None:
    """Add emoji reaction to a message."""
    channel = TG_CHANNELS.get(lang)
    if not channel or not channel["id"]:
        return

    httpx.post(
        f"{_API}/setMessageReaction",
        json={
            "chat_id": channel["id"],
            "message_id": msg_id,
            "reaction": [{"type": "emoji", "emoji": emoji}],
        },
        timeout=10,
    )


def _is_silent_hour() -> bool:
    """Check if current UTC hour is outside sound window."""
    hour = datetime.now(timezone.utc).hour
    return not (SOUND_ON_START <= hour < SOUND_ON_END)
