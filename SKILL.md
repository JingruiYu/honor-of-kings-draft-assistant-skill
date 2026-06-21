---
name: honor-of-kings-draft-assistant
description: Honor of Kings draft, matchup, build, and playstyle assistant. Use it when the user asks which hero to pick, how to fill a lane, how to adjust builds, or how to record/update hero pool and match feedback.
---

# Honor of Kings Draft Assistant

This skill helps with Honor of Kings hero selection, lane filling, matchup reasoning, builds, runes, summoner spells, and short playstyle advice.

中文优先：用户通常会用中文描述阵容、分路、英雄池和战绩。回答时默认用简洁中文。

The default data uses Chinese hero names for the mainland 王者荣耀 context. Do not translate hero names unless the user explicitly maintains an English alias mapping.

## When to use

Use this skill when the user asks things like:

- “这局我补中路/游走/发育路，拿什么？”
- “我方是……对面是……推荐英雄。”
- “这局怎么出装、带什么召唤师技能？”
- “帮我记录这局战绩/胜负/出装。”
- “我第一次用，帮我整理英雄池和历史战绩。”
- “我发你截图，你帮我录入英雄池或战绩。”（仅当当前 Agent / LLM 支持视觉输入时）

## User onboarding

On first use, ask the user to provide hero-pool data in text. If the current Agent / LLM supports vision input, screenshots can also be used:

- owned heroes;
- preferred lanes;
- frequently used heroes;
- appearances and win rates;
- recent match results;
- current version tier list or strategy screenshots.

Image handling is not implemented by this script itself; it depends on the host Agent / LLM. If image input is available, extract visible hero names, lanes, win rates, ranks, match results, and builds, then update the local data files. If a field is unclear, keep it as uncertain instead of guessing.

## Local data

The repo does not commit user data. Run:

```bash
python3 scripts/recommend.py --init-data
```

to generate a local `data/` directory.

Expected files:

- `data/hero_pool.json`: user hero pool, owned heroes, lane preferences, match statistics.
- `data/meta.json`: version strength, lanes, tags, difficulty, situational flags.
- `data/matchups.json`: enemy tags, counter relationships, team needs.
- `data/builds.json`: summoner spells, runes, core builds, situational items, playstyle.
- `data/sources.json`: source notes for version/meta/matchup data.
- `data/feedback.jsonl`: post-match feedback records.

`HOK_ASSISTANT_DATA_DIR` can override the data directory.

## Recommendation logic

The script uses a transparent rule-based score:

1. Filter by lane and owned heroes.
2. Score personal familiarity from appearances, win rate, and sample size.
3. Add version/meta strength from `meta.json`.
4. Infer enemy tags such as mobility, control, sustain, tanks, poke, or engage.
5. Add matchup bonuses from `matchups.json`.
6. Attach builds and playstyle from `builds.json`.

Do not present the result as a guaranteed best pick. Mention low sample size when needed.

## CLI example

```bash
python3 scripts/recommend.py \
  --lane 中路 \
  --ally '孙策,后羿,牛魔' \
  --enemy '镜,王昭君,张飞' \
  --top-k 3
```

## Output preference

Keep replies short unless the user explicitly asks for analysis:

- 首选 / 备选；
- 关键理由；
- 核心出装和针对调整；
- 一句话打法；
- 最多 1-2 条注意事项。
