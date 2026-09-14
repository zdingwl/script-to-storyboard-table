# script-to-storyboard-table

将剧本、对白稿、小说改编稿转换为 **可拍、可剪、可供 AI 视频流水线继续读取的结构化分镜表**。

这个仓库本身就是一个 Agent Skill，核心入口是根目录 `SKILL.md`。

## 适合做什么

- 剧本 → 分镜表 / Shot List
- 短剧、漫剧、AI 动漫拆镜
- Narrative Beat → Shot 可追溯拆解
- 景别、角度、运镜、构图、blocking
- 对话正反打、反应镜、insert、动作连续剪辑
- `start_state / end_state` 连续性管理
- 角色 / 场景 / 道具资产 ID 引用
- Generation Segment 规划
- MiniMax H3 等下游 AI 视频模型交接
- 分镜 JSON 自动校验

## 不做什么

- 不擅自改剧情
- 不生成角色图 / 场景图 / 分镜图
- 不生成最终视频
- 不把 MiniMax H3 / Seedance / Kling 等最终 Prompt 强塞进分镜阶段

推荐流水线：

```text
剧本
  ↓
script-to-storyboard-table
  ↓
storyboard.md + storyboard.json
  ↓
分镜关键帧 / 图片 Prompt Skill
  ↓
视频 Prompt Skill（例如官方 h3-prompt-writing）
  ↓
视频生成
```

## Skill 结构

```text
script-to-storyboard-table/
├── SKILL.md
├── README.md
├── references/
│   ├── storyboard-method.md
│   ├── schema.md
│   ├── h3-handoff.md
│   └── sources.md
├── assets/
│   └── storyboard-template.md
└── scripts/
    └── validate_storyboard.py
```

## 核心设计

### 1. 先拆 Beat，再拆 Shot

每个 Shot 必须认领原剧本中的连续剧情 Beat，避免：

- 漏剧情
- 重复剧情
- AI 自己加戏
- 镜头顺序错乱

### 2. Generation Segment 与 Shot 分开

```text
Scene
└── Generation Segment  ← AI 视频一次生成任务的规划单位
    ├── Shot 1           ← 最终剪辑镜头
    ├── Shot 2
    └── Shot 3
```

因此“一个 12 秒 H3 生成段内部有 3 个 cut”和“3 个独立生成视频”不会再混为一谈。

### 3. 每镜有首尾状态

```text
start_state → action → end_state
```

相邻镜检查：

```text
previous.end_state → current.start_state
```

用来解决 AI 漫剧最常见的：人物突然换位置、道具换手、动作跳帧、镜头接不上。

### 4. 分镜与模型 Prompt 解耦

模型硬限制更新很快，所以：

- 通用分镜方法写在 `SKILL.md` / `storyboard-method.md`
- MiniMax H3 当前约束单独写在 `h3-handoff.md`
- 最终 H3 Prompt 交给 MiniMax 官方 `h3-prompt-writing`

以后 H3 Prompt 格式变化时，不需要重写整个分镜 Skill。

## 标准输出

默认输出完整表格：

| 镜号 | 生成段 | 场次 | 时间码 | 时长 | 原剧本节拍 | 景别/角度 | 运镜 | 画面与构图 | 人物/调度 | 动作/表演 | 情绪目的 | 台词/旁白 | 声音 | 场景/道具/资产 | 首帧状态 | 尾帧/衔接 | 连续性/风险 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

模板：`assets/storyboard-template.md`

## JSON 校验

如果下游还要自动生成关键帧、图片 Prompt 或视频 Prompt，建议同时输出 `storyboard.json`。

运行：

```bash
python scripts/validate_storyboard.py storyboard.json
```

严格模式：

```bash
python scripts/validate_storyboard.py storyboard.json --strict
```

当前校验包括：

- ID 重复
- Beat 漏覆盖
- Shot 时长异常
- 时间码与时长不一致
- Segment 声明时长与 shots 求和不一致
- Scene / Segment 归属错误
- MiniMax H3 Segment 4–15 秒范围
- H3 当前参考图片 / 视频 / 音频 / 混合文件数量上限
- reference label 重复
- 缺失 start/end state、景别、运镜等 warning

## MiniMax H3

仓库会为 H3 准备：

```text
剧情事实
+ Shot 结构
+ cut 时间
+ Generation Segment
+ 角色/场景/道具资产
+ start/end state
+ generation_mode hint
```

最终 H3 Prompt 建议继续使用 MiniMax 官方 Skill：

```text
https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing
```

详见：`references/h3-handoff.md`。

## 资料来源

本 Skill 依据 2026-09-15 前后可核对资料重新整理，主要参考：

- Agent Skills Specification
- MiniMax H3 官方仓库与 `h3-prompt-writing`
- StudioBinder Shot List / Storyboard Blocking
- Boords Script-to-Storyboard / Shot List / Camera Guide
- `eternityspring/shuohao-skills` 的 beat ownership / generation segment 思路
- `seaartpublic/skills` storyboard-prompt-assistant
- `script-to-shootable-storyboard` 的 atomic shot / continuity 思路

完整链接和采用范围见：`references/sources.md`。

## 版本

当前：`2.0.0` — 2026-09-15
