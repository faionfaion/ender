"""S3: Generate — create EN article from research."""

from __future__ import annotations

import logging

from pipeline.config import CHARACTERS, CONTENT_TYPES, HASHTAGS_EN
from pipeline.context import PipelineContext
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)


def _build_system_prompt(ctx: PipelineContext) -> str:
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])
    ct = CONTENT_TYPES.get(ctx.article_type, CONTENT_TYPES["news"])

    return (
        f"You are {char['name']}, writing for Ender — a Roblox media site for kids.\n\n"
        f"Character: {char['description']}\n\n"
        f"Writing rules:\n"
        f"- Write in English\n"
        f"- Article type: {ctx.article_type} ({ct['min_words']}-{ct['max_words']} words)\n"
        f"- Tone: fun, engaging, kid-friendly (ages 8-14)\n"
        f"- Use gaming slang naturally but keep it understandable\n"
        f"- Include specific details, numbers, game names\n"
        f"- Break into short paragraphs (2-3 sentences each)\n"
        f"- Use subheadings for longer articles\n"
        f"- No violence, gambling, or inappropriate content\n"
        f"- No markdown links in article body — plain text only\n"
        f"- The article should feel like a friend telling you something cool\n\n"
        f"Return valid JSON with these fields:\n"
        f"- title_en: catchy title (max 80 chars)\n"
        f"- slug: URL slug (lowercase, hyphens, max 60 chars)\n"
        f"- article_en: full article text in markdown\n"
        f"- description_en: meta description (max 160 chars)\n"
        f"- tags: array of 3-5 tags (lowercase)\n"
        f"- hashtags: hashtag string for social media\n"
        f"- source_urls: array of source URLs used\n"
        f"- image_prompt: scene description for image generation "
        f"(describe what {char['name']} is doing in the scene, 1-2 sentences)\n"
        f"- summary_en: 1-2 sentence summary for internal tracking"
    )


def run(ctx: PipelineContext) -> None:
    """Generate EN article and populate ctx fields."""
    hashtags = HASHTAGS_EN.get(ctx.topic, "#Roblox")

    prompt = (
        f"Write a {ctx.article_type} article about: {ctx.topic_label}\n\n"
        f"Research findings:\n{ctx.research_text}\n\n"
        f"Suggested hashtags: {hashtags}\n\n"
        f"Return JSON with: title_en, slug, article_en, description_en, "
        f"tags, hashtags, source_urls, image_prompt, summary_en."
    )

    result = structured_query(
        prompt=prompt,
        system_prompt=_build_system_prompt(ctx),
    )

    ctx.title_en = result.get("title_en", "")
    ctx.slug = result.get("slug", "")
    ctx.article_en = result.get("article_en", "")
    ctx.description_en = result.get("description_en", "")
    ctx.tags = result.get("tags", [])
    ctx.hashtags_en = result.get("hashtags", hashtags)
    ctx.source_urls = result.get("source_urls", [])
    ctx.image_prompt = result.get("image_prompt", "")
    ctx.summary_en = result.get("summary_en", "")

    logger.info(
        "Article generated: '%s' (slug: %s, %d chars)",
        ctx.title_en,
        ctx.slug,
        len(ctx.article_en),
    )
