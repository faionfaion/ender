"""S7: Translate — translate EN article to Ukrainian."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS, HASHTAGS_UA
from pipeline.context import PipelineContext
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)


def _build_system_prompt(ctx: PipelineContext) -> str:
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])

    return (
        f"You are a professional EN-to-UA translator for Ender, "
        f"a Roblox media site for kids.\n\n"
        f"Character voice: {char['name']} — {char['description']}\n\n"
        f"Translation rules:\n"
        f"- Translate from English to Ukrainian\n"
        f"- Keep the same fun, engaging tone\n"
        f"- Keep gaming terms that are commonly used in Ukrainian gaming community "
        f"(e.g. 'Roblox', 'obby', 'Robux' stay as-is)\n"
        f"- Adapt jokes and expressions to sound natural in Ukrainian\n"
        f"- Keep the same paragraph structure\n"
        f"- Keep all subheadings\n"
        f"- Kid-friendly language\n"
        f"- No literal word-for-word translation — it should read like "
        f"it was originally written in Ukrainian\n\n"
        f"Return valid JSON with:\n"
        f"- article_ua: full article text in Ukrainian (markdown)\n"
        f"- title_ua: Ukrainian title\n"
        f"- description_ua: Ukrainian meta description (max 160 chars)"
    )


def run(ctx: PipelineContext) -> None:
    """Translate EN article to Ukrainian."""
    hashtags_ua = HASHTAGS_UA.get(ctx.topic, "#Роблокс")

    prompt = (
        f"Translate this article from English to Ukrainian.\n\n"
        f"Title: {ctx.title_en}\n\n"
        f"Article:\n{ctx.article_en}\n\n"
        f"Description: {ctx.description_en}\n\n"
        f"Return JSON with: article_ua, title_ua, description_ua."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_build_system_prompt(ctx),
    )

    ctx.article_ua = result.get("article_ua", "")
    ctx.title_ua = result.get("title_ua", "")
    ctx.description_ua = result.get("description_ua", "")
    ctx.hashtags_ua = hashtags_ua

    logger.info(
        "Translation complete: '%s' (%d chars UA)",
        ctx.title_ua,
        len(ctx.article_ua),
    )
