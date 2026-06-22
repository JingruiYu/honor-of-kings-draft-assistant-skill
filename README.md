# Honor of Kings Draft Assistant Skill

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a>
</p>

A lightweight Agent skill for **Honor of Kings** draft assistance. It helps users choose heroes, fill lanes, reason about matchups, adjust builds, and record post-match feedback based on local configurable data.

> Official game name: **Honor of Kings**.
>
> The default templates target the mainland Chinese 王者荣耀 context and intentionally use Chinese hero names. If you target another regional version, update the data files and hero aliases accordingly.

## What it is for

Use this skill when a user wants to:

- choose a hero during draft / BP;
- fill a specific lane based on current allied and enemy picks;
- ask for build, rune, summoner spell, or playstyle adjustments;
- record match results, heroes, lanes, KDA, builds, and feedback;
- initialize or update a personal hero pool and match-history dataset.

The skill is designed for Chinese-language gameplay conversations, but the repository documentation is available in both English and Chinese.

## Quick start

```bash
python3 scripts/recommend.py --init-data
python3 scripts/recommend.py \
  --lane 中路 \
  --ally '孙策,后羿,牛魔' \
  --enemy '镜,王昭君,张飞' \
  --top-k 3
```

By default, runtime data is generated under `data/`. To store data elsewhere:

```bash
export HOK_ASSISTANT_DATA_DIR=/path/to/my/hok-data
python3 scripts/recommend.py --init-data
```

## Repository layout

```text
.
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── scripts/
│   └── recommend.py
└── templates/
    └── data/
        ├── builds.json
        ├── feedback.jsonl
        ├── hero_pool.json
        ├── matchups.json
        ├── meta.json
        └── sources.json
```

## Runtime data

`templates/data/` contains public starter templates. These files are committed to the repository and are intended to show the expected data schema.

`data/` is local runtime data. It is generated from `templates/data/` by:

```bash
python3 scripts/recommend.py --init-data
```

Expected local files:

- `data/hero_pool.json`: owned heroes, preferred lanes, and optional match statistics;
- `data/meta.json`: version strength, lanes, tags, difficulty, and situational flags;
- `data/matchups.json`: enemy tags, counter relationships, and team needs;
- `data/builds.json`: summoner spells, runes, core builds, situational items, and playstyle notes;
- `data/sources.json`: source notes for version/meta/matchup data;
- `data/feedback.jsonl`: post-match feedback records.

`data/` should not be committed to a public repository because it may contain personal match history.

## Input modes

The script itself only reads structured JSON files and command-line arguments.

Users can provide information to an Agent in two ways:

- text: hero pool, lanes, lineups, win rates, match results, and build choices;
- images / screenshots: only if the host Agent and LLM support vision input.

If screenshots are supported, the Agent can extract visible hero names, lanes, win rates, builds, and match records, then update local `data/` files. If a field is unclear, keep it uncertain rather than guessing.

## Recommendation logic

The recommendation script is a transparent rule-based scorer:

1. Filter candidates by target lane and owned heroes.
2. Estimate personal familiarity from appearances, win rate, and sample size.
3. Add version/meta strength from `meta.json`.
4. Infer enemy lineup tags such as high mobility, control, sustain, tanks, poke, or engage.
5. Add matchup bonuses from `matchups.json`.
6. Attach builds and playstyle suggestions from `builds.json`.

It is not a machine-learning model and should not be presented as a guaranteed best pick. Its main advantage is that the logic and data are transparent, editable, and easy to calibrate with user feedback.

## Example prompts

Draft phase:

```text
我补中路。我方已选孙策、后羿、牛魔；对面镜、王昭君、张飞。推荐我拿什么？
```

In-game build adjustment:

```text
我这局甄姬，对面有蔡文姬和程咬金，还要不要出梦魇？后面怎么打？
```

Post-match feedback:

```text
这局我中路甄姬赢了，3/1/13，出了冷静鞋、面具、凝冰、日暮、梦魇。帮我记录。
```

## Skill usage

Clone this repository into an Agent skills directory that supports `SKILL.md`. The Agent can then use the instructions in `SKILL.md` to decide when to invoke the skill and how to update the local data files.

The CLI can also be used directly without an Agent.

## Related article

- [我用 Agent 打王者后，居然没怎么输过了](https://zhuanlan.zhihu.com/p/2052139141006151933) — a Chinese write-up about why I built this skill and how a small game-assistant skill reflects the broader value of personal Agent systems.

## License

MIT License.
