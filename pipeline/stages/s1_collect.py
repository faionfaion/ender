"""S1: Collect — fetch RSS headlines and load existing article slugs."""

from __future__ import annotations

import logging
from pathlib import Path

from pipeline.config import CONTENT_DIR
from pipeline.feeds import fetch_rss_headlines

logger = logging.getLogger(__name__)


def run() -> dict:
    """Collect RSS headlines and existing slugs. Returns collection dict."""

    # Fetch RSS
    try:
        headlines = fetch_rss_headlines(max_per_feed=10)
        logger.info("Collected %d RSS headlines", len(headlines))
    except Exception as e:
        logger.warning("RSS fetch failed: %s", e)
        headlines = []

    # Load existing article slugs from content/*.md
    existing_slugs = _load_existing_slugs()
    logger.info("Found %d existing articles", len(existing_slugs))

    return {
        "headlines": headlines,
        "existing_slugs": existing_slugs,
    }


def _load_existing_slugs() -> list[str]:
    """Extract slugs from content directory filenames."""
    slugs = set()
    content_dir = Path(CONTENT_DIR)
    if not content_dir.exists():
        return []

    for md_file in content_dir.glob("*.md"):
        # Filename format: YYYY-MM-DD-slug-lang.md
        name = md_file.stem  # e.g. 2026-04-11-roblox-update-en
        parts = name.split("-")
        if len(parts) >= 5:
            # Skip date (3 parts) and lang (last part)
            slug = "-".join(parts[3:-1])
            slugs.add(slug)

    return sorted(slugs)
