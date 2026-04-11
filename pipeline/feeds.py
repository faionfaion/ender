"""RSS feed fetcher for Roblox news sources."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

import httpx

from pipeline.config import RSS_FEEDS

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "EnderBot/1.0"}
_DEDUP_THRESHOLD = 0.7


def fetch_rss_headlines(max_per_feed: int = 10) -> list[dict]:
    """Fetch headlines from all configured RSS feeds."""
    all_items: list[dict] = []

    for name, url in RSS_FEEDS.items():
        try:
            resp = httpx.get(url, headers=_HEADERS, timeout=15, follow_redirects=True)
            resp.raise_for_status()
            items = _parse_feed(resp.text, name)
            all_items.extend(items[:max_per_feed])
            logger.info("RSS %s: %d items", name, len(items))
        except Exception as e:
            logger.warning("RSS %s failed: %s", name, e)

    # Deduplicate
    return _deduplicate(all_items)


def _parse_feed(xml_text: str, source: str) -> list[dict]:
    """Parse RSS 2.0 or Atom feed."""
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    # RSS 2.0
    for item in root.iter("item"):
        title = _text(item, "title")
        link = _text(item, "link")
        desc = _text(item, "description")
        if title:
            items.append({
                "title": _clean(title),
                "url": link,
                "description": _clean(desc)[:300],
                "source": source,
            })

    # Atom
    if not items:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            title = _text(entry, "atom:title", ns)
            link_el = entry.find("atom:link", ns)
            link = link_el.get("href", "") if link_el is not None else ""
            summary = _text(entry, "atom:summary", ns)
            if title:
                items.append({
                    "title": _clean(title),
                    "url": link,
                    "description": _clean(summary)[:300],
                    "source": source,
                })

    return items


def _text(el: ET.Element, tag: str, ns: dict | None = None) -> str:
    child = el.find(tag, ns) if ns else el.find(tag)
    return (child.text or "").strip() if child is not None else ""


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _deduplicate(items: list[dict]) -> list[dict]:
    """Remove items with similar titles."""
    unique: list[dict] = []
    for item in items:
        is_dup = False
        for existing in unique:
            ratio = SequenceMatcher(
                None, item["title"].lower(), existing["title"].lower()
            ).ratio()
            if ratio > _DEDUP_THRESHOLD:
                is_dup = True
                break
        if not is_dup:
            unique.append(item)
    return unique
