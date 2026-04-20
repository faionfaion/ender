"""S7-save: Save article files, generate image, update state, git commit."""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pipeline.config import CHARACTERS, CONTENT_DIR, ROOT, SITE_BASE_URL, STATE_DIR
from pipeline.context import PipelineContext
from pipeline.stages.s_image_orchestrator import generate_with_qa

logger = logging.getLogger(__name__)


def run(ctx: PipelineContext, dry_run: bool = False) -> None:
    """Save markdown files, generate image, update state."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    char = CHARACTERS.get(ctx.character, CHARACTERS["ender"])

    # Generate image (via orchestrator: editor -> gen -> QA -> retry)
    if not dry_run:
        image_path = generate_with_qa(
            raw_prompt=ctx.image_prompt,
            slug=ctx.slug,
            character=ctx.character,
        )
        ctx.image_path = image_path
    else:
        logger.info("[DRY RUN] Skipping image generation")
        image_path = None

    image_field = f"/images/{ctx.slug}.png" if image_path else ""

    # Build article URLs
    ctx.article_url_en = f"{SITE_BASE_URL}/en/{ctx.slug}/"
    ctx.article_url_ua = f"{SITE_BASE_URL}/ua/{ctx.slug}/"

    # Write EN markdown
    en_path = _write_article(
        date=today,
        slug=ctx.slug,
        lang="en",
        title=ctx.title_en,
        article=ctx.article_en,
        description=ctx.description_en,
        tags=ctx.tags,
        author=char["name"],
        article_type=ctx.article_type,
        image=image_field,
        tg_post=ctx.tg_post_en,
        dry_run=dry_run,
    )

    # Write UA markdown
    ua_path = _write_article(
        date=today,
        slug=ctx.slug,
        lang="ua",
        title=ctx.title_ua,
        article=ctx.article_ua,
        description=ctx.description_ua,
        tags=ctx.tags,
        author=char["name"],
        article_type=ctx.article_type,
        image=image_field,
        tg_post=ctx.tg_post_ua,
        dry_run=dry_run,
    )

    # Save teaser
    if not dry_run:
        _save_teaser(ctx, today)

    # Update summaries
    if not dry_run:
        _update_summaries(ctx, today)

    # Git commit
    if not dry_run:
        _git_commit(ctx, today, en_path, ua_path)

    logger.info("Article saved: %s (EN + UA)", ctx.slug)


def _write_article(
    date: str,
    slug: str,
    lang: str,
    title: str,
    article: str,
    description: str,
    tags: list[str],
    author: str,
    article_type: str,
    image: str,
    tg_post: str,
    dry_run: bool,
) -> Path:
    """Write a markdown article file with frontmatter."""
    content_dir = Path(CONTENT_DIR)
    content_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{date}-{slug}-{lang}.md"
    filepath = content_dir / filename

    tags_str = json.dumps(tags)
    # Escape quotes in tg_post for frontmatter
    tg_post_escaped = tg_post.replace('"', '\\"')

    frontmatter = (
        f'---\n'
        f'title: "{title}"\n'
        f'slug: "{slug}"\n'
        f'date: "{date}"\n'
        f'type: "{article_type}"\n'
        f'lang: "{lang}"\n'
        f'tags: {tags_str}\n'
        f'description: "{description}"\n'
        f'author: "{author}"\n'
        f'image: "{image}"\n'
        f'tg_post: "{tg_post_escaped}"\n'
        f'---\n\n'
    )

    content = frontmatter + article

    if dry_run:
        logger.info("[DRY RUN] Would write: %s (%d chars)", filepath, len(content))
    else:
        filepath.write_text(content, encoding="utf-8")
        logger.info("Written: %s (%d chars)", filepath, len(content))

    return filepath


def _save_teaser(ctx: PipelineContext, date: str) -> None:
    """Save teaser JSON for TG publish scheduling."""
    teasers_dir = STATE_DIR / "teasers"
    teasers_dir.mkdir(parents=True, exist_ok=True)

    teaser = {
        "slug": ctx.slug,
        "date": date,
        "title_en": ctx.title_en,
        "title_ua": ctx.title_ua,
        "tg_post_en": ctx.tg_post_en,
        "tg_post_ua": ctx.tg_post_ua,
        "character": ctx.character,
        "article_type": ctx.article_type,
        "image": f"/images/{ctx.slug}.png" if ctx.image_path else "",
        "published_en": False,
        "published_ua": False,
    }

    teaser_path = teasers_dir / f"{ctx.slug}.json"
    teaser_path.write_text(json.dumps(teaser, indent=2, ensure_ascii=False))
    logger.info("Teaser saved: %s", teaser_path)


def _update_summaries(ctx: PipelineContext, date: str) -> None:
    """Append to summaries.json for editorial plan dedup."""
    summaries_path = STATE_DIR / "summaries.json"

    if summaries_path.exists():
        try:
            data = json.loads(summaries_path.read_text())
        except Exception:
            data = []
    else:
        data = []

    data.append({
        "date": date,
        "slug": ctx.slug,
        "title_en": ctx.title_en,
        "title_ua": ctx.title_ua,
        "topic": ctx.topic,
        "article_type": ctx.article_type,
        "character": ctx.character,
        "summary_en": ctx.summary_en,
    })

    summaries_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _git_commit(ctx: PipelineContext, date: str, en_path: Path, ua_path: Path) -> None:
    """Git add and commit the new article files."""
    try:
        subprocess.run(
            ["git", "add", str(en_path), str(ua_path)],
            cwd=str(ROOT),
            check=True,
            capture_output=True,
        )
        # Also add image if it exists
        if ctx.image_path and ctx.image_path.exists():
            subprocess.run(
                ["git", "add", str(ctx.image_path)],
                cwd=str(ROOT),
                check=True,
                capture_output=True,
            )
        # Add state files
        subprocess.run(
            ["git", "add", "state/"],
            cwd=str(ROOT),
            check=True,
            capture_output=True,
        )

        msg = f"content: add {ctx.slug} ({ctx.article_type})"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(ROOT),
            check=True,
            capture_output=True,
        )
        logger.info("Git commit: %s", msg)
    except subprocess.CalledProcessError as e:
        logger.warning("Git commit failed: %s", e.stderr.decode()[:200] if e.stderr else str(e))
