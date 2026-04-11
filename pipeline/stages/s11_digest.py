"""S11: Digest — compile day's articles into evening digest for TG."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline.config import CHARACTERS, SITE_BASE_URL, STATE_DIR
from pipeline.sdk import structured_query
from pipeline.telegram import send_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are EnderFaion, creating an evening digest for your Roblox media channels.\n\n"
    "The digest summarizes all articles published today in a fun, engaging way.\n\n"
    "Format (for each language):\n"
    "- Start with a greeting emoji and bold title like "
    "'<b>Today on Ender</b>' (EN) or '<b>Сьогодні на Ender</b>' (UA)\n"
    "- List each article with an emoji bullet, title as link, and 1-sentence teaser\n"
    "- End with a fun sign-off from EnderFaion\n"
    "- Max 900 characters per digest\n"
    "- HTML formatting: <b>bold</b>, <a href='url'>link</a>\n"
    "- Kid-friendly, excited tone\n\n"
    "Return JSON with:\n"
    "- digest_en: English digest post (HTML)\n"
    "- digest_ua: Ukrainian digest post (HTML)"
)


def run() -> bool:
    """Create and send evening digest to both TG channels.

    Returns True if digest was sent successfully.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Collect today's published articles
    articles = _collect_today_articles(today)
    if not articles:
        logger.info("No articles published today, skipping digest")
        return False

    logger.info("Creating digest for %d articles", len(articles))

    # Build article list for prompt
    articles_text = ""
    for i, art in enumerate(articles, 1):
        articles_text += (
            f"{i}. {art['title_en']} / {art['title_ua']}\n"
            f"   Type: {art.get('article_type', 'news')}\n"
            f"   Author: {art.get('character', 'ender')}\n"
            f"   EN URL: {SITE_BASE_URL}/en/{art['slug']}/\n"
            f"   UA URL: {SITE_BASE_URL}/ua/{art['slug']}/\n"
            f"   Summary: {art.get('summary_en', '')}\n\n"
        )

    prompt = (
        f"Create an evening digest for {today}.\n\n"
        f"Articles published today:\n{articles_text}\n\n"
        f"Site: {SITE_BASE_URL}\n\n"
        f"Return JSON with: digest_en, digest_ua."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_SYSTEM_PROMPT,
    )

    digest_en = result.get("digest_en", "")
    digest_ua = result.get("digest_ua", "")

    if not digest_en and not digest_ua:
        logger.error("Empty digest generated")
        return False

    # Send to channels
    sent = False
    if digest_en:
        msg_id = send_text(text=digest_en, lang="en")
        if msg_id:
            logger.info("Digest sent to EN channel: msg_id=%d", msg_id)
            sent = True

    if digest_ua:
        msg_id = send_text(text=digest_ua, lang="ua")
        if msg_id:
            logger.info("Digest sent to UA channel: msg_id=%d", msg_id)
            sent = True

    # Save digest to state
    if sent:
        _save_digest(today, digest_en, digest_ua, len(articles))

    return sent


def _collect_today_articles(today: str) -> list[dict]:
    """Collect today's articles from summaries.json."""
    summaries_path = STATE_DIR / "summaries.json"
    if not summaries_path.exists():
        return []

    try:
        data = json.loads(summaries_path.read_text())
        return [s for s in data if s.get("date") == today]
    except Exception:
        return []


def _save_digest(today: str, digest_en: str, digest_ua: str, count: int) -> None:
    """Save digest record to state/logs/."""
    logs_dir = STATE_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "date": today,
        "type": "digest",
        "article_count": count,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "digest_en": digest_en,
        "digest_ua": digest_ua,
    }

    path = logs_dir / f"digest-{today}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    logger.info("Digest record saved: %s", path)
