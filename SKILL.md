---
name: script-to-storyboard-table
description: 将剧本、对白稿、小说改编稿、导演计划或已有分镜转换、检查并修复为可拍、可剪、可供 AI 视频流水线读取的结构化分镜表。用于剧本锁定后的导演预演：Script Lock、Sequence Type Router、各种场型专用 Sequence Plan、Visual Bible/Asset State 接口、Blocking、Coverage、Storyboard、Animatic/Previs Gate、Shot Production Packet、连续性诊断，以及 MiniMax H3 等下游视频模型交接。默认忠实于原剧情；不负责擅自改剧情、生成最终视频 Prompt、图片或视频。
compatibility: Portable Agent Skill. Works in ChatGPT/Codex/Claude-style agents that can read SKILL.md and local resources. Validator uses Python 3 standard library only.
metadata:
  author: zdingwl
  version: "3.3.0"
  updated: "2026-10-03"
---

# AI Director & Cinematic Previsualization v3.3

把“文学/剧本语言”编译成“导演、剪辑、关键帧和 AI 视频生成都能继续执行的镜头数据”。

核心原则：

```text
Script Lock / Story Contract
→ Sequence Type Router
→ Director Plan
→ Type-specific Sequence Plan / Combat Plan
→ Visual Bible Contract
→ Asset State Matrix
→ Geography / Blocking
→ Beat / Coverage
→ Atomic Shot
→ Continuity Handoff
→ Storyboard
→ Animatic / Previs Gate
→ AI Video Shot Production Packet
```

最终 AI Video Generation / Assembly Edit / Sound / VFX / Color 属于下游生产，不由本 Skill 直接执行。

不要直接从一段剧本文字跳到一张看似完整的镜头表。单镜正确但相邻镜无法连接，仍然是不合格分镜。

## 0. 职责边界

### 本 Skill 负责

- 解析 Scene、人物、地点、时间、道具、对白、旁白、声音和已知资产。
- 先建立或读取 **Script Lock / Story Contract**，冻结必须保留的剧情事实。
- 若没有上游导演计划，先做**导演预规划**，明确 POV、信息控制、情绪曲线、权力变化、geography、blocking、镜头/灯光/剪辑/声音策略。
- 将原稿拆成可追溯 Narrative Beats。
- 将 Beat 编译为可拍、可剪、可生成的 Atomic Shots。
- 为每镜记录 `start_state → action → end_state`。
- 为相邻镜记录 `handoff_from_previous`，明确为什么这里能切。
- 规划 shot duration、累计时间码和对白容量。
- 当目标语言发生变化时，按目标文本/目标音频**重新计算对白时长**，禁止沿用源语言时长。
- 读取或声明 Visual Bible 锁定项，并通过 Asset State Matrix 维护人物、服装、伤势、湿度、道具、场景损坏、时间等连续状态。
- 维护人物、道具、动作、空间、视线、光线、声音和屏幕方向连续性。
- 需要 AI 视频生产时，将连续 shots 分组为 Generation Segments。
- 输出 Markdown 分镜表；需要机器接力时同时输出 `storyboard.json`。
- 在 cinematic previs 工作流中输出 `animatic-plan.json` / `previs-report.md` 规划，并在通过 Previs Gate 后生成模型无关的 Shot Production Packets。
- 运行确定性 validator，并报告 error / warning。

### 本 Skill 不负责

- 未经授权改剧情因果、角色决定、核心台词事实、结局或反转。
- 为缺失设定凭空发明角色外观、服装、世界观或资产细节。
- 直接生成角色资产、场景资产或最终视频；它只定义视觉/资产/镜头需求与交接合同。
- 直接承担 MiniMax H3 / Seedance / Kling / Veo 的最终 Prompt 编译；Shot Packet 由下游模型专用 Skill 编译。
- 用“电影感、高级感、宿命感”替代具体镜头设计。
- 为了满足模型时长限制，把不连续的剧情硬塞进同一个 Segment。

如果用户只要求“剧本转分镜表”，可以使用轻量 storyboard 流程；用户要求电影工业感、导演规划、previs、整套视频前期时，使用 cinematic_previs 工作流。

## 1. 默认模式

| 模式 | 允许 | 禁止 |
|---|---|---|
| `faithful` | 拆 Beat、导演化、视觉化、拆镜、必要补全 | 改核心剧情和事实 |
| `visual` | 在 faithful 上增强构图、动作、反应、声音和环境反馈 | 新增剧情事件 |
| `pacing` | 拆合表现镜头、调整镜头时长、重排纯表现性 coverage | 改核心因果与人物决定 |
| `story` | 按用户明确授权范围改剧情 | 超出授权范围改写 |

未指定时使用 `faithful`，无需追问。

### 工作流 Profile

- `storyboard`：Director / Sequence / Shot / Continuity 的轻量分镜流程。
- `cinematic_previs`：增加 Script Lock、Visual Bible Contract、Asset State Matrix、Animatic/Previs Gate 和 Shot Production Packet。

当用户明确追求“电影工业感、previs、正式 AI 视频生产、整套导演系统”时，优先使用 `cinematic_previs`。

## 2. 按需读取

### 正常剧本转分镜

先读：

1. `references/sequence-router.md`
2. `references/director-plan.md`
3. `references/storyboard-method.md`

### cinematic_previs 工作流

额外读取：

- `references/previs-pipeline.md`
- `references/script-lock-contract.md`
- `references/visual-bible-contract.md`
- `references/asset-state-matrix.md`
- `references/animatic-previs.md`
- `references/shot-production-packet.md`
- 需要粗剪反馈时读取 `references/post-generation-loop.md`

Router 根据 `sequence_type` 按需读取：

- 对白 / 谈判 / 情感：`references/dialogue-emotion-planning.md`
- 调查 / 悬疑 / 恐怖 / 潜入：`references/suspense-investigation-planning.md`
- 追逐 / 载具 / 环境危险 / 救援：`references/chase-action-planning.md`
- 战斗 / 打戏 / 多人动作：`references/combat-planning.md`
- 灾难 / 群戏 / 喜剧 / 蒙太奇 / 表演 / 世界揭示 / 过渡：`references/tempo-spectacle-planning.md`

需要结构化交付时再读：

4. `references/schema.md`
5. `assets/storyboard-template.md`

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

## 3.5 Script Lock / Story Contract

进入导演规划前，先确认每个 Scene：

- objective；
- obstacle；
- escalation；
- information release；
- emotional start/end；
- irreversible change；
- must-preserve facts；
- authorized flex。

上游剧本已经批准时只抽取，不改写。完整结构见 `references/script-lock-contract.md`。

## 4. 必须先做 Sequence Type Router

在正式 Director Plan 前，先判断这段戏由哪一种导演机制主导。

核心 `sequence_type`：

- `dialogue`
- `confrontation_negotiation`
- `emotional_intimacy`
- `investigation_reveal`
- `suspense_threat`
- `horror_dread`
- `stealth_infiltration`
- `chase_escape`
- `combat`
- `physical_hazard_rescue`
- `vehicle_action`
- `disaster_survival`
- `crowd_ensemble`
- `comedy`
- `montage_progression`
- `performance_ritual`
- `world_reveal_establishing`
- `transition_travel`
- `other`

混合场型使用主类型 + secondary types；导演机制明显改变时拆 Sequence Block。

完整规则见 `references/sequence-router.md`。

## 5. 必须先做导演预规划

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

### 5.1 非战斗场必须增加 Type-specific Sequence Plan

除 `combat` 外，v3.2 Scene 建立 `sequence_plan`：

- `profile`：与主 `sequence_type` 一致；
- `sequence_goal`：观看层必须完成什么；
- `sequence_beats`：导演阶段，不等于 Narrative Beat；
- `rhythm_plan`；
- `camera_strategy`；
- `continuity_priorities`。

Shot 通过 `sequence_context.sequence_beat_ids` 认领 Sequence Beat，并用 `state_start/state_end` 维护场型状态。

例如：

- chase：route / gap / heading
- suspense：threat_visibility / audience_knowledge
- stealth：detection_state / cover
- negotiation：power_holder / leverage
- emotional：distance / trust / gaze
- montage：progress_stage / chronology

相邻镜没有明确 jump 时，同名状态必须连续。

### 5.2 战斗场必须增加 Combat Plan

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

## 6. 先拆 Beat，再拆 Shot

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

## 7. Atomic Shot

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

## 8. 每次切镜必须有理由

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

## 9. 时间与对白

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

## 10. Blocking 先于 Camera

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

## 11. 连续性合同

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

## 12. Coverage 与缺镜审计

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

## 13. 钩子只做“视觉兑现”，不擅改剧情

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

## 14. Visual Bible 与 Asset State

### Visual Bible

项目已有 Visual Bible / Lookbook 时读取并传播其锁定项，不在每个 Shot 重新发明风格。

Shot 层只记录必要 intent：

- lens intent；
- lighting intent；
- composition intent；
- visual exception。

没有 Visual Bible 时可输出 `visual_bible_requirements`，但不在 faithful 模式凭空决定完整美术风格。

详见 `references/visual-bible-contract.md`。

### Asset State Matrix

连续性必须从 base identity 升级为：

```text
Character × Costume × Physical State × Location × Prop × Time × Damage
```

Shot 优先引用状态 ID，例如 `C01-ST02`、`S01-ST03`，而不是只写 C01 / S01。

详见 `references/asset-state-matrix.md`。

## 15. Asset 使用

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

## 16. Generation Segment

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

## 17. 时间码唯一语义

v3 中：

- `Shot.timecode_in / timecode_out` = 成片/集内累计时间；
- Segment 本地 cut 时间从该 Segment 的 `shot_ids` 顺序和 Shot 时长推导；
- 不把 Segment 本地时间和成片全局时间混在同一个字段。

这样可避免“分镜表显示 00:32，但 H3 Prompt 需要 0.00 秒起算”的歧义。

## 18. 标准输出

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

## 19. 机器 JSON

需要下游自动化时输出 `storyboard.json`。

v3 规则：

- `scene.shots` 是 Shot 唯一事实源；
- Segment 只存 `shot_ids`；
- Dialogue 行显式存 `language`、`timing_seconds`、`timing_source`；
- 非第一镜存 `handoff_from_previous`；
- Scene 存 `director_plan`；
- 模型 profile 带 `verified_at`。

完整字段见 `references/schema.md`。

## 20. 增量修改

用户说“只改第 6、7 镜”时：

1. 冻结其余已批准内容；
2. 读取第 5–8 镜；
3. 只修改 6、7；
4. 若连续性受牵连，只最小修改相邻镜的 handoff/状态字段；
5. 不重排未受影响 ID；
6. 不偷偷优化其他镜；
7. 重新计算受影响后的时间码、Scene runtime 和 Segment runtime。

## 21. 交付前质量门

### A. 剧情保真

- must-preserve Beat 全覆盖；
- 无无授权增删；
- 核心台词事实、关系、道具事实不漂移。

### B. Director Plan

- 每场有 dramatic job 与 turn；
- blocking / axis / coverage obligations 已明确；
- Shot 设计能追溯到场次任务。

### B1. Sequence Plan（非战斗场）

- `sequence_type` 已通过 Router 确定；
- `sequence_plan.profile` 与主类型一致；
- Sequence Beats 能追溯 Narrative Beats；
- 每个 Sequence Beat 至少被一个 Shot 认领；
- 类型核心状态通过 `sequence_context.state_start/state_end` 跨镜连续；
- profile 没有擅自制造剧情事实。

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

### G. Previs Readiness（cinematic_previs）

- Script Lock / Story Contract 已明确；
- Visual Bible 已 locked 或明确 pending；
- Asset State Matrix 足够覆盖本次 Shots；
- Geography / Blocking 可读；
- Storyboard Continuity Audit 通过；
- Animatic/Previs 没有 blocking issue；
- Shot Production Packet 可由 canonical data 派生。

### H. Hook（若适用）

- 钩子来自原剧情或授权；
- 没把“已经给出结果”误当“未决问题”；
- 最后一镜没有提前把下一拍的信息泄完。

## 22. Animatic / Previs Gate

cinematic_previs 工作流中，Storyboard 完成后不要直接进入正式视频生成。

先按 Shot duration 生成 Animatic / Previs timeline 计划，至少包含：

- storyboard panel；
- 临时对白/TTS；
- ambience / SFX；
- temp music（需要时）；
- 简单 camera preview；
- transition；
- black frame / subtitle placeholder。

检查：

- 不看剧本能否理解动作和空间；
- dialogue / reaction timing 是否成立；
- sequence rhythm 是否成立；
- missing shot 是否暴露；
- asset state / screen direction 是否跳变；
- hook/reveal 是否在正确时间发生。

`previs_gate.status != pass` 时返回上游修镜头，不建议开始正式逐镜生成。

详见 `references/animatic-previs.md`。

## 23. AI Video Shot Production Packet

Previs Gate 通过后，每个正式生成 Shot 编译为模型无关 Packet：

- references；
- character / costume / environment / prop states；
- start / end state；
- action / blocking；
- character movement；
- camera position；
- shot size / angle / lens intent / movement；
- foreground / midground / background；
- duration；
- dialogue / sound；
- continuity from / into；
- visual bible reference；
- do-not-change；
- generation constraints；
- risk / fallback。

H3/Kling/Veo 专用 Skill 再把 Packet 编译成各模型 Prompt。

详见 `references/shot-production-packet.md`。

## 22. Validator

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

## 24. 最终交付顺序

1. Script Lock / Story Contract 摘要。
2. Sequence Type / Director Plan 摘要。
3. Type-specific Sequence Plan / Combat Plan 摘要。
4. Visual Bible reference / requirements。
5. Asset State Matrix / 待绑定状态。
6. 角色/场景/道具索引。
7. Beat 清单。
8. 完整分镜表。
9. 节奏/钩子节点。
10. 连续性、对白时长、场型状态和高风险说明。
11. cinematic_previs 时：Animatic Plan + Previs Gate。
12. 正式生成前：Shot Production Packets。
13. 若需要自动化：`storyboard.json` + validator 结果。

不要在结尾自动追加视频 Prompt；除非用户明确要求进入下一阶段。
