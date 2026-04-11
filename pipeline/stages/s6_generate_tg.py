"""S6: Generate TG posts — create Telegram posts for both languages."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS, HASHTAGS_EN, HASHTAGS_UA, SITE_BASE_URL
from pipeline.context import PipelineContext
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)


def _build_system_prompt(ctx: PipelineContext) -> str:
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])

    return (
        f"You are {char['name']}, creating Telegram channel posts for Ender — "
        f"a bilingual (EN+UA) Roblox media for kids.\n\n"
        f"Character: {char['description']}\n"
        f"Character emoji: {char['emoji']}\n\n"
        f"TG post format (both languages):\n"
        f"- Start with an emoji hook (related to the topic)\n"
        f"- Bold first line as a catchy hook\n"
        f"- 2-3 short sentences that make you want to read the full article\n"
        f"- 'Read more' link at the end (will be added separately)\n"
        f"- Hashtags at the very end\n\n"
        f"Rules:\n"
        f"- Max 900 characters per post\n"
        f"- HTML formatting: <b>bold</b>, <i>italic</i>\n"
        f"- Kid-friendly, fun, exciting tone\n"
        f"- Ukrainian post should sound natural in Ukrainian, not a literal translation\n"
        f"- No violence, gambling, or inappropriate content\n\n"
        f"Return JSON with:\n"
        f"- tg_post_en: English TG post (HTML)\n"
        f"- tg_post_ua: Ukrainian TG post (HTML)"
    )


def run(ctx: PipelineContext) -> None:
    """Generate TG posts for EN and UA channels."""
    hashtags_en = HASHTAGS_EN.get(ctx.topic, "#Roblox")
    hashtags_ua = HASHTAGS_UA.get(ctx.topic, "#Роблокс")
    article_url = f"{SITE_BASE_URL}/{ctx.slug}/"

    prompt = (
        f"Create Telegram posts for this article in both EN and UA.\n\n"
        f"Title (EN): {ctx.title_en}\n"
        f"Description: {ctx.description_en}\n"
        f"Article summary: {ctx.summary_en}\n"
        f"Article URL: {article_url}\n\n"
        f"Key points from the article:\n{ctx.article_en[:500]}...\n\n"
        f"Hashtags EN: {hashtags_en}\n"
        f"Hashtags UA: {hashtags_ua}\n\n"
        f"Return JSON with: tg_post_en, tg_post_ua."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_build_system_prompt(ctx),
    )

    ctx.tg_post_en = result.get("tg_post_en", "")
    ctx.tg_post_ua = result.get("tg_post_ua", "")

    logger.info(
        "TG posts generated: EN=%d chars, UA=%d chars",
        len(ctx.tg_post_en),
        len(ctx.tg_post_ua),
    )
