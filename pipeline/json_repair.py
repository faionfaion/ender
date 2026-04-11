"""JSON repair utilities for LLM output."""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


def safe_parse_json(raw: str) -> dict | None:
    """Parse JSON from LLM output with progressive repair."""
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # Step 1: try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 2: extract from markdown fences
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            text = m.group(1).strip()

    # Step 3: find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            text = candidate

    # Step 4: fix unicode quotes
    fixed = text.replace("\u201c", '"').replace("\u201d", '"')
    fixed = fixed.replace("\u2018", "'").replace("\u2019", "'")
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Step 5: remove trailing commas
    fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Step 6: remove control chars (except \n, \t)
    fixed = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Step 7: escape unescaped backslashes
    fixed = fixed.replace("\\", "\\\\")
    fixed = fixed.replace('\\\\"', '\\"')  # fix double-escaped
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    logger.error("JSON repair failed for: %s", raw[:300])
    return None
