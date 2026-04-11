"""Pipeline context — mutable state passed between stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PipelineContext:
    """Shared state for a single article generation run."""

    # Editorial plan
    topic: str = ""
    topic_label: str = ""
    article_type: str = "news"
    character: str = "ender"  # ender or dad

    # Research
    research_text: str = ""

    # Generation (EN source)
    article_en: str = ""
    title_en: str = ""
    slug: str = ""
    description_en: str = ""
    tags: list[str] = field(default_factory=list)
    hashtags_en: str = ""
    source_urls: list[str] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)
    summary_en: str = ""

    # Translation (UA)
    article_ua: str = ""
    title_ua: str = ""
    description_ua: str = ""
    hashtags_ua: str = ""
    tg_post_ua: str = ""

    # TG post (EN)
    tg_post_en: str = ""

    # Review
    review_approved: bool = False
    review_feedback: str = ""

    # Image
    image_prompt: str = ""
    image_path: Path | None = None

    # Deploy
    article_url_en: str = ""
    article_url_ua: str = ""
    site_ok: bool = False

    # Publish
    msg_id_en: int = 0
    msg_id_ua: int = 0
