"""S8: Deploy — run gatsby/deploy-gh.sh to build and push site."""

from __future__ import annotations

import logging
import subprocess

from pipeline.config import DEPLOY_SCRIPT, ROOT

logger = logging.getLogger(__name__)


def run() -> bool:
    """Run the deploy script. Returns True on success."""
    if not DEPLOY_SCRIPT.exists():
        logger.error("Deploy script not found: %s", DEPLOY_SCRIPT)
        return False

    logger.info("Starting deploy: %s", DEPLOY_SCRIPT)

    try:
        result = subprocess.run(
            ["bash", str(DEPLOY_SCRIPT)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info("Deploy successful")
            return True
        else:
            logger.error(
                "Deploy failed (exit %d): %s",
                result.returncode,
                result.stderr[:500] if result.stderr else "no stderr",
            )
            return False

    except subprocess.TimeoutExpired:
        logger.error("Deploy timed out after 300s")
        return False
    except Exception as e:
        logger.error("Deploy error: %s", e)
        return False
