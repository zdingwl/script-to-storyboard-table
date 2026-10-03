# Tempo, Spectacle & Ensemble Sequence Planning

用于：`disaster_survival`、`crowd_ensemble`、`comedy`、`montage_progression`、`performance_ritual`、`world_reveal_establishing`、`transition_travel`。

## 1. Disaster / Survival

灾难场不是“大场面镜头越多越好”。

先追踪：

- macro hazard state；
- local hazard state；
- survival objective；
- safe/unsafe zones；
- infrastructure state；
- crowd flow；
- resource state；
- information delay；
- escalation stage。

### Disaster Stage

```text
normal / anomaly
→ recognition
→ disruption
→ escalation
→ system failure
→ survival adaptation
→ temporary stabilization / worse phase
```

### Plan

```json
{
  "profile": "disaster_survival",
  "hazard": "...",
  "macro_stages": [],
  "local_objective": "...",
  "safe_unsafe_map": {},
  "infrastructure_changes": [],
  "crowd_flow": [],
  "resource_changes": [],
  "scale_shots": [],
  "human_anchor": "C01"
}
```

原则：大尺度镜头负责 scale/state，小尺度镜头负责人物目标与代价，两者交替而不是只堆灾难全景。

## 2. Crowd / Ensemble

核心是 attention routing。

追踪：

- groups；
- focal character；
- alliances；
- crowd objective；
- flow direction；
- foreground/mid/background action；
- reaction wave；
- current speaker/leader；
- exits / chokepoints。

不要让 10 个角色都成为“同时主角”。

## 3. Comedy

Comedy 规划核心是：

```text
setup
→ expectation
→ delay / repetition
→ reveal/payoff
→ reaction / topper
```

笑点如果依赖视觉信息，要保证观众在角色之前/之后知道什么是明确设计。

### Plan

```json
{
  "profile": "comedy",
  "setup": "...",
  "audience_expectation": "...",
  "payoff": "...",
  "knowledge_advantage": "audience / character / equal",
  "repetition_pattern": [],
  "timing_holds": [],
  "reaction_priority": [],
  "topper": null
}
```

不要自动加笑点。faithful 模式只把已有 comedy mechanism 拍清楚。

## 4. Montage / Progression

Montage 不是“随便列几个漂亮镜头”。

StudioBinder 的 montage storyboard 资料强调 montage 镜头之间的互动、方向、节奏与 animatic 验证；montage 常用于压缩时间、并置、比较和多线交织。citeturn783034search0turn783034search11

追踪：

- compression goal；
- start state；
- end state；
- progression axis；
- motif；
- repetition with variation；
- transition logic；
- music/rhythm relation；
- chronology。

### Plan

```json
{
  "profile": "montage_progression",
  "compression_goal": "三天准备过程压缩成 12 秒",
  "start_state": "...",
  "end_state": "...",
  "progression_axis": "resources increase",
  "motifs": [],
  "repetition_pattern": [],
  "transition_logic": "graphic / action / sound / contrast",
  "rhythm_plan": [],
  "chronology": "forward"
}
```

每个 montage shot 应贡献“变化”，不要只是换场景。

## 5. Performance / Ritual

用于演讲、演出、比赛开场、仪式、发布会、婚礼等。

重点：

- performer/focal subject；
- audience relation；
- stage geography；
- ritual order；
- key beats；
- reaction audience；
- sync points；
- spectacle vs intimacy balance。

不能只拍舞台正面。重要时刻通常需要 performer + audience reaction + spatial context。

## 6. World Reveal / Establishing

目的不是“给一个空镜”，而是建立：

- scale；
- geography；
- rules；
- threat/opportunity；
- human relation to space；
- important landmarks。

### Reveal Plan

```text
partial clue
→ orientation
→ scale reveal
→ key landmark
→ character response / objective
```

如果世界信息在后续动作中自然可见，不一定需要独立 establishing shot。

## 7. Transition / Travel

过渡戏只保留观众必须知道的变化：

- location change；
- time change；
- condition change；
- objective continuity；
- travel progress；
- arrival state。

如果“上车→路上→下车”没有任何状态变化，可以压缩成一个转场，不应机械生成三镜。

## 8. Quality Gate

- [ ] disaster 有阶段与人类锚点
- [ ] crowd 有 attention routing
- [ ] comedy setup/payoff 时序清楚
- [ ] montage 每镜贡献 progression
- [ ] performance 同时考虑主体和观众
- [ ] world reveal 建立可用空间/规则
- [ ] transition 只保留必要状态变化
