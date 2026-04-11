"""S2: Research — agent_query with WebSearch to research the topic."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS
from pipeline.context import PipelineContext
from pipeline.sdk import agent_query

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a research assistant for Ender, a kid-friendly Roblox media site. "
    "Research the given topic thoroughly using web search.\n\n"
    "Rules:\n"
    "- Focus on Roblox-related information only\n"
    "- Find recent news, updates, tips, or facts about the topic\n"
    "- Include specific details: game names, update versions, dates, numbers\n"
    "- All content must be kid-friendly — no violence, gambling, inappropriate content\n"
    "- Provide source URLs when possible\n"
    "- Write a concise research summary (300-500 words)\n"
    "- Focus on what would be interesting for kids aged 8-14"
)


def run(ctx: PipelineContext) -> None:
    """Research the topic and store findings in ctx.research_text."""
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])

    prompt = (
        f"Research this Roblox topic for a {ctx.article_type} article:\n\n"
        f"Topic: {ctx.topic_label}\n"
        f"Category: {ctx.topic}\n"
        f"Article type: {ctx.article_type}\n"
        f"Author character: {char['name']} — {char['description']}\n\n"
        f"Search for the latest information about this topic. "
        f"Find specific facts, numbers, game names, and details that would make "
        f"the article informative and engaging for kids.\n\n"
        f"Write a research summary with key findings and source URLs."
    )

    result = agent_query(
        prompt=prompt,
        system_prompt=_SYSTEM_PROMPT,
        allowed_tools=["WebSearch", "WebFetch"],
    )

    ctx.research_text = result
    logger.info(
        "Research complete for '%s' (%d chars)",
        ctx.topic_label,
        len(result),
    )
