"""S9: Verify — check that articles are live on ender.faion.net."""

from __future__ import annotations

import logging

import httpx

from pipeline.config import SITE_BASE_URL
from pipeline.context import PipelineContext

logger = logging.getLogger(__name__)


def run(ctx: PipelineContext) -> bool:
    """Verify that the article pages are accessible. Returns True if OK."""
    urls = []
    if ctx.article_url_en:
        urls.append(("EN", ctx.article_url_en))
    if ctx.article_url_ua:
        urls.append(("UA", ctx.article_url_ua))

    if not urls:
        # Construct URLs from slug
        urls = [
            ("EN", f"{SITE_BASE_URL}/en/{ctx.slug}/"),
            ("UA", f"{SITE_BASE_URL}/ua/{ctx.slug}/"),
        ]

    all_ok = True
    for lang, url in urls:
        try:
            resp = httpx.get(url, timeout=15, follow_redirects=True)
            if resp.status_code == 200:
                logger.info("Verify OK: %s %s", lang, url)
            else:
                logger.warning("Verify FAIL: %s %s -> %d", lang, url, resp.status_code)
                all_ok = False
        except Exception as e:
            logger.warning("Verify ERROR: %s %s -> %s", lang, url, e)
            all_ok = False

    ctx.site_ok = all_ok
    return all_ok
