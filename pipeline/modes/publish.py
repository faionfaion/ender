"""Publish mode — pick next unpublished article, send to TG channels."""

from __future__ import annotations

import logging

from pipeline.run_report import RunReport
from pipeline.stages import s10_pick_and_publish

logger = logging.getLogger(__name__)


def run() -> None:
    """Publish the next unpublished article to both TG channels."""
    report = RunReport(mode="publish")

    try:
        with report.time_stage("s10_pick_and_publish"):
            published = s10_pick_and_publish.run()

        if published:
            report.exit_status = "ok"
            logger.info("Publish mode complete: article sent")
        else:
            report.exit_status = "ok"
            logger.info("Publish mode complete: nothing to publish")

    except Exception as e:
        logger.error("Publish failed: %s", e)
        report.exit_status = "error"
        report.error = str(e)[:500]

    finally:
        report.save()
