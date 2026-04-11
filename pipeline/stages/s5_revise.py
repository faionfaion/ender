"""S5: Revise — apply review feedback to improve the article."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS
from pipeline.context import PipelineContext
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)


def _build_system_prompt(ctx: PipelineContext) -> str:
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])

    return (
        f"You are {char['name']}, revising an article for Ender — "
        f"a Roblox media site for kids.\n\n"
        f"Character: {char['description']}\n\n"
        f"Revision rules:\n"
        f"- Apply all feedback from the reviewer\n"
        f"- Keep the same tone and character voice\n"
        f"- Keep it kid-friendly, fun, and engaging\n"
        f"- Fix any grammar or factual issues\n"
        f"- Maintain the same general structure\n"
        f"- No violence, gambling, or inappropriate content\n\n"
        f"Return valid JSON with:\n"
        f"- article_en: the revised full article text in markdown\n"
        f"- title_en: revised title (or same if no change needed)\n"
        f"- description_en: revised description (or same if no change needed)\n"
        f"- image_prompt: revised image prompt (or same if no change needed)"
    )


def run(ctx: PipelineContext) -> None:
    """Revise article based on review feedback."""
    prompt = (
        f"Revise this article based on reviewer feedback.\n\n"
        f"Current title: {ctx.title_en}\n\n"
        f"Current article:\n{ctx.article_en}\n\n"
        f"Current description: {ctx.description_en}\n\n"
        f"Reviewer feedback:\n{ctx.review_feedback}\n\n"
        f"Return JSON with: article_en, title_en, description_en, image_prompt."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_build_system_prompt(ctx),
    )

    ctx.article_en = result.get("article_en", ctx.article_en)
    ctx.title_en = result.get("title_en", ctx.title_en)
    ctx.description_en = result.get("description_en", ctx.description_en)
    ctx.image_prompt = result.get("image_prompt", ctx.image_prompt)

    # Reset review state for next cycle
    ctx.review_approved = False
    ctx.review_feedback = ""

    logger.info("Article revised: '%s' (%d chars)", ctx.title_en, len(ctx.article_en))
