# Suspense, Investigation, Horror & Stealth Planning

用于：`investigation_reveal`、`suspense_threat`、`horror_dread`、`stealth_infiltration`。

## 1. Investigation / Reveal

核心不是“角色到处找”，而是 **evidence chain + knowledge delta**。

追踪：

- evidence state；
- who knows what；
- clue visibility；
- false interpretation（只来自原剧情）；
- confirmation；
- reveal order；
- reaction to evidence。

### Plan

```json
{
  "profile": "investigation_reveal",
  "question": "谁进入过房间？",
  "evidence_chain": ["P01", "P02"],
  "knowledge_start": {},
  "knowledge_end": {},
  "reveal_schedule": [],
  "evidence_readability": [],
  "false_leads": [],
  "camera_strategy": "search geography -> insert -> reaction"
}
```

### 镜头义务

证据通常至少需要回答：

```text
它在哪里？
→ 角色如何发现？
→ 观众看清什么？
→ 角色如何解释？
```

若证据依赖小字、UI、文件，AI 视频风险高，应考虑独立关键帧/后期文字。

## 2. Suspense / Threat

Suspense 的核心是：

```text
提出问题
→ 延迟答案
→ 增加可信威胁/成本
→ 部分释放信息
→ 重新提出更具体的问题
```

StudioBinder 将 suspense 的基础描述为：观众等待一个答案，但不知道何时/如何发生。重点不是“镜头越晃越紧张”，而是信息控制。 

### State

- audience_knows；
- character_knows；
- threat_known；
- threat_location；
- deadline；
- safe/unsafe zones；
- withheld_answer；
- reveal_threshold。

### Plan

```json
{
  "profile": "suspense_threat",
  "audience_question": "门后是否有人？",
  "audience_knowledge": "...",
  "character_knowledge": "...",
  "threat_visibility": "unknown / partial / known",
  "reveal_schedule": [],
  "delay_devices": [],
  "safe_unsafe_map": {},
  "sound_cues": [],
  "release_point": "..."
}
```

### 镜头原则

- 不要过早给出威胁完整位置；
- 角色 eyeline 后是否切目标，要由“此刻该不该给答案”决定；
- blocking 可制造 tension；
- 留白/负空间只有在观众被引导去期待它时才有效；
- 声音可先于画面泄露存在，但要进入 information plan。

## 3. Horror / Dread

与普通 suspense 的区别：

- 观众可能无法确认威胁是什么；
- 空间本身可成为威胁；
- negative space / occlusion / offscreen space 更重要；
- 安全规则可能逐步崩溃。

### Plan

```json
{
  "profile": "horror_dread",
  "fear_question": "...",
  "known_safe_space": [],
  "unknown_space": [],
  "offscreen_threat_channels": ["sound", "shadow"],
  "visibility_policy": "withhold",
  "dread_escalation": [],
  "confirmation_point": null,
  "aftermath": "..."
}
```

### 禁止默认套路

不要自动：

- 加 jumpscare；
- 加鬼影；
- 加镜子反射；
- 加灯闪；
- 加角色回头发现人。

只有原剧情或授权存在时才能使用。

## 4. Stealth / Infiltration

核心状态：

- objective；
- detection state；
- observer sightline；
- cover/occlusion；
- noise risk；
- route；
- checkpoint；
- exposure consequence。

### Detection State

```text
hidden
→ suspected
→ searched_for
→ partially_seen
→ exposed
```

### Plan

```json
{
  "profile": "stealth_infiltration",
  "objective": "...",
  "route": ["Z1", "Z2", "Z3"],
  "observer_map": {},
  "sightline_map": {},
  "cover_points": [],
  "noise_events": [],
  "detection_state_start": "hidden",
  "detection_turns": [],
  "failure_condition": "exposed"
}
```

### 镜头原则

- 观众要知道“谁可能看见谁”；
- 不能只拍主角近景而完全失去守卫/观察者空间；
- POV / eyeline / cutaway 常用于建立 sightline；
- 一旦 detection state 变化，要有可见/可听原因；
- stealth 转 chase 时应切换 profile，而不是继续用潜入语法。

## 5. Quality Gate

- [ ] evidence / threat / detection 状态明确
- [ ] 谁知道什么可追踪
- [ ] reveal 没有提前泄露
- [ ] 证据可读性合理
- [ ] offscreen 信息通过声音/视线/空间建立
- [ ] stealth sightline 连续
- [ ] suspense 的延迟有原因，不是无意义拖时长
