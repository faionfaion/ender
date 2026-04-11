"""Run report — tracks stage timing and status."""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pipeline.config import STATE_DIR

logger = logging.getLogger(__name__)


@dataclass
class RunReport:
    """Pipeline execution report."""

    mode: str = "generate"
    started_at: str = ""
    stages: dict = field(default_factory=dict)
    slug: str = ""
    character: str = ""
    languages: list[str] = field(default_factory=list)
    image_generated: bool = False
    msg_ids: dict = field(default_factory=dict)
    exit_status: str = "ok"
    error: str = ""
    failed_stage: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()

    @contextmanager
    def time_stage(self, name: str):
        """Time a pipeline stage."""
        start = time.monotonic()
        self.stages[name] = {"status": "running", "duration_s": 0}
        try:
            yield
            elapsed = time.monotonic() - start
            self.stages[name] = {"status": "ok", "duration_s": round(elapsed, 1)}
        except Exception as e:
            elapsed = time.monotonic() - start
            self.stages[name] = {
                "status": "error",
                "duration_s": round(elapsed, 1),
                "error": str(e)[:200],
            }
            self.exit_status = "error"
            self.failed_stage = name
            self.error = str(e)[:500]
            raise

    def save(self) -> None:
        """Save report to state/runs/."""
        runs_dir = STATE_DIR / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        path = runs_dir / f"{ts}.json"

        total_s = sum(s.get("duration_s", 0) for s in self.stages.values())

        data = {
            "mode": self.mode,
            "started_at": self.started_at,
            "duration_s": round(total_s, 1),
            "exit_status": self.exit_status,
            "slug": self.slug,
            "character": self.character,
            "languages": self.languages,
            "image_generated": self.image_generated,
            "msg_ids": self.msg_ids,
            "stages": self.stages,
        }
        if self.error:
            data["error"] = self.error
            data["failed_stage"] = self.failed_stage

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info("Run report saved: %s", path)
