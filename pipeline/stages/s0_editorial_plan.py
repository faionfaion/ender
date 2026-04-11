"""S0: Editorial plan — LLM creates 5 topics for the day."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from pipeline.config import (
    CHARACTERS,
    CONTENT_TYPES,
    HASHTAGS_EN,
    STATE_DIR,
    TOPICS,
)
from pipeline.sdk import structured_query

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are the editorial planner for Ender, a bilingual (EN+UA) Roblox media site "
    "for kids and teens. You create a daily content plan with exactly 5 articles.\n\n"
    "Characters:\n"
    "- EnderFaion (character key: 'ender'): main author, ~80% of articles. "
    "Enthusiastic Roblox girl gamer.\n"
    "- FaionEnder (character key: 'dad'): dad's corner, ~20% of articles. "
    "Funny gaming dad.\n\n"
    "Rules:\n"
    "- Exactly 5 articles per day\n"
    "- 4 articles by EnderFaion, 1 by FaionEnder (dad's corner)\n"
    "- Mix content types (news, guide, review, lifehack, top)\n"
    "- Each article must have a unique angle — no repetition\n"
    "- Content must be kid-friendly, fun, and engaging\n"
    "- No violence, gambling, or inappropriate content\n"
    "- Dad's article should use topic 'dad-corner'\n"
    "- Avoid topics already covered in recent summaries\n\n"
    "Return valid JSON matching the editorial_plan schema."
)


def run() -> dict:
    """Create editorial plan for today. Returns plan dict."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    plans_dir = STATE_DIR / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    # Check if plan already exists
    plan_path = plans_dir / f"{today}.json"
    if plan_path.exists():
        logger.info("Plan already exists for %s, loading", today)
        return json.loads(plan_path.read_text())

    # Load recent summaries for dedup
    recent_summaries = _load_recent_summaries()

    # Load RSS headlines for inspiration
    try:
        from pipeline.feeds import fetch_rss_headlines
        headlines = fetch_rss_headlines(max_per_feed=5)
        headlines_text = "\n".join(
            f"- {h['title']}" for h in headlines[:10]
        )
    except Exception as e:
        logger.warning("Failed to fetch RSS: %s", e)
        headlines_text = "(no RSS headlines available)"

    topics_list = ", ".join(TOPICS)
    types_list = ", ".join(
        f"{k} ({v['min_words']}-{v['max_words']} words)"
        for k, v in CONTENT_TYPES.items()
    )

    prompt = (
        f"Create an editorial plan for {today}.\n\n"
        f"Available topics: {topics_list}\n"
        f"Content types: {types_list}\n\n"
        f"Recent RSS headlines for inspiration:\n{headlines_text}\n\n"
        f"Recent articles already published (avoid repeating these):\n"
        f"{recent_summaries}\n\n"
        f"Plan exactly 5 articles:\n"
        f"- 4 by EnderFaion (character: 'ender')\n"
        f"- 1 by FaionEnder (character: 'dad', topic: 'dad-corner')\n\n"
        f"Return JSON with date and topics array."
    )

    plan = structured_query(
        prompt=prompt,
        system_prompt=_SYSTEM_PROMPT,
    )

    # Validate and fix plan
    plan["date"] = today
    if "topics" not in plan:
        raise ValueError("Plan missing 'topics' key")

    # Ensure exactly 5 topics
    plan["topics"] = plan["topics"][:5]

    # Save
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
    logger.info("Editorial plan saved: %s (%d topics)", plan_path, len(plan["topics"]))

    return plan


def _load_recent_summaries() -> str:
    """Load recent article summaries for dedup."""
    summaries_path = STATE_DIR / "summaries.json"
    if not summaries_path.exists():
        return "(no previous articles)"

    try:
        data = json.loads(summaries_path.read_text())
        if not data:
            return "(no previous articles)"

        # Last 30 entries
        recent = data[-30:] if isinstance(data, list) else []
        lines = []
        for s in recent:
            title = s.get("title_en", s.get("title", ""))
            topic = s.get("topic", "")
            date = s.get("date", "")
            lines.append(f"- [{date}] {title} ({topic})")
        return "\n".join(lines) if lines else "(no previous articles)"
    except Exception:
        return "(no previous articles)"
