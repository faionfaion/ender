"""Claude Agent SDK wrappers — synchronous interface."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from pipeline.config import (
    MODEL,
    RETRY_BASE_DELAY,
    RETRY_MAX_ATTEMPTS,
    RETRY_MAX_DELAY,
    ROOT,
)
from pipeline.json_repair import safe_parse_json

logger = logging.getLogger(__name__)

_ALL_BUILTIN_TOOLS = [
    "Read", "Edit", "Write", "Glob", "Grep", "Bash",
    "WebSearch", "WebFetch", "Agent", "NotebookEdit",
]


def structured_query(
    prompt: str,
    system_prompt: str,
    schema: dict | None = None,
    model: str = "",
    timeout: int = 900,
) -> dict[str, Any]:
    """LLM call expecting JSON output (no tools)."""
    model = model or MODEL
    return _retry(
        lambda: _run_sdk(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            allowed_tools=[],
            disallowed_tools=_ALL_BUILTIN_TOOLS,
            timeout=timeout,
            cwd=str(ROOT),
        ),
        label="structured_query",
    )


def agent_query(
    prompt: str,
    system_prompt: str,
    model: str = "",
    allowed_tools: list[str] | None = None,
    timeout: int = 900,
) -> str:
    """LLM call with tool access (research, verification)."""
    model = model or MODEL
    tools = allowed_tools or ["WebSearch", "WebFetch"]
    return _retry(
        lambda: _run_sdk_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            allowed_tools=tools,
            timeout=timeout,
            cwd=str(ROOT),
        ),
        label="agent_query",
    )


def _run_sdk(
    prompt: str,
    system_prompt: str,
    model: str,
    allowed_tools: list[str],
    disallowed_tools: list[str] | None = None,
    timeout: int = 900,
    cwd: str = "",
) -> dict[str, Any]:
    """Run SDK and parse JSON response."""
    from claude_code_sdk import ClaudeCodeOptions, query as sdk_query

    opts = ClaudeCodeOptions(
        model=model,
        system_prompt=system_prompt,
        permission_mode="bypassPermissions",
        allowed_tools=allowed_tools,
        disallowed_tools=disallowed_tools or [],
        max_turns=1,
        cwd=cwd or str(ROOT),
    )

    raw = asyncio.run(
        asyncio.wait_for(
            _collect_text(sdk_query(prompt=prompt, options=opts)),
            timeout=timeout,
        )
    )

    if not raw.strip():
        raise ValueError("Empty response from SDK")

    parsed = safe_parse_json(raw)
    if parsed is None:
        raise ValueError(f"Failed to parse JSON: {raw[:200]}")
    return parsed


def _run_sdk_text(
    prompt: str,
    system_prompt: str,
    model: str,
    allowed_tools: list[str],
    timeout: int = 900,
    cwd: str = "",
) -> str:
    """Run SDK and return raw text response."""
    from claude_code_sdk import ClaudeCodeOptions, query as sdk_query

    opts = ClaudeCodeOptions(
        model=model,
        system_prompt=system_prompt,
        permission_mode="bypassPermissions",
        allowed_tools=allowed_tools,
        max_turns=10,
        cwd=cwd or str(ROOT),
    )

    raw = asyncio.run(
        asyncio.wait_for(
            _collect_text(sdk_query(prompt=prompt, options=opts)),
            timeout=timeout,
        )
    )
    return raw


async def _collect_text(aiter) -> str:
    """Collect text blocks from SDK async iterator."""
    parts = []
    async for msg in aiter:
        if hasattr(msg, "content"):
            if isinstance(msg.content, str):
                parts.append(msg.content)
            elif isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, "text"):
                        parts.append(block.text)
    return "\n".join(parts)


def _retry(fn, label: str = "sdk_call"):
    """Retry with exponential backoff."""
    last_error = None
    for attempt in range(1, RETRY_MAX_ATTEMPTS + 1):
        try:
            return fn()
        except Exception as e:
            last_error = e
            err_str = str(e)

            # Non-retryable
            if any(code in err_str for code in ("401", "403")):
                logger.error("%s: non-retryable error: %s", label, e)
                raise

            if attempt < RETRY_MAX_ATTEMPTS:
                delay = min(RETRY_BASE_DELAY * (2 ** (attempt - 1)), RETRY_MAX_DELAY)
                logger.warning(
                    "%s: attempt %d/%d failed (%s), retrying in %.0fs",
                    label, attempt, RETRY_MAX_ATTEMPTS, e, delay,
                )
                time.sleep(delay)
            else:
                logger.error("%s: all %d attempts failed", label, RETRY_MAX_ATTEMPTS)

    raise last_error  # type: ignore[misc]
