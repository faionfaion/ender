"""Central configuration for Ender — Roblox media pipeline."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATE_DIR = ROOT / "state"
SCRIPTS_DIR = ROOT / "scripts"
PROMPTS_DIR = ROOT / "pipeline" / "prompts"
GATSBY_DIR = ROOT / "gatsby"
IMAGES_DIR = GATSBY_DIR / "static" / "images"

# Site
SITE_BASE_URL = "https://ender.faion.net"
SITE_NAME = "Ender — Roblox Media"

# Languages (bilingual)
LANGUAGES = ["ua", "en"]
SOURCE_LANG = "en"  # generate in EN first, translate to UA

# LLM
MODEL = os.getenv("ENDER_MODEL", "opus")
RETRY_MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 5.0
RETRY_MAX_DELAY = 60.0

# Telegram — shared bot, two channels
TG_BOT_TOKEN = os.getenv(
    "NERO_TG_BOT_TOKEN",
    "8585090528:AAHWmjiT9TIlmdtz0x8Q_YpUCnP3APEx7i8",
)

TG_CHANNELS = {
    "ua": {
        "id": os.getenv("ENDER_TG_UA_ID", ""),  # set after channel creation
        "username": "ender_faion_ua",
    },
    "en": {
        "id": os.getenv("ENDER_TG_EN_ID", ""),  # set after channel creation
        "username": "ender_faion_en",
    },
}

# Sound window (UTC hours when notification sound is ON)
SOUND_ON_START = 9
SOUND_ON_END = 20

# Schedule
GENERATE_HOUR = 7        # 07:00 UTC daily batch
MAX_ARTICLES_PER_DAY = 5  # HARD LIMIT
TG_PUBLISH_HOURS = [9, 11, 14, 17]  # 4 slots + digest at 19
DIGEST_HOUR = 19

# Content types with word count ranges
CONTENT_TYPES = {
    "news": {"min_words": 200, "max_words": 500, "per_day": "1-2"},
    "guide": {"min_words": 500, "max_words": 1500, "per_day": "1-2"},
    "review": {"min_words": 300, "max_words": 800, "per_day": "1"},
    "lifehack": {"min_words": 200, "max_words": 400, "per_day": "1"},
    "top": {"min_words": 400, "max_words": 1000, "per_day": "0-1"},
}

# Characters
CHARACTERS = {
    "ender": {
        "name": "EnderFaion",
        "role": "main",
        "description": (
            "A Roblox girl character, enthusiastic gamer and content creator. "
            "She knows everything about Roblox — new updates, best games, building tricks, "
            "and community trends. Friendly, energetic, uses gaming slang naturally. "
            "Speaks to her audience like a friend who just discovered something cool."
        ),
        "emoji": "\U0001f3ae",  # controller
        "frequency": 0.8,  # 80% of articles
    },
    "dad": {
        "name": "FaionEnder",
        "role": "dad",
        "description": (
            "EnderFaion's dad, also a Roblox player. A bit old-school but genuinely "
            "enjoys gaming with his daughter. His favorite game is '99 Nights in the Forest' "
            "(a spooky survival game). Gives dad-jokes, shares wisdom about patience in gaming, "
            "and sometimes writes 'Dad's Corner' articles. Warm, funny, slightly embarrassing."
        ),
        "emoji": "\U0001f9d4",  # bearded person
        "frequency": 0.2,  # 20% of articles
    },
}

# Image generation
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1536  # vertical 2:3
IMAGE_MODEL = "gpt-image-1"
IMAGE_STYLE = (
    "Roblox-style 3D render, bright colorful blocky characters, "
    "clean digital art, vibrant colors, kid-friendly, no text overlay. "
    "Characters have classic Roblox proportions — blocky body, round head, "
    "simple facial features."
)

# Character visual descriptions for image generation
CHARACTER_VISUALS = {
    "ender": (
        "EnderFaion: a Roblox girl character with purple hair in twin tails, "
        "bright green eyes, wearing a black hoodie with an ender pearl logo, "
        "purple sneakers, a silver headset around her neck. "
        "Expression: confident smile, ready for adventure."
    ),
    "dad": (
        "FaionEnder: a tall Roblox dad character with brown short hair, "
        "square glasses, wearing a green plaid shirt over a white t-shirt, "
        "jeans, brown boots. Has a small camping backpack. "
        "Expression: warm goofy smile, slightly tired but happy."
    ),
}

# Topics for editorial planning
TOPICS = [
    "roblox-updates",
    "game-reviews",
    "building-guides",
    "obby-tips",
    "trading-tips",
    "dev-tutorials",
    "community-events",
    "records-achievements",
    "trends-memes",
    "dad-corner",
]

# Hashtags
HASHTAGS_UA = {
    "roblox-updates": "#Роблокс #Оновлення",
    "game-reviews": "#Роблокс #ОглядГри",
    "building-guides": "#Роблокс #Гайд #Будівництво",
    "obby-tips": "#Роблокс #Обі #Лайфхак",
    "trading-tips": "#Роблокс #Трейдинг",
    "dev-tutorials": "#Роблокс #RobloxStudio #Розробка",
    "community-events": "#Роблокс #Івент",
    "records-achievements": "#Роблокс #Рекорд",
    "trends-memes": "#Роблокс #Тренди #Меми",
    "dad-corner": "#Роблокс #ТатовийКуточок",
}

HASHTAGS_EN = {
    "roblox-updates": "#Roblox #Updates",
    "game-reviews": "#Roblox #GameReview",
    "building-guides": "#Roblox #Guide #Building",
    "obby-tips": "#Roblox #Obby #Tips",
    "trading-tips": "#Roblox #Trading",
    "dev-tutorials": "#Roblox #RobloxStudio #Dev",
    "community-events": "#Roblox #Event",
    "records-achievements": "#Roblox #Record",
    "trends-memes": "#Roblox #Trends #Memes",
    "dad-corner": "#Roblox #DadsCorner",
}

# RSS / News sources for Roblox content
RSS_FEEDS = {
    "roblox_blog": "https://blog.roblox.com/feed/",
    "roblox_devforum": "https://devforum.roblox.com/latest.rss",
}

# Review loop
MAX_REVIEW_CYCLES = 3
MAX_TG_REVIEW_CYCLES = 2

# Deploy
DEPLOY_SCRIPT = GATSBY_DIR / "deploy-gh.sh"
