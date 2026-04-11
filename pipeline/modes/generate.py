"""Generate mode — morning batch: create up to 5 articles."""

from __future__ import annotations

import logging

from pipeline.config import MAX_ARTICLES_PER_DAY, MAX_REVIEW_CYCLES
from pipeline.context import PipelineContext
from pipeline.run_report import RunReport
from pipeline.stages import (
    s0_editorial_plan,
    s1_collect,
    s2_research,
    s3_generate,
    s4_review,
    s5_revise,
    s6_generate_tg,
    s7_save,
    s7_translate,
    s8_deploy,
    s9_verify,
)

logger = logging.getLogger(__name__)


def run(dry_run: bool = False) -> None:
    """Run the full generation pipeline for today's batch."""
    report = RunReport(mode="generate")

    try:
        # S0: Editorial plan
        with report.time_stage("s0_editorial_plan"):
            plan = s0_editorial_plan.run()

        # S1: Collect RSS + existing slugs
        with report.time_stage("s1_collect"):
            collection = s1_collect.run()

        existing_slugs = collection.get("existing_slugs", [])
        topics = plan.get("topics", [])[:MAX_ARTICLES_PER_DAY]

        logger.info(
            "Starting batch: %d topics, %d existing slugs",
            len(topics), len(existing_slugs),
        )

        # Process each topic
        for i, topic_info in enumerate(topics):
            topic_label = topic_info.get("topic_label", f"topic-{i}")
            logger.info("=== Article %d/%d: %s ===", i + 1, len(topics), topic_label)

            ctx = PipelineContext(
                topic=topic_info.get("topic", ""),
                topic_label=topic_label,
                article_type=topic_info.get("article_type", "news"),
                character=topic_info.get("character", "ender"),
            )

            try:
                _generate_single(ctx, report, i, dry_run)
            except Exception as e:
                logger.error("Failed to generate article '%s': %s", topic_label, e)
                continue

        # S8: Deploy (skip in dry-run)
        if not dry_run:
            with report.time_stage("s8_deploy"):
                s8_deploy.run()

        report.exit_status = "ok"
        logger.info("Batch generation complete")

    except Exception as e:
        logger.error("Pipeline failed: %s", e)
        report.exit_status = "error"
        report.error = str(e)[:500]

    finally:
        report.save()


def _generate_single(
    ctx: PipelineContext,
    report: RunReport,
    index: int,
    dry_run: bool,
) -> None:
    """Generate a single article through all stages."""
    prefix = f"article_{index}"

    # S2: Research
    with report.time_stage(f"{prefix}_s2_research"):
        s2_research.run(ctx)

    # S3: Generate EN article
    with report.time_stage(f"{prefix}_s3_generate"):
        s3_generate.run(ctx)

    # S4 + S5: Review-revise loop (max 3 cycles)
    for cycle in range(MAX_REVIEW_CYCLES):
        with report.time_stage(f"{prefix}_s4_review_c{cycle}"):
            s4_review.run(ctx)

        if ctx.review_approved:
            logger.info("Article approved on cycle %d", cycle + 1)
            break

        if cycle < MAX_REVIEW_CYCLES - 1:
            with report.time_stage(f"{prefix}_s5_revise_c{cycle}"):
                s5_revise.run(ctx)
        else:
            logger.warning("Max review cycles reached, proceeding anyway")

    # S6: Generate TG posts
    with report.time_stage(f"{prefix}_s6_generate_tg"):
        s6_generate_tg.run(ctx)

    # S7: Translate to UA
    with report.time_stage(f"{prefix}_s7_translate"):
        s7_translate.run(ctx)

    # S7-save: Save files + generate image
    with report.time_stage(f"{prefix}_s7_save"):
        s7_save.run(ctx, dry_run=dry_run)

    # S9: Verify (skip in dry-run)
    if not dry_run:
        with report.time_stage(f"{prefix}_s9_verify"):
            s9_verify.run(ctx)

    report.slug = ctx.slug
    report.character = ctx.character
    report.languages = ["en", "ua"]
    report.image_generated = ctx.image_path is not None

    logger.info(
        "Article complete: %s ('%s' by %s)",
        ctx.slug, ctx.title_en, ctx.character,
    )
