#!/usr/bin/env python3
"""Honor of Kings draft recommendation script.

The script keeps the original MVP rule-based logic: lane filtering, personal
hero-pool scoring, version/meta score, matchup tag bonus, and build lookup.
User data is stored in a generated local data directory.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("HOK_ASSISTANT_DATA_DIR", REPOSITORY_ROOT / "data"))

LANE_ALIASES = {
    "中": "中路",
    "中路": "中路",
    "法师": "中路",
    "射手": "发育路",
    "发育": "发育路",
    "发育路": "发育路",
    "辅助": "游走",
    "游走": "游走",
    "辅": "游走",
    "对抗": "对抗路",
    "对抗路": "对抗路",
    "上路": "对抗路",
    "打野": "打野",
    "野": "打野",
}

DEFAULT_JSON_FILES: dict[str, dict[str, Any]] = {
    "hero_pool.json": {
        "game": "Honor of Kings",
        "updated_at": "replace-me",
        "source": "local user input",
        "lane_preferences": ["中路", "游走", "对抗路", "发育路"],
        "owned_heroes": ["甄姬", "张良", "王昭君", "后羿", "庄周"],
        "match_statistics": [
            {
                "hero": "甄姬",
                "appearances": 10,
                "win_rate_percent": 60.0,
                "preferred_lanes": ["中路"],
                "confidence": "example",
            }
        ],
    },
    "meta.json": {
        "updated_at": "replace-me",
        "version_label": "local configurable meta data",
        "score_scale": "1-10, higher means stronger default recommendation",
        "heroes": {
            "甄姬": {
                "lanes": ["中路"],
                "meta_score": 8.0,
                "tier": "A",
                "tags": ["团控", "守线", "反冲阵", "法伤"],
                "difficulty": "低",
                "situational": False,
            },
            "张良": {
                "lanes": ["中路"],
                "meta_score": 8.0,
                "tier": "A",
                "tags": ["压制", "反刺客", "工具人", "法伤"],
                "difficulty": "低",
                "situational": False,
            },
            "王昭君": {
                "lanes": ["中路"],
                "meta_score": 7.8,
                "tier": "A-",
                "tags": ["团控", "分割战场", "守线", "法伤"],
                "difficulty": "中",
                "situational": False,
            },
            "后羿": {
                "lanes": ["发育路"],
                "meta_score": 7.0,
                "tier": "B+",
                "tags": ["持续物伤", "站桩射手"],
                "difficulty": "低",
                "situational": True,
            },
            "庄周": {
                "lanes": ["游走"],
                "meta_score": 7.5,
                "tier": "A-",
                "tags": ["解控", "反控制", "保护"],
                "difficulty": "低",
                "situational": True,
            },
        },
    },
    "matchups.json": {
        "updated_at": "replace-me",
        "principles": [
            "克制优先看机制，而不是只看版本强度。",
            "用户熟练度不足时，不因版本强就硬选。",
        ],
        "enemy_tags_to_counters": {
            "高机动": ["张良", "王昭君", "甄姬"],
            "多突进": ["张良", "王昭君", "甄姬", "庄周"],
            "多控制": ["庄周"],
            "回血续航": ["梦魇之牙", "制裁之刃"],
            "多前排": ["吕布", "貂蝉", "马可波罗"],
        },
        "hero_specific": {},
        "team_needs_to_heroes": {
            "法伤": ["甄姬", "张良", "王昭君"],
            "保护射手": ["庄周"],
            "持续物伤": ["后羿"],
        },
    },
    "builds.json": {
        "updated_at": "replace-me",
        "disclaimer": "Builds are templates and should be adjusted by enemy composition.",
        "common_adjustments": {
            "anti_heal_magic": "敌方高回复：法师或辅助补梦魇之牙。",
            "anti_heal_physical": "物理位面对高回复：补制裁之刃。",
            "need_cleanse": "敌方强控多时，射手/法刺可考虑净化。",
        },
        "heroes": {
            "甄姬": {
                "summoner_spells": ["闪现"],
                "runes": "梦魇、心眼、狩猎/调和。",
                "core_build": ["冷静之靴", "痛苦面具", "凝冰之息", "日暮之流", "博学者之怒", "虚无法杖"],
                "situational": ["辉月保命", "梦魇之牙制裁回血"],
                "playstyle": "先清线再支援，团战站后排打反手控制。",
            },
            "张良": {
                "summoner_spells": ["闪现"],
                "runes": "梦魇、心眼、狩猎/调和。",
                "core_build": ["疾步之靴/冷静之靴", "痛苦面具", "凝冰之息", "日暮之流", "辉月", "虚无法杖"],
                "situational": ["梦魇之牙", "炽热支配者保命"],
                "playstyle": "按住敌方最肥或最高机动核心。",
            },
            "王昭君": {
                "summoner_spells": ["闪现"],
                "runes": "梦魇、心眼、狩猎/调和。",
                "core_build": ["冷静之靴", "痛苦面具", "凝冰之息", "日暮之流", "博学者之怒", "虚无法杖"],
                "situational": ["梦魇之牙", "辉月"],
                "playstyle": "用二技能封路和反手，大招分割战场。",
            },
        },
    },
    "sources.json": {
        "updated_at": "replace-me",
        "sources": [],
        "notes": [
            "Add official patch notes, community tier lists, screenshots, and personal match feedback here.",
            "This file explains where meta and matchup assumptions come from.",
        ],
    },
}

LEGACY_FILE_NAMES = {
    "hero_pool.json": "my_hero_pool.json",
    "sources.json": "version_sources.json",
}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def init_data(overwrite: bool = False) -> list[Path]:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for file_name, content in DEFAULT_JSON_FILES.items():
        path = DATA_ROOT / file_name
        if overwrite or not path.exists():
            write_json(path, content)
            written.append(path)
    feedback_path = DATA_ROOT / "feedback.jsonl"
    if overwrite or not feedback_path.exists():
        feedback_path.write_text("", encoding="utf-8")
        written.append(feedback_path)
    return written


def load_json(name: str) -> dict[str, Any]:
    path = DATA_ROOT / name
    if not path.exists() and name in LEGACY_FILE_NAMES:
        legacy_path = DATA_ROOT / LEGACY_FILE_NAMES[name]
        if legacy_path.exists():
            path = legacy_path
    if not path.exists():
        init_data(overwrite=False)
    return json.loads(path.read_text(encoding="utf-8"))


def split_heroes(text: str) -> list[str]:
    if not text:
        return []
    separators = ["，", ",", "、", "/", " ", "\n"]
    items = [text]
    for separator in separators:
        next_items: list[str] = []
        for item in items:
            next_items.extend(item.split(separator))
        items = next_items
    return [item.strip() for item in items if item.strip()]


def normalized_lane(lane: str) -> str:
    return LANE_ALIASES.get(lane.strip(), lane.strip())


def personal_score(statistics_by_hero: dict[str, dict[str, Any]], hero: str) -> tuple[float, str]:
    statistic = statistics_by_hero.get(hero)
    if not statistic:
        return 0.8, "已拥有但暂无战绩样本"
    appearances = float(statistic.get("appearances", 0))
    win_rate = float(statistic.get("win_rate_percent", 0))
    sample_weight = min(appearances / 10.0, 1.0)
    score = 1.0 + sample_weight * 2.0 + (win_rate - 50.0) / 25.0
    if appearances <= 2:
        note = f"{int(appearances)} 场 {win_rate:.1f}%，样本少"
    else:
        note = f"{int(appearances)} 场 {win_rate:.1f}%"
    return score, note


def infer_enemy_tags(enemy_heroes: list[str]) -> set[str]:
    tags: set[str] = set()
    high_mobility_names = {"镜", "澜", "露娜", "韩信", "马超", "关羽", "不知火舞", "司马懿", "上官婉儿", "孙悟空", "阿轲", "兰陵王"}
    projectile_names = {"嬴政", "干将莫邪", "百里守约", "虞姬", "后羿", "伽罗", "小乔", "墨子", "鲁班七号"}
    control_names = {"王昭君", "甄姬", "墨子", "白起", "牛魔", "廉颇", "张飞", "东皇太一", "张良"}
    sustain_names = {"蔡文姬", "程咬金", "桑启", "扁鹊", "猪八戒"}
    tank_names = {"项羽", "廉颇", "张飞", "牛魔", "白起", "程咬金", "猪八戒"}
    for hero in enemy_heroes:
        if hero in high_mobility_names:
            tags.update(["高机动", "多突进"])
        if hero in projectile_names:
            tags.add("飞行物消耗")
        if hero in control_names:
            tags.add("多控制")
        if hero in sustain_names:
            tags.add("回血续航")
        if hero in tank_names:
            tags.add("多前排")
    if len(enemy_heroes) >= 3 and len(tags) == 0:
        tags.add("未知威胁")
    return tags


def recommend(lane: str, ally_text: str, enemy_text: str, top_k: int) -> list[dict[str, Any]]:
    lane = normalized_lane(lane)
    personal = load_json("hero_pool.json")
    meta = load_json("meta.json")
    matchups = load_json("matchups.json")
    builds = load_json("builds.json")

    owned_heroes = set(personal.get("owned_heroes", []))
    statistics_by_hero = {item["hero"]: item for item in personal.get("match_statistics", [])}
    enemy_heroes = split_heroes(enemy_text)
    enemy_tags = infer_enemy_tags(enemy_heroes)
    counter_heroes = set()
    for tag in enemy_tags:
        counter_heroes.update(matchups.get("enemy_tags_to_counters", {}).get(tag, []))

    recommendations: list[dict[str, Any]] = []
    for hero, hero_meta in meta.get("heroes", {}).items():
        if hero not in owned_heroes:
            continue
        if lane and lane not in hero_meta.get("lanes", []):
            continue
        base_score = float(hero_meta.get("meta_score", 5.0))
        user_score, user_note = personal_score(statistics_by_hero, hero)
        counter_score = 1.5 if hero in counter_heroes else 0.0
        situational_penalty = -0.4 if hero_meta.get("situational") and not counter_score else 0.0
        score = base_score + user_score + counter_score + situational_penalty
        reasons = [f"版本/通用强度 {hero_meta.get('tier')}({base_score:.1f})", f"个人数据：{user_note}"]
        if hero in counter_heroes:
            reasons.append(f"机制上可应对敌方标签：{'、'.join(sorted(enemy_tags))}")
        if hero_meta.get("situational") and hero not in counter_heroes:
            reasons.append("偏阵容英雄，本局没有明显触发克制加分")
        hero_build = builds.get("heroes", {}).get(hero, {})
        recommendations.append({
            "hero": hero,
            "score": round(score, 2),
            "lanes": hero_meta.get("lanes", []),
            "tags": hero_meta.get("tags", []),
            "reasons": reasons,
            "summoner_spells": hero_build.get("summoner_spells", []),
            "core_build": hero_build.get("core_build", []),
            "situational_build": hero_build.get("situational", []),
            "playstyle": hero_build.get("playstyle", ""),
        })

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return recommendations[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Honor of Kings draft recommendation assistant")
    parser.add_argument("--init-data", action="store_true", help="generate local data files and exit")
    parser.add_argument("--overwrite-data", action="store_true", help="overwrite generated data files; use carefully")
    parser.add_argument("--lane", default="", help="目标分路：中路/发育路/游走/对抗路/打野")
    parser.add_argument("--ally", default="", help="我方已选英雄，逗号分隔")
    parser.add_argument("--enemy", default="", help="敌方已选英雄，逗号分隔")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if args.init_data:
        written = init_data(overwrite=args.overwrite_data)
        print(f"data_dir: {DATA_ROOT}")
        for path in written:
            print(f"created: {path}")
        if not written:
            print("data files already exist")
        return

    if not args.lane:
        parser.error("--lane is required unless --init-data is used")

    result = recommend(args.lane, args.ally, args.enemy, args.top_k)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"推荐分路：{normalized_lane(args.lane)}")
    for index, item in enumerate(result, 1):
        print(f"\n{index}. {item['hero']}｜评分 {item['score']}")
        print("   理由：" + "；".join(item["reasons"]))
        if item["summoner_spells"]:
            print("   召唤师技能：" + " / ".join(item["summoner_spells"]))
        if item["core_build"]:
            print("   核心出装：" + " → ".join(item["core_build"]))
        if item["situational_build"]:
            print("   针对调整：" + "；".join(item["situational_build"]))
        if item["playstyle"]:
            print("   打法：" + item["playstyle"])


if __name__ == "__main__":
    main()
