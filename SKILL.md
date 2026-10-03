---
name: script-to-storyboard-table
description: 将剧本、对白稿、小说改编稿、导演计划或已有分镜转换、检查并修复为可拍、可剪、可供 AI 视频流水线读取的结构化分镜表。用于剧本转分镜、shot list、短剧/漫剧拆镜、导演预规划、战斗/动作场 Combat Plan、Beat→Shot 可追溯拆解、镜头时长与跨语言对白重算、人物调度、首尾状态、跨镜衔接、Generation Segment、连续性诊断，以及 MiniMax H3 等下游视频模型交接。默认忠实于原剧情；不负责擅自改剧情、生成最终视频 Prompt、图片或视频。
compatibility: Portable Agent Skill. Works in ChatGPT/Codex/Claude-style agents that can read SKILL.md and local resources. Validator uses Python 3 standard library only.
metadata:
  author: zdingwl
  version: "3.1.0"
  updated: "2026-10-03"
---

# 剧本转分镜表 v3

把“文学/剧本语言”编译成“导演、剪辑、关键帧和 AI 视频生成都能继续执行的镜头数据”。

核心原则：

```text
剧情事实
→ 导演预规划
→ Combat Plan（战斗场）
→ Beat
→ Atomic Shot
→ Continuity Handoff
→ Timing
→ Generation Segment（需要时）
→ Audit
```

不要直接从一段剧本文字跳到一张看似完整的镜头表。单镜正确但相邻镜无法连接，仍然是不合格分镜。

## 0. 职责边界

### 本 Skill 负责

- 解析 Scene、人物、地点、时间、道具、对白、旁白、声音和已知资产。
- 若没有上游导演计划，先做**导演预规划**，明确场次职责、转折、blocking、轴线、coverage 和节奏。
- 将原稿拆成可追溯 Narrative Beats。
- 将 Beat 编译为可拍、可剪、可生成的 Atomic Shots。
- 为每镜记录 `start_state → action → end_state`。
- 为相邻镜记录 `handoff_from_previous`，明确为什么这里能切。
- 规划 shot duration、累计时间码和对白容量。
- 当目标语言发生变化时，按目标文本/目标音频**重新计算对白时长**，禁止沿用源语言时长。
- 维护人物、道具、动作、空间、视线、光线、声音和屏幕方向连续性。
- 需要 AI 视频生产时，将连续 shots 分组为 Generation Segments。
- 输出 Markdown 分镜表；需要机器接力时同时输出 `storyboard.json`。
- 运行确定性 validator，并报告 error / warning。

### 本 Skill 不负责

- 未经授权改剧情因果、角色决定、核心台词事实、结局或反转。
- 为缺失设定凭空发明角色外观、服装、世界观或资产细节。
- 生成角色图、场景图、分镜图或视频。
- 编写 MiniMax H3 / Seedance / Kling / Veo 等最终模型 Prompt。
- 用“电影感、高级感、宿命感”替代具体镜头设计。
- 为了满足模型时长限制，把不连续的剧情硬塞进同一个 Segment。

如果用户只要求“剧本转分镜表”，不要自动扩展成整套视频生产。

## 1. 默认模式

| 模式 | 允许 | 禁止 |
|---|---|---|
| `faithful` | 拆 Beat、导演化、视觉化、拆镜、必要补全 | 改核心剧情和事实 |
| `visual` | 在 faithful 上增强构图、动作、反应、声音和环境反馈 | 新增剧情事件 |
| `pacing` | 拆合表现镜头、调整镜头时长、重排纯表现性 coverage | 改核心因果与人物决定 |
| `story` | 按用户明确授权范围改剧情 | 超出授权范围改写 |

未指定时使用 `faithful`，无需追问。

## 2. 按需读取

### 正常剧本转分镜

先读：

1. `references/director-plan.md`
2. `references/storyboard-method.md`

需要结构化交付时再读：

3. `references/schema.md`
4. `assets/storyboard-template.md`

### 战斗 / 打戏 / 多人动作场

读取：

5. `references/combat-planning.md`

### 有对白、配音或翻译时

读取：

6. `references/dialogue-timing.md`

### 目标明确为 MiniMax H3 时

读取：

7. `references/h3-handoff.md`

### 需要核对研究依据时

读取：

8. `references/sources.md`

需要机器校验时：

```bash
python scripts/validate_storyboard.py storyboard.json
```

严格模式：

```bash
python scripts/validate_storyboard.py storyboard.json --strict
```

## 3. 输入处理

至少接受一种输入：

- 完整剧本或单场剧本；
- 对白稿 + 动作；
- 小说/故事段落，并明确要求忠实分镜；
- 已有导演计划；
- 已有分镜表 / storyboard.json，需要诊断或修复。

有则读取，不强制索取：

- 上游导演计划；
- 角色 / 场景 / 道具资产清单与稳定 ID；
- 前一场尾帧或已批准镜头；
- 目标总时长、画幅、平台、目标语言；
- 目标视频模型与用户提供的当前模型限制。

缺失但不阻止第一版时，使用 `unknown` / `pending` / `assumed`，不要停下询问。

### 上游优先级

若输入同时存在多个版本，按以下事实层处理：

```text
用户当前明确指令
> 已批准导演计划/剧本
> 已批准资产事实
> 已批准前序分镜状态
> 未确认草稿
> 模型自行补全
```

后层不得覆盖前层。

## 4. 必须先做导演预规划

如果用户已提供导演计划，读取并尊重；不要重新发明。

如果没有，先对每个 Scene 建立最小 Director Plan：

- `dramatic_job`：这场戏必须完成什么；
- `turn`：本场真正发生变化的点；
- `entry_state / exit_state`；
- `blocking_plan`：人物初始关系、关键移动、视线；
- `axis_plan`：180°轴线或有意越轴方案；
- `coverage_obligations`：必须看清的动作、反应、证据、空间；
- `visual_strategy`：本场主要视觉逻辑，不是风格形容词；
- `pacing`：held / neutral / compressed；
- `hook_role`：none / setup / escalation / end_hook。

导演预规划细则见 `references/director-plan.md`。

### 4.1 战斗场必须增加 Combat Plan

如果 Scene 属于连续战斗、打戏、持械对抗或多人混战，在 Director Plan 中设置：

```json
"sequence_type": "combat"
```

并在拆普通 Beat / Shot 前建立 `combat_plan`，至少明确：

- `combat_goal`：这场战斗在剧情上必须完成什么；
- `participants`：参与者目标、起始区域、状态和关键道具；
- `arena`：空间 zones、出入口、障碍/高低差和主要移动路径；
- `combat_beats`：真正改变战斗状态的节点，而不是逐拳逐脚；
- `advantage_before / advantage_after`：每个 Combat Beat 的权力变化；
- `zone_before / zone_after`：空间移动；
- `range_before / range_after`：仅用于镜头连续性的 far / mid / close / grapple；
- `rhythm_plan`：交锋、停顿、反转、升级、决定性节点、after-math；
- `camera_strategy`：camera 如何服务 choreography，而不是反过来；
- `continuity_priorities`：方向、距离、动作相位、道具、伤势和多人位置。

战斗场正式链路：

```text
Director Plan
→ Combat Plan
→ Combat Beat
→ Action Phase
→ Atomic Shot
→ Combat Handoff
→ Aftermath
```

关键原则：

- Combat Beat 是一次状态变化，不是“一拳”；
- 重要冲击至少要能读到“来向/预备 → 接触感或暗示 → 结果/反应”；
- 优势变化必须有可见原因；
- 多人混战先分 primary exchange / secondary threat / theaters；
- 复杂 choreography 优先简化 camera；
- AI 视频中单个 Segment 通常只承载 1–2 个清楚 Combat Beats；
- 真实拍摄安全、动作技术和武器操作必须交给专业动作/特技团队，本 Skill 只规划银幕连续性。

完整规则见 `references/combat-planning.md`。

## 5. 先拆 Beat，再拆 Shot

Beat 是一次有意义的状态变化，不是句号或台词行。

常见 Beat：

- 信息获得 / 暴露；
- 目标变化；
- 权力变化；
- 动作阶段完成；
- 道具或空间状态改变；
- 可观察的情绪阈值变化；
- 问题被提出、延期、兑现或替换。

稳定编号：

```text
E01-S03-B01
E01-S03-B02
```

每个 Shot 必须通过 `source_beats` 认领一个或多个**连续 Beat**。

默认质量门：

- `must_preserve=true` Beat 不得漏；
- 不得无理由重复认领；
- Shot 不得跨 Scene 认领；
- Beat 顺序不得倒置，除非有明确非线性结构；
- coverage 镜头重复同一 Beat 时写 `coverage_exception`。

## 6. Atomic Shot

一个正常 Shot 应同时满足：

1. 一个连续时空；
2. 一个主导景别；
3. 一个主要注意力中心；
4. 一个主要视觉行动/信息任务；
5. 一个主要摄影机运动，固定也算明确选择；
6. 明确 `start_state → action → end_state`；
7. 时长能容纳动作、对白和必要停顿；
8. 相邻镜存在可解释的切点。

出现以下情况优先拆镜：

- 文本实际隐藏了“切到 / 再看 / 同时 / 另一边”；
- 注意力中心从 A 换到 B；
- 需要独立读取小道具、屏幕、伤口、手部动作；
- 重台词后的听者反应重要；
- 同镜包含复杂动作 + 多人精准口型 + 小道具 + 复杂运镜；
- 跨地点、跨时间、跨服装/伤势/光线状态；
- 镜头内部需要两个互相冲突的构图目标。

允许长镜头，但要标记 `long_take_exception`，写明人物路线、摄影机路线、关键节点和拆镜备用方案。

## 7. 每次切镜必须有理由

除第一镜外，每个 Shot 写：

```json
"handoff_from_previous": {
  "from_shot_id": "E01-S01-001",
  "type": "match_on_action",
  "reason": "在手即将触碰门把时切入手部近景"
}
```

推荐 `type`：

- `direct`
- `match_on_action`
- `eyeline`
- `reaction`
- `insert`
- `insert_return`
- `sound_bridge`
- `reframe`
- `motivated_jump`
- `time_jump`
- `scene_cut`

如果说不清“为什么这里切、下一镜从哪里接”，优先认为缺镜、错镜或切点不成立。

## 8. 时间与对白

镜头时长由三件事共同决定：

```text
视觉信息读取时间
+ 动作完成时间
+ 对白/旁白/声音容量
```

启发式只作初稿：

- 冲击 insert：约 1–3 秒；
- 单一动作/反应：约 2–4 秒；
- 对话近景/中景：约 3–6 秒；
- 空间建立/连续动作：约 4–8 秒。

不要把这些数字当模型硬限制。

### 跨语言硬规则

如果对白从一种语言翻成另一种语言：

- 原 shot duration **立即失效为可复用依据**；
- 必须根据目标语言最终台词重新估算，最好使用目标 TTS/实录测量；
- `timing_source` 不得继续写 `inherited_source`；
- 如目标文本尚未最终锁定，标记 `estimated_target_text`；
- 翻译发生后，重新做 shot duration、scene runtime、segment duration 和总时长检查。

详细规则见 `references/dialogue-timing.md`。

## 9. Blocking 先于 Camera

每镜先确定：

- 人物在哪里；
- 朝哪边；
- 看谁/看什么；
- 怎么移动；
- 道具在哪只手；
- 镜头结束时停在哪里。

之后才决定 shot size、angle、movement。

镜头变化应服务以下至少一种：

- 新信息；
- 权力/关系变化；
- 注意力转移；
- 动作连续；
- 情绪落点；
- 空间重新建立；
- 节奏需要。

不是为了“镜头丰富”而变化。

## 10. 连续性合同

每镜维护：

- 人物左右/前后位置；
- 面朝、视线；
- 姿势和动作相位；
- 服装、发型、伤势、污渍；
- 道具位置、持有人、持有手、状态；
- 门窗、车辆、大型物体状态；
- 时间、天气、光线；
- 180°轴线；
- 屏幕运动方向；
- 对白、VO、音乐、环境声、J/L cut。

相邻镜至少检查：

```text
previous.end_state
→ handoff_from_previous
→ current.start_state
```

只检查首尾状态而不检查“中间如何切过去”，仍然不够。

## 11. Coverage 与缺镜审计

每场对照 Director Plan 的 `coverage_obligations` 检查：

- 空间第一次出现时是否足够建立；
- 关键证据是否读得清；
- 关键动作是否缺阶段；
- 重台词是否需要听者反应；
- 位置改变是否有过渡；
- 轴线变化是否有重建或有意越轴；
- insert 后是否知道回到哪里；
- 结果镜是否缺原因镜，或原因镜是否缺结果镜。

不要为了“保险”无限增加 coverage；每个镜头都应有 `purpose` 和 `cut_reason`。

## 12. 钩子只做“视觉兑现”，不擅改剧情

短剧/漫剧如存在开场或结尾钩子，检查它是否被镜头语言准确保留。

优先识别：

- 信息缺口；
- 未知威胁逼近；
- 秘密即将暴露；
- 选择尚未作出；
- 认知反转刚发生但后果未知；
- 倒计时/行动未完成。

“结果已经发生且没有新的未决问题”通常只是结果，不应被误标为强钩子。

本 Skill 可以调整镜头呈现，但在 `faithful` 模式下不能凭空增加悬念事实。

## 13. Asset 使用

有资产清单时使用稳定 ID：

```text
C01 角色
S01 场景
P01 道具
```

只引用实际需要的资产。

若没有资产表：

- 可以列出 `asset_requirements`；
- 只记录“需要什么资产/状态”；
- 不替资产 Skill 发明具体脸、服装、材质、色彩设计；
- 用 `pending` 标记待绑定项。

## 14. Generation Segment

只有下游需要“一次 AI 视频生成任务”时使用。

**v3 单一事实源：**

```text
Scene.shots = 唯一正式 Shot 数据
GenerationSegment.shot_ids = 只引用 Shot ID
```

不要把完整 Shot 再复制一份到 Segment 里。

Segment 规则：

- 不跨 Scene；
- `shot_ids` 按剪辑顺序；
- total duration = 引用 shots 的 duration 之和；
- 同一环境、时间、主要人物和参考资产关系尽量稳定；
- 高风险交互、状态突变或关键帧边界可主动断 Segment；
- 模型硬限制只来自当前官方资料或用户给定资料。

Segment 内模型时间线从 `shot_ids + duration_seconds` **派生**，不维护第二份手写 cut 时间码。

## 15. 时间码唯一语义

v3 中：

- `Shot.timecode_in / timecode_out` = 成片/集内累计时间；
- Segment 本地 cut 时间从该 Segment 的 `shot_ids` 顺序和 Shot 时长推导；
- 不把 Segment 本地时间和成片全局时间混在同一个字段。

这样可避免“分镜表显示 00:32，但 H3 Prompt 需要 0.00 秒起算”的歧义。

## 16. 标准输出

默认 Markdown 主表至少包含：

| 字段 | 作用 |
|---|---|
| 镜号 | 稳定 ID |
| 生成段 | 可空 |
| 场次 | Scene |
| 时间码 | 成片累计 |
| 时长 | 秒 |
| 原剧本节拍 | `source_beats` |
| 镜头职责 | `purpose` |
| 景别/角度 | framing |
| 运镜 | camera |
| 画面与构图 | composition |
| 人物/调度 | blocking |
| 动作/表演 | action/performance |
| 台词/旁白 | 含目标语言 timing |
| 声音 | ambience/SFX/bridge |
| 资产 | C/S/P |
| 首帧状态 | `start_state` |
| 尾帧状态 | `end_state` |
| 衔接合同 | `handoff_from_previous` |
| 连续性/风险 | notes + risk |

模板见 `assets/storyboard-template.md`。

## 17. 机器 JSON

需要下游自动化时输出 `storyboard.json`。

v3 规则：

- `scene.shots` 是 Shot 唯一事实源；
- Segment 只存 `shot_ids`；
- Dialogue 行显式存 `language`、`timing_seconds`、`timing_source`；
- 非第一镜存 `handoff_from_previous`；
- Scene 存 `director_plan`；
- 模型 profile 带 `verified_at`。

完整字段见 `references/schema.md`。

## 18. 增量修改

用户说“只改第 6、7 镜”时：

1. 冻结其余已批准内容；
2. 读取第 5–8 镜；
3. 只修改 6、7；
4. 若连续性受牵连，只最小修改相邻镜的 handoff/状态字段；
5. 不重排未受影响 ID；
6. 不偷偷优化其他镜；
7. 重新计算受影响后的时间码、Scene runtime 和 Segment runtime。

## 19. 交付前质量门

### A. 剧情保真

- must-preserve Beat 全覆盖；
- 无无授权增删；
- 核心台词事实、关系、道具事实不漂移。

### B. Director Plan

- 每场有 dramatic job 与 turn；
- blocking / axis / coverage obligations 已明确；
- Shot 设计能追溯到场次任务。

### B2. Combat Plan（战斗场）

- `sequence_type=combat` 时必须有 Combat Plan；
- arena zones、参与者和 Combat Beats 已建立；
- 优势变化、空间移动、range 与 action phase 可连续；
- 关键冲击有前因与结果，不靠动作跳帧；
- 多人混战有明确主要交锋或 theater；
- 武器/关键道具、伤势与 aftermath 状态连续；
- AI Segment 没有同时承载过多 Combat Beats。

### C. 镜头可执行

- 每镜只有一个主要视觉任务；
- 无隐藏剪辑；
- 动作和对白能在时长内完成；
- `purpose` 和 `cut_reason` 成立。

### D. 跨镜连续

- `end_state → handoff → start_state` 成立；
- 屏幕方向、视线、动作相位、道具、服装、环境连续；
- 30°/180°规则没有无意制造跳切或空间混乱；
- insert/cutaway 能安全返回主动作。

### E. Timing

- 时间码连续；
- Scene/Episode 时长可解释；
- 对白 timing 不超过镜头容量；
- 目标语言变化后已重新计时；
- Segment 时长由 shots 派生，没有第二份冲突时间线。

### F. AI 生产（若适用）

- Segment 不跨 Scene；
- reference 角色明确；
- 模型约束核对日期可见；
- 复杂多人/小道具/口型/运镜没有同镜过载；
- 高风险镜头有 fallback。

### G. Hook（若适用）

- 钩子来自原剧情或授权；
- 没把“已经给出结果”误当“未决问题”；
- 最后一镜没有提前把下一拍的信息泄完。

## 20. Validator

生成 JSON 后运行：

```bash
python scripts/validate_storyboard.py storyboard.json
```

当前 validator 检查：

- schema/version；
- 全局 ID 重复；
- Beat 覆盖与顺序；
- canonical Shot / Segment 引用关系；
- 时长与时间码；
- handoff 结构；
- 对白 timing 与镜头容量；
- 跨语言 stale timing；
- Segment duration 与 shot_ids 求和；
- H3 当前官方范围和参考素材数量；
- H3 profile 核对日期；
- 资产引用；
- 常见缺字段 warning。

修复 error；warning 可以保留，但在交付摘要解释。

## 21. 最终交付顺序

1. 分镜摘要：场次、镜数、总时长、Segment 数。
2. Director Plan 摘要。
3. Combat Plan 摘要（有战斗场时）。
4. 角色/场景/道具索引或待绑定资产。
5. Beat 清单。
6. 完整分镜表。
7. 节奏/钩子节点。
8. 连续性、对白时长、战斗连续性和高风险说明。
9. 若需要自动化：`storyboard.json` + validator 结果。

不要在结尾自动追加视频 Prompt；除非用户明确要求进入下一阶段。
