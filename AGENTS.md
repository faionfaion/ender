# Ender — Roblox Media for Kids

Roblox news, guides, lifehacks, game reviews, trends, records, map creation tutorials.
Site: ender.faion.net. TG: @ender_faion_ua (UA), @ender_faion_en (EN).

## Structure

| Path | Purpose |
|------|---------|
| `pipeline/` | Content generation pipeline (Claude Agent SDK) |
| `pipeline/config.py` | All constants: models, channels, content types, schedules |
| `pipeline/sdk.py` | Claude Agent SDK wrappers (structured_query, agent_query) |
| `pipeline/stages/` | Pipeline stages (s0-s11) |
| `pipeline/modes/` | Execution modes: generate, publish, digest |
| `pipeline/prompts/templates/` | Jinja2 XML prompt templates |
| `pipeline/schemas/` | JSON schemas for structured LLM output |
| `content/` | Generated markdown articles (YYYY-MM-DD-slug-lang.md) |
| `gatsby/` | Gatsby 5 static site |
| `state/` | Runtime state (plans, teasers, summaries, logs) |
| `scripts/` | Cron runner, deploy scripts |
| `site/nginx/` | Nginx config for ender.faion.net |

## Characters

| Name | Role | Description |
|------|------|-------------|
| EnderFaion | Main author | Roblox girl character, enthusiastic gamer, knows everything about Roblox |
| FaionEnder | Dad | Her dad, loves "99 Nights in the Forest", gives dad-jokes and wisdom |

## Pipeline

| Mode | Schedule | What |
|------|----------|------|
| generate | 07:00 UTC daily | Batch 5 articles (UA + EN = 10 files) |
| publish | 09:05, 11:05, 14:05, 17:05 UTC | Pick & send to 2 TG channels |
| digest | 19:05 UTC | Evening digest to both channels |

## Content Types

| Type | Words | Per day |
|------|-------|---------|
| news | 200-500 | 1-2 |
| guide | 500-1500 | 1-2 |
| review | 300-800 | 1 |
| lifehack | 200-400 | 1 |
| top | 400-1000 | 0-1 |

## Commands

```bash
python3 -m pipeline generate --dry-run -v   # test run
python3 -m pipeline generate -v             # full generation
python3 -m pipeline publish -v              # single TG publish
python3 -m pipeline digest -v               # evening digest
python3 -m pipeline plan                    # show today's plan
```

## Deploy

```bash
bash gatsby/deploy-gh.sh    # requires: source ~/bin/op_unlock.sh
```

## Key Rules

- Max 5 articles per day (hard limit)
- Both UA and EN for every article
- Vertical images (1024x1536) with Roblox characters
- EnderFaion writes most posts, FaionEnder appears in ~20% (dad's corner)
- Fun, engaging tone for kids/teens
- No violence, gambling, or inappropriate content
