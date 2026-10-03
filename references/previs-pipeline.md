# Cinematic Previsualization Pipeline

本文件定义本 Skill 的完整前期导演/预演流程。

目标不是直接生成最终视频，而是把锁定剧本编译成一个可以被分镜、Animatic、AI 视频模型和后续剪辑稳定执行的 **Cinematic Previs Package**。

## 1. 正确层级

推荐：

```text
Story / Novel
→ Script
→ Script Lock / Story Contract
→ Sequence Type Router
→ Director Plan
→ Type-specific Sequence Plan
→ Visual Bible Contract
→ Asset State Matrix
→ Geography / Blocking
→ Coverage / Cinematography
→ Storyboard
→ Continuity Audit
→ Animatic / Previs
→ Previs Gate
→ AI Video Shot Production Packet
→ downstream generation / edit / sound / VFX
```

本 Skill 负责从 Script Lock 到 Shot Production Packet。

最终 AI 视频生成、正式剪辑、Sound Design、VFX、Color 和 Final QC 属于下游生产系统。

## 2. 为什么不能 Script → Shot

直接拆 Shot 容易把以下导演问题推给视频模型：

- 场面目的不清；
- POV 失焦；
- 信息释放顺序错误；
- 人物空间关系缺失；
- blocking 未定义；
- 资产状态漂移；
- coverage 不足；
- 节奏未经时间线验证；
- 镜头各自漂亮但无法剪成连续场面。

AI 视频模型不应该替导演解决这些问题。

## 3. Previs Gate

Storyboard 完成不等于可以正式生成。

进入正式 AI Video Production 前至少检查：

- 剧情 Beat 是否完整；
- Scene / Sequence Plan 是否兑现；
- start/end/handoff 是否连续；
- asset state 是否连续；
- blocking/geography 是否可读；
- dialogue timing 是否成立；
- Animatic 总节奏是否成立；
- 转场是否自然；
- 是否存在 missing shot；
- AI Segment 是否过载；
- Shot Production Packet 是否完整。

若 Animatic / Previs 显示场面无法理解、动作跳跃或节奏失衡，应返回上游修 Shot，而不是先增加视频 Prompt 字数。

## 4. Canonical 与 Derived Artifacts

### Canonical

- locked script / story contract
- director plan
- sequence plan
- storyboard.json
- asset state matrix
- visual bible reference

### Derived

- storyboard.md
- animatic plan / animatic timeline
- shot production packets
- H3 / Kling / Veo handoff
- pickup request

Derived 文件不得反向创造新的剧情事实。

## 5. Pipeline Quality Gates

### Gate A — Story Lock

通过条件：

- 每场 objective / obstacle / escalation 清楚；
- information release 可追踪；
- emotional start/end 清楚；
- irreversible change 明确；
- must-preserve facts 已冻结。

### Gate B — Director / Sequence

通过条件：

- sequence_type 正确；
- POV / information control 明确；
- geography / blocking 清楚；
- coverage obligations 完整；
- sequence/combat beats 能映射 Narrative Beats。

### Gate C — Visual / Asset

通过条件：

- visual bible 已锁定或明确 pending；
- Character × Costume × State 已建立；
- Location / Prop / Damage / Time state 已建立；
- Shot 不再自行发明资产外观。

### Gate D — Storyboard / Continuity

通过条件：

- Shot atomic；
- end → handoff → start 成立；
- sequence state 连续；
- screen direction / axis 清楚；
- asset state refs 连续；
- timing 可执行。

### Gate E — Animatic / Previs

通过条件：

- 全片时间线可理解；
- 临时对白不被截断；
- 镜头停留时间足够；
- action / reaction 节奏成立；
- 不存在明显 missing shot；
- sequence climax / release / hook 时机成立。

### Gate F — AI Video Handoff

通过条件：

- 每 Shot 有 production packet；
- style / asset / continuity locks 完整；
- do-not-change 清楚；
- generation constraints 与 fallback 清楚；
- Segment 符合目标模型限制。

## 6. 与 Unreal / Virtual Production 思路的关系

现代 virtual production / previs 的价值不是“先做一版漂亮 3D”，而是尽早验证：

- location / geography；
- blocking；
- composition；
- camera；
- timing；
- shot interaction；
- sequence structure。

Unreal 的 Virtual Scouting 也明确用于 location exploration、composition 和 scene blocking；官方项目结构示例中也将 Previs / Techvis / Edits 作为独立制作层。

本 Skill 不依赖 Unreal，但采用同一原则：**先可视化并验证，再进入高成本最终生产。**
