# Honor of Kings Draft Assistant Skill

一个面向《王者荣耀》（官方英文名 **Honor of Kings**）的 Agent skill：根据你的英雄池、历史战绩、双方阵容、版本强度和克制关系，快速给出选英雄、出装和打法建议。

> 中文为主；English summary is included below.

## 适用场景

- 开局 BP / 选人时：告诉 Agent 你要补哪个位置、双方已选英雄，快速推荐首选和备选。
- 对局中：询问针对敌方阵容的出装、召唤师技能、打法重点。
- 赛后：记录胜负、英雄、分路、战绩和实际出装，用于后续推荐校准。
- 第一次使用：可以用文字提供英雄池、常用英雄、历史战绩、胜率、分路偏好；如果你使用的 Agent / LLM 支持视觉输入，也可以直接提供截图。Agent 负责整理成结构化数据。

## 快速开始

```bash
python3 scripts/recommend.py --init-data
python3 scripts/recommend.py \
  --lane 中路 \
  --ally '孙策,后羿,牛魔' \
  --enemy '镜,王昭君,张飞' \
  --top-k 3
```

如果不想把数据放在仓库目录下，可以指定：

```bash
export HOK_ASSISTANT_DATA_DIR=/path/to/my/hok-data
python3 scripts/recommend.py --init-data
```

## Data 目录

`data/` 是本地生成目录，默认不会提交到 Git。首次运行：

```bash
python3 scripts/recommend.py --init-data
```

会生成这些文件：

- `hero_pool.json`：用户英雄池、分路偏好、拥有英雄、历史战绩。
- `meta.json`：版本强度、英雄分路、标签、操作难度。
- `matchups.json`：敌方阵容标签、克制关系、阵容需求。
- `builds.json`：召唤师技能、铭文、核心出装、针对性出装、打法。
- `sources.json`：版本信息、强势英雄、克制关系的数据来源说明。
- `feedback.jsonl`：每次推荐后的实战反馈，一行一个 JSON。

这些文件是配置，不是固定答案。用户可以根据当前赛季、段位、英雄池和实战结果持续更新。

## 数据来源说明

版本强度、强势英雄和克制关系通常来自：

- 官方公告、英雄调整和赛季更新；
- 王者营地、社区榜单、攻略文章、视频和截图；
- 用户自己的历史战绩与胜负反馈；
- 英雄机制常识，例如压制、解控、挡飞行物、反开、真伤、强开团等。

本项目不内置官方实时榜单。建议把当前版本榜单或截图交给 Agent，让 Agent 更新 `meta.json`、`matchups.json` 和 `builds.json`。

## 推荐原理

推荐脚本是一个可解释的规则打分器：

1. 先按目标分路和已拥有英雄过滤候选。
2. 结合你的出场次数、胜率和样本量计算个人熟练度。
3. 读取版本强度和英雄标签，给出基础强度分。
4. 根据敌方英雄推断阵容标签，例如高机动、多控制、回血、多前排。
5. 用克制关系给合适英雄加分。
6. 输出推荐理由、召唤师技能、核心出装和一句话打法。

它不是机器学习模型，也不会替代实时判断；优势是透明、可修改、可被个人数据持续校准。

## 文字与截图输入说明

本 skill 的脚本本身只处理结构化 JSON 和命令行参数。图片 / 截图识别能力取决于你所使用的 Agent 和 LLM 是否支持视觉输入。

- 如果支持图片：可以发英雄池、战绩、出装或版本榜单截图，让 Agent 先识别，再更新本地 `data/`。
- 如果不支持图片：请用文字描述英雄、胜率、分路、阵容和战绩。

## 对局输入示例

选人阶段：

```text
我补中路。我方已选孙策、后羿、牛魔；对面镜、王昭君、张飞。推荐我拿什么？
```

对局中：

```text
我这局甄姬，对面有蔡文姬和程咬金，还要不要出梦魇？后面怎么打？
```

赛后反馈：

```text
这局我中路甄姬赢了，3/1/13，出了冷静鞋、面具、凝冰、日暮、梦魇。帮我记录。
```

## Skill 使用方式

把本仓库 clone 到支持 `SKILL.md` 的 Agent skills 目录后，Agent 会根据 `SKILL.md` 了解什么时候使用本 skill。推荐脚本可以被 Agent 调用，也可以直接命令行运行。

## English summary

Honor of Kings Draft Assistant Skill is a lightweight, configurable Agent skill for hero draft, matchup reasoning, build suggestions, and post-match feedback. It uses local JSON data for hero pool, version meta, matchups, builds, and user feedback. The generated `data/` directory is local-only and should be customized by each user.
