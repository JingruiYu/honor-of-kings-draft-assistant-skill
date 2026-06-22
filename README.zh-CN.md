# Honor of Kings Draft Assistant Skill

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a>
</p>

这是一个面向 **Honor of Kings（王者荣耀）** 的轻量 Agent skill。它可以根据本地可配置数据，辅助用户选英雄、补位、判断阵容克制、调整出装，并记录赛后反馈。

> 官方英文名：**Honor of Kings**。
>
> 本项目默认面向国服《王者荣耀》语境，配置文件使用中文英雄名；如果要适配海外版 Honor of Kings，需要自行维护英雄名映射和版本数据。

## 适用场景

当用户有以下需求时，可以使用这个 skill：

- 开局 BP / 选人时，想快速决定拿什么英雄；
- 需要根据我方和敌方已选英雄补某个分路；
- 想询问出装、铭文、召唤师技能或打法调整；
- 想记录赛后胜负、英雄、分路、KDA、出装和反馈；
- 想初始化或更新自己的英雄池与历史战绩数据。

这个 skill 主要面向中文游戏对话，但仓库文档提供中英文两个版本。

## 快速开始

```bash
python3 scripts/recommend.py --init-data
python3 scripts/recommend.py \
  --lane 中路 \
  --ally '孙策,后羿,牛魔' \
  --enemy '镜,王昭君,张飞' \
  --top-k 3
```

默认情况下，运行数据会生成在 `data/` 目录。如果你希望把数据放到其他位置，可以设置：

```bash
export HOK_ASSISTANT_DATA_DIR=/path/to/my/hok-data
python3 scripts/recommend.py --init-data
```

## 项目结构

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

## 运行数据

`templates/data/` 是公开的初始模板，会提交到仓库里，用来说明配置文件应该长什么样。

`data/` 是本地运行时数据。首次运行下面命令时，会从 `templates/data/` 复制生成：

```bash
python3 scripts/recommend.py --init-data
```

本地会生成这些文件：

- `data/hero_pool.json`：拥有英雄、偏好分路、可选历史战绩；
- `data/meta.json`：版本强度、英雄分路、标签、操作难度和情境标记；
- `data/matchups.json`：敌方阵容标签、克制关系和阵容需求；
- `data/builds.json`：召唤师技能、铭文、核心出装、针对性装备和打法；
- `data/sources.json`：版本、强度、克制关系等信息来源说明；
- `data/feedback.jsonl`：赛后反馈记录，一行一个 JSON。

`data/` 不应该提交到公开仓库，因为里面可能包含个人战绩和英雄池数据。

## 输入方式

脚本本身只处理结构化 JSON 文件和命令行参数。

用户可以通过 Agent 提供两类输入：

- 文字：英雄池、分路、阵容、胜率、战绩和出装；
- 图片 / 截图：仅当当前 Agent 和 LLM 支持视觉输入时可用。

如果支持截图，Agent 可以从英雄池、战绩、出装或版本榜单截图里识别英雄、分路、胜率和出装，再更新本地 `data/` 文件。如果某个字段不确定，应保留为不确定，而不是强行猜测。

## 推荐逻辑

推荐脚本是一个可解释的规则打分器：

1. 先按目标分路和已拥有英雄过滤候选。
2. 根据出场次数、胜率和样本量估算个人熟练度。
3. 从 `meta.json` 读取版本强度和英雄标签。
4. 根据敌方英雄推断阵容标签，例如高机动、多控制、回血、多前排、消耗或强开。
5. 根据 `matchups.json` 中的克制关系加分。
6. 从 `builds.json` 附加出装和打法建议。

它不是机器学习模型，也不应该被表达成“绝对最优选择”。它的优势是逻辑透明、数据可改，并且可以用用户反馈持续校准。

## 示例输入

选人阶段：

```text
我补中路。我方已选孙策、后羿、牛魔；对面镜、王昭君、张飞。推荐我拿什么？
```

对局中出装调整：

```text
我这局甄姬，对面有蔡文姬和程咬金，还要不要出梦魇？后面怎么打？
```

赛后反馈：

```text
这局我中路甄姬赢了，3/1/13，出了冷静鞋、面具、凝冰、日暮、梦魇。帮我记录。
```

## Skill 使用方式

把这个仓库 clone 到支持 `SKILL.md` 的 Agent skills 目录后，Agent 可以根据 `SKILL.md` 判断什么时候使用这个 skill，以及如何更新本地数据文件。

你也可以不通过 Agent，直接使用命令行脚本。

## 相关文章

- [我用 Agent 打王者后，居然没怎么输过了](https://zhuanlan.zhihu.com/p/2052139141006151933)：这篇文章记录了我为什么做这个 skill，以及一个游戏辅助 skill 如何体现个人 Agent 系统的价值。

## License

MIT License.
