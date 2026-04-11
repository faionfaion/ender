"""S10: Pick and publish — find next unpublished article, send to TG."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline.config import CHARACTERS, IMAGES_DIR, STATE_DIR
from pipeline.telegram import add_reaction, send_photo, send_text

logger = logging.getLogger(__name__)


def run() -> bool:
    """Find today's next unpublished article and send to both TG channels.

    Returns True if an article was published.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    teasers_dir = STATE_DIR / "teasers"
    published_dir = STATE_DIR / "tg_published"
    published_dir.mkdir(parents=True, exist_ok=True)

    if not teasers_dir.exists():
        logger.info("No teasers directory, nothing to publish")
        return False

    # Find unpublished teasers for today
    teaser = _find_next_unpublished(teasers_dir, today)
    if not teaser:
        logger.info("No unpublished articles for today")
        return False

    slug = teaser["slug"]
    character = teaser.get("character", "ender")
    char = CHARACTERS.get(character, CHARACTERS["ender"])

    # Find image
    image_path = IMAGES_DIR / f"{slug}.png"
    if not image_path.exists():
        logger.warning("Image not found for %s, sending text only", slug)
        image_path = None

    # Publish to both channels
    for lang in ["en", "ua"]:
        tg_post = teaser.get(f"tg_post_{lang}", "")
        if not tg_post:
            logger.warning("No TG post for %s/%s, skipping", slug, lang)
            continue

        if image_path:
            msg_id = send_photo(
                image_path=image_path,
                caption=tg_post,
                lang=lang,
            )
        else:
            msg_id = send_text(text=tg_post, lang=lang)

        if msg_id:
            teaser[f"published_{lang}"] = True
            teaser[f"msg_id_{lang}"] = msg_id
            # Add fire reaction
            add_reaction(msg_id, lang, char["emoji"])
            logger.info("Published %s to %s: msg_id=%d", slug, lang, msg_id)

    # Save updated teaser
    teaser_path = teasers_dir / f"{slug}.json"
    teaser_path.write_text(json.dumps(teaser, indent=2, ensure_ascii=False))

    # Mark as published
    pub_record = {
        "slug": slug,
        "date": today,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "msg_id_en": teaser.get("msg_id_en", 0),
        "msg_id_ua": teaser.get("msg_id_ua", 0),
    }
    pub_path = published_dir / f"{slug}.json"
    pub_path.write_text(json.dumps(pub_record, indent=2, ensure_ascii=False))

    logger.info("Published article: %s", slug)
    return True


def _find_next_unpublished(teasers_dir: Path, today: str) -> dict | None:
    """Find the next unpublished teaser for today."""
    candidates = []

    for teaser_file in sorted(teasers_dir.glob("*.json")):
        try:
            teaser = json.loads(teaser_file.read_text())
        except Exception:
            continue

        if teaser.get("date") != today:
            continue

        # Check if already fully published
        if teaser.get("published_en") and teaser.get("published_ua"):
            continue

        candidates.append(teaser)

    if not candidates:
        return None

    # Return the first unpublished one
    return candidates[0]
