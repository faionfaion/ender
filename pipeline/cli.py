"""CLI for Ender pipeline — generate, publish, digest, plan."""

from __future__ import annotations

import argparse
import json
import logging
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ender-pipeline",
        description="Ender — Roblox media pipeline for kids",
    )
    parser.add_argument(
        "mode",
        choices=["generate", "publish", "digest", "plan"],
        help="Pipeline mode to run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving/publishing (generate mode)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.mode == "generate":
        from pipeline.modes.generate import run
        run(dry_run=args.dry_run)

    elif args.mode == "publish":
        from pipeline.modes.publish import run
        run()

    elif args.mode == "digest":
        from pipeline.modes.digest import run
        run()

    elif args.mode == "plan":
        from pipeline.stages.s0_editorial_plan import run
        plan = run()
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        sys.exit(0)
