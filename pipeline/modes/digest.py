"""Digest mode — compile day's articles into evening digest for TG."""

from __future__ import annotations

import logging

from pipeline.run_report import RunReport
from pipeline.stages import s11_digest

logger = logging.getLogger(__name__)


def run() -> None:
    """Create and send the evening digest to both TG channels."""
    report = RunReport(mode="digest")

    try:
        with report.time_stage("s11_digest"):
            sent = s11_digest.run()

        if sent:
            report.exit_status = "ok"
            logger.info("Digest mode complete: digest sent")
        else:
            report.exit_status = "ok"
            logger.info("Digest mode complete: no articles to digest")

    except Exception as e:
        logger.error("Digest failed: %s", e)
        report.exit_status = "error"
        report.error = str(e)[:500]

    finally:
        report.save()
