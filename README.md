# script-to-storyboard-table

> Skill 定位：**AI Director & Cinematic Previsualization System**

将剧本、对白稿、小说改编稿或已有导演计划转换为 **可拍、可剪、可校验、可供 AI 视频流水线继续读取的结构化分镜表**。

当前版本：**v4.0.0（2026-10-04）**。

核心入口是根目录 `SKILL.md`。详细方法按需拆到 `references/`，确定性检查放在 `scripts/`，符合 Skill 的渐进式加载思路。

## 为什么继续升级到 v4

v2 已有 Beat ownership、Atomic Shot、Generation Segment、start/end state 与 H3 handoff，但实际生产还存在四类容易导致“单镜没问题、视频接不上”的结构性风险：

1. **缺导演预规划层**：直接从 Beat 拆 Shot，容易缺 establishing / reaction / insert-return / 动作中间相位。
2. **只有首尾状态，没有切镜合同**：相邻镜虽各自合理，却说不清为什么能自然切过去。
3. **Shot 与 Segment 可能形成两份事实**：同一镜头被嵌套复制后容易发生时长、台词和状态漂移。
4. **翻译后沿用原语言时长**：不同语言/配音版本的对白长度变化后，原镜头时长不再可靠。

v4 将正式流程收敛为：

```text
Script Lock / Story Contract
→ Sequence Type Router
→ Director Plan
→ Type-specific Sequence Plan / Combat Plan
→ Visual Bible Contract
→ Asset State Matrix
→ Geography / Blocking
→ Narrative Beat / Coverage
→ Atomic Shot
→ Continuity Handoff
→ Draft Storyboard
→ Continuity Audit
→ Continuity Repair
→ Approved Storyboard
→ Animatic / Previs
→ Previs Validation Gate
→ AI Video Shot Production Packet
```

核心变化不是“多拆镜”，而是把相邻镜头之间的状态继承变成机器可验证合同。

## v4.0：把“能看懂”升级成“能连续执行”

v4 新增三层硬约束：

- **State Inheritance**：连续 Handoff 明确列出必须继承的 `start/end state` 路径，validator 逐路径比较上一镜尾状态与下一镜首状态；
- **Action State**：跨镜连续物理动作用稳定 `action_id + phase_start/phase_end` 跟踪，防止动作重启、倒退和无解释跳相位；
- **Continuity/Previs 双 Gate**：第一版只能是 Draft Storyboard，必须经过 Continuity Audit/Repair 才能进 Animatic，再通过 Previs Gate 才进入正式 AI 视频生产。

完整规则：

- `references/continuity-audit.md`
- `references/ai-video-shot-transition.md`
- `references/previs-validation.md`
- `references/migration-v3.3-v4.0.md`

## v3.3：从“分镜 Skill”升级为 Previs System

v3.3 吸收电影/动画前期中最值得 AI 短剧使用的几层：

- **Script Lock / Story Contract**：锁 objective、obstacle、escalation、information release、情绪起止与 irreversible change；
- **Visual Bible Contract**：项目级摄影、镜头意图、灯光、色彩、构图、材质规则只定义一次；
- **Asset State Matrix**：不只管理 C01，而是管理 C01-ST01 / ST02 / ST03 等剧情状态；
- **Animatic / Previs Gate**：分镜完成后先放到时间线上验证节奏、动作、对白和缺镜；
- **Shot Production Packet**：正式视频模型只执行已经设计好的镜头；
- **Pickup Feedback Loop**：粗剪发现问题时优先补镜/替换，而不是整场推倒。

Storyboard 与 Animatic 是两个不同质量门；Animatic 会把静态分镜放入时间、声音和运动关系里验证。研究来源见 `references/sources.md`。

Visual Bible / Lookbook 则作为跨部门视觉参考，让 cinematography、production design、lighting、color 等方向不必在每镜重新决定。研究来源见 `references/sources.md`。

## v4 关键能力

### 1. Director Plan 先于拆镜

每场先决定：

- `dramatic_job`：这场必须完成什么；
- `turn`：场内真正的转折；
- `visual_strategy`：主要视觉组织方式；
- `blocking_plan`：人物站位与移动；
- `axis_plan`：180°轴线和屏幕方向；
- `coverage_obligations`：必须拍到哪些信息/反应/证据；
- `pacing` 与 `hook_role`。

详见 `references/director-plan.md`。

### 1.2 Sequence Type Router：不同场面使用不同导演语法

v3.2 先识别场型，再拆镜。核心类型覆盖：

```text
dialogue / negotiation / emotional
investigation / suspense / horror / stealth
chase / vehicle / rescue
combat
disaster / crowd / comedy / montage / performance / world reveal / transition
```

每种类型追踪不同核心状态：

| 场型 | 核心状态 |
|---|---|
| dialogue | information turn / reaction |
| negotiation | power / leverage / concession |
| emotional | distance / trust / gaze |
| investigation | evidence / knowledge |
| suspense | withheld answer / threat visibility |
| horror | unknown space / offscreen threat |
| stealth | detection / sightline / cover |
| chase | route / gap / heading |
| combat | zone / range / advantage / action phase |
| rescue | hazard / victim / rescue phase |
| disaster | hazard stage / safe zone / crowd flow |
| comedy | setup / expectation / payoff |
| montage | progression / motif / chronology |
| performance | stage geography / audience relation |

非战斗场通过 `sequence_plan + sequence_context` 把这些状态真正传进 Shot，并跨镜校验。

详见 `references/sequence-router.md`。

### 1.5 战斗场 Combat Plan

战斗、打戏、持械冲突和多人混战不会直接按“逐招拆镜”。v3.1 增加：

```text
Director Plan
→ Combat Plan
→ Combat Beat
→ Action Phase
→ Atomic Shot
→ Combat Handoff
→ Aftermath
```

Combat Plan 会先建立：

- Combat Goal；
- 参与者目标/状态；
- Arena Zones；
- Combat Beats；
- advantage 前后变化；
- zone / range 前后变化；
- Rhythm Plan；
- 多人 theater；
- camera strategy；
- 道具/伤势/屏幕方向连续性。

详见 `references/combat-planning.md`，并提供 `examples/combat-storyboard.example.json`。

### 2. Beat → Shot 可追溯

每个正式 Shot 必须认领原剧本 Beat：

```text
source_beats: ["E01-S01-B02"]
```

默认不允许：

- 漏掉 must-preserve Beat；
- 无解释重复覆盖；
- Shot 乱序认领 Beat；
- 非线性没有显式 exception。

### 3. 每镜必须有“存在理由”

v3 为 Shot 增加：

```text
purpose
cut_reason
director_obligation
```

避免“为了丰富而多切镜”。镜头变化必须服务信息、动作、关系、证据、反应、节奏或空间建立。

### 4. Handoff 解决跨镜衔接

除 Scene 第一镜外，推荐每镜记录：

```json
"handoff_from_previous": {
  "from_shot_id": "E01-S01-001",
  "type": "reaction",
  "reason": "证据露出后切发现者反应，注意力从物转人"
}
```

支持：

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

`start_state / end_state` 回答“状态是什么”，`handoff_from_previous` 回答“为什么这里能切”，v4 的 `state_inheritance` 则回答“哪些状态必须从上一镜尾帧原样进入下一镜首帧”。

例如：

```json
"state_inheritance": [
  "characters.C01.zone",
  "props.P01.holder",
  "props.P01.hand"
]
```

validator 会直接比较这些路径，不再只靠人工阅读两段自由文本。

### 5. Shot 单一事实源

v3 只允许：

```text
Scene.shots = 完整 Shot 数据（唯一正式来源）
GenerationSegment.shot_ids = 对 Shot 的引用
```

不再允许把完整 Shot 同时复制进 Segment。

这样关键帧、剪辑、H3 Prompt、校验器都读取同一组镜头事实。

### 6. 两套时间轴分开

Shot：

```text
timecode_in / timecode_out = 集内/成片累计时间
```

Generation Segment：

```text
本地 cut 时间 = 按 shot_ids 的 duration_seconds 从 0 派生
```

例如全片时间为 31–39 秒的 Segment，给 H3 时仍是本地：

```text
0.00–3.00
3.00–8.00
```

不会把全片时间码误传给模型。

### 7. 跨语言对白时长重算

当：

```text
source_language != output_language
```

源语言 timing 自动视为失效。不得写：

```text
timing_source: inherited_source
```

必须按目标语言文本或目标 TTS / 实际音频重新测量，再回写：

```text
Dialogue timing
→ Shot duration
→ Scene / Episode runtime
→ Segment boundary
→ 全局 timecode
```

详见 `references/dialogue-timing.md`。

### 8. Hook Audit

v3 区分真正“未决型钩子”和单纯结果：

- `information_gap`
- `threat_pending`
- `secret_approaching`
- `choice_unresolved`
- `cognitive_reversal`
- `countdown`
- `action_unresolved`
- `result_only`
- `none`

在 `faithful` 模式中只审计，不擅自改剧情；`result_only` 会被 validator 提醒。

### 9. MiniMax H3 交接

H3 仍与最终 Prompt Skill 解耦。本 Skill 只准备：

```text
剧情事实
+ Shot 结构
+ Segment shot_ids
+ Segment 本地 cut 时间
+ 参考资产职责
+ start/end state
+ handoff
+ generation_mode hint
```

最终 H3 Prompt 交给 MiniMax 官方 `h3-prompt-writing`。

当前 H3 规则核对日期记录在：

```text
project.model_profile.verified_at
```

validator 内置规则日期与项目日期不一致时会发出 warning，防止把快速变化的模型硬限制永久当成影视规则。

## 仓库结构

```text
script-to-storyboard-table/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── previs-pipeline.md
│   ├── script-lock-contract.md
│   ├── visual-bible-contract.md
│   ├── asset-state-matrix.md
│   ├── continuity-audit.md
│   ├── ai-video-shot-transition.md
│   ├── animatic-previs.md
│   ├── previs-validation.md
│   ├── shot-production-packet.md
│   ├── post-generation-loop.md
│   ├── sequence-router.md
│   ├── director-plan.md
│   ├── dialogue-emotion-planning.md
│   ├── suspense-investigation-planning.md
│   ├── chase-action-planning.md
│   ├── combat-planning.md
│   ├── tempo-spectacle-planning.md
│   ├── storyboard-method.md
│   ├── dialogue-timing.md
│   ├── schema.md
│   ├── h3-handoff.md
│   ├── migration-v2-v3.md
│   ├── migration-v3.3-v4.0.md
│   └── sources.md
├── assets/
│   └── storyboard-template.md
├── examples/
│   ├── storyboard.example.json
│   └── combat-storyboard.example.json
├── scripts/
│   └── validate_storyboard.py
└── tests/
    └── test_validate_storyboard.py
```

## 标准使用方式

### 普通剧本转分镜

给 Skill 剧本并说明：

```text
按 faithful 模式生成完整分镜表；先做导演预规划，不改剧情。
```

默认交付：

1. 分镜摘要；
2. 资产/资产需求；
3. Scene Director Plan；
4. Beat 清单；
5. 完整分镜表；
6. Generation Segment（需要 AI 视频时）；
7. Hook / Continuity / Missing-shot / Timing Audit；
8. `storyboard.json`（需要机器接力时）。

### 翻译版分镜

```text
把现有中文分镜改成英文配音版。剧情和镜头逻辑不变，但按英文台词重新计算时长并重新分配 Segment。
```

Skill 不得保留中文版对白时长。

### MiniMax H3 下游

```text
按 MiniMax H3 生产模式整理 Generation Segments，但不要生成最终 H3 Prompt。
```

随后将 `storyboard.json` + 资产交给官方 H3 Prompt Skill。

## JSON 校验

普通校验：

```bash
python scripts/validate_storyboard.py examples/storyboard.example.json
```

严格模式：

```bash
python scripts/validate_storyboard.py examples/storyboard.example.json --strict
```

机器报告：

```bash
python scripts/validate_storyboard.py examples/storyboard.example.json --json
```

当前 validator 包括：

- ID 重复；
- Beat 漏覆盖 / 乱序 / 非连续认领；
- Shot duration 与 finished-cut timecode；
- Director Plan 缺失；
- `purpose` / `cut_reason` 缺失；
- v4 结构化 start/end state；
- handoff 类型、前镜 ID、理由；
- 连续切镜 `state_inheritance` 非空与逐路径一致性；
- action_state phase 合法性、倒退检测；
- match-on-action 同一 action_id；
- v3 Segment 禁止重复嵌入完整 Shot；
- `shot_ids` 顺序和重复归属；
- Segment 时长与 Shot 求和；
- 翻译项目禁止沿用源语言 timing；
- Dialogue / VO 容量；
- H3 4–15 秒输出范围；
- H3 图片/视频/音频/混合参考数量；
- H3 参考视频/音频单段与累计时长；
- H3 规则核对日期提示；
- Episode / Project runtime 一致性；
- result-only 结尾钩子提示。

## 回归测试

```bash
python -m unittest discover -s tests -v
```

当前基线覆盖：

- 合法 v4 示例零 warning；
- 翻译后禁止 `inherited_source` timing；
- v3 禁止 Segment 内复制 Shot；
- H3 Segment 时长越界；
- handoff 必须指向真实前镜；
- v4 连续 handoff 必须有 state_inheritance；
- world-state inheritance 断裂会报错；
- match-on-action 必须继续同一 action_id；
- 同一 action_id 的 phase 不允许倒退；
- v3.2 Scene 必须有合法 sequence_type；
- 非战斗场必须有对应 sequence_plan；
- Sequence Beat 必须被 Shot 认领；
- sequence_context 同名状态必须跨镜连续；
- combat Scene 必须存在 Combat Plan；
- 战斗 Shot 的 zone/range/advantage 跨镜连续性。

## 数据迁移

已有 v2/v3 数据不必重做剧情分析。先按原迁移文档保留现有 Director / Sequence / Combat 数据，再按 `references/migration-v3.3-v4.0.md` 把关键 start/end state 结构化，并补 state_inheritance / action_state。

1. 收敛 Shot 到 `scene.shots`；
2. Segment 改为 `shot_ids`；
3. 统一全片时间码；
4. 补 `handoff_from_previous`；
5. 补 `director_plan`；
6. 翻译项目重新测 timing。

## 资料依据

研究来源与采用边界统一记录在 `references/sources.md`，包括：

- OpenAI Skill 当前结构与 progressive disclosure；
- MiniMax H3 官方仓库 / `h3-prompt-writing`；
- StudioBinder 的 blocking、180° 连续性与剪辑基础；
- Boords 的 script → storyboard / shot-list 方法；
- Google Veo prompting guidance；
- 跨语言 speech-rate / information-rate 研究；
- 多个公开 storyboard Skill 的可复用设计。

原则：**模型硬限制听官方最新资料，摄影与剪辑语法听成熟影视方法，社区 Skill 只吸收可验证的结构，不照搬其模型假设。**

## 版本

- `4.0.0` — Draft→Continuity Audit/Repair→Approved→Previs 双 Gate；结构化 state inheritance；action_state；AI Video Shot Transition Contract；v4 validator + regression tests。
- `3.3.0` — Script Lock、Visual Bible Contract、Asset State Matrix、Animatic/Previs Gate、Shot Production Packet、Pickup Loop。
- `3.2.0` — Sequence Type Router、主要场型专用规划、Sequence Plan/Beat/Context 与通用状态连续性校验。
- `3.1.0` — Combat Plan、Combat Beat、Arena/Range/Advantage 连续性、战斗示例与 validator。
- `3.0.0` — Director Plan、Handoff、跨语言 Timing、单一 Shot 事实源、Hook Audit、v3 validator + tests。
- `2.0.0` — Beat ownership、Atomic Shot、Generation Segment、start/end state、H3 handoff。
