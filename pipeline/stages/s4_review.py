"""S4: Review — LLM reviews the generated article for quality."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS, CONTENT_TYPES
from pipeline.context import PipelineContext
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a strict but fair editor for Ender, a Roblox media site for kids (ages 8-14).\n\n"
    "Review the article and check:\n"
    "1. Kid-friendliness: no violence, gambling, inappropriate content, scary stuff\n"
    "2. Accuracy: facts about Roblox should be correct\n"
    "3. Engagement: is it fun and interesting for kids?\n"
    "4. Length: does it match the word count range for the article type?\n"
    "5. Tone: does it match the character's personality?\n"
    "6. Structure: good title, paragraphs, subheadings where needed\n"
    "7. Grammar: correct English\n\n"
    "Return JSON with:\n"
    "- approved: boolean (true if article is good to publish)\n"
    "- feedback: string with specific issues found (empty if approved)\n"
    "- fixes_applied: array of strings listing fixes you would recommend"
)


def run(ctx: PipelineContext) -> None:
    """Review the article. Sets ctx.review_approved and ctx.review_feedback."""
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])
    ct = CONTENT_TYPES.get(ctx.article_type, CONTENT_TYPES["news"])

    prompt = (
        f"Review this {ctx.article_type} article for Ender (Roblox media for kids).\n\n"
        f"Character: {char['name']}\n"
        f"Expected word count: {ct['min_words']}-{ct['max_words']}\n\n"
        f"Title: {ctx.title_en}\n\n"
        f"Article:\n{ctx.article_en}\n\n"
        f"Description: {ctx.description_en}\n\n"
        f"Return JSON with: approved (bool), feedback (string), fixes_applied (array)."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_SYSTEM_PROMPT,
    )

    ctx.review_approved = bool(result.get("approved", False))
    ctx.review_feedback = result.get("feedback", "")

    status = "APPROVED" if ctx.review_approved else "NEEDS REVISION"
    logger.info("Review: %s — %s", status, ctx.review_feedback[:100] if ctx.review_feedback else "no issues")
