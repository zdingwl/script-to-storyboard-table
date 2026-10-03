# Dialogue & Emotion Sequence Planning

用于：`dialogue`、`confrontation_negotiation`、`emotional_intimacy`。

## 1. Dialogue

普通对白戏重点不是“谁说一句就切谁”，而是追踪：

- information turn：谁提供新信息；
- listening value：谁的反应更重要；
- relationship geometry：人物距离/朝向；
- topic shift：话题何时改变；
- silence：停顿是否有叙事意义；
- coverage economy：哪些镜头真正需要。

### Dialogue Plan

```json
{
  "profile": "dialogue",
  "sequence_goal": "...",
  "information_turns": [],
  "relationship_geometry": "...",
  "speaker_listener_priority": [],
  "reaction_obligations": [],
  "silence_points": [],
  "coverage_strategy": "master -> OTS -> selective close",
  "rhythm_plan": []
}
```

### 切镜优先点

- 新信息改变理解；
- 听者反应比说话人更重要；
- 话题/立场改变；
- 人物靠近/远离改变关系；
- 道具/证据进入对话；
- 沉默成为回答。

不要按台词行机械正反打。Shot/reverse-shot 是 coverage 工具，不是默认节奏。StudioBinder 的 coverage 资料同样强调，coverage 应随场景变化服务叙事与剪辑，而不是只做匹配镜头。

## 2. Confrontation / Negotiation / Interrogation

重点状态：

- power holder；
- demand / refusal；
- leverage；
- information asymmetry；
- physical territory；
- concession；
- threat level；
- breaking point。

### Plan

```json
{
  "profile": "confrontation_negotiation",
  "power_start": "C01",
  "power_end": "C02",
  "leverage_items": ["P01"],
  "demands": [],
  "concessions": [],
  "power_turns": [],
  "territory_plan": "...",
  "coverage_strategy": "...",
  "exit_condition": "..."
}
```

### 镜头逻辑

- power 未变化时，不必为了“有变化”频繁换景别；
- 权力变化时可通过 blocking、构图占比、前后景、视线和景别变化强化；
- leverage 被亮出时通常需要 insert / reveal / reaction；
- 逼问后的沉默可能比答案更重要；
- 人物进入对方私人空间是 blocking 事件，应写进状态，不只写“压迫感”。

## 3. Emotional / Intimacy / Romance

重点不是 romance 类型标签，而是：

- emotional distance；
- physical distance；
- mutual gaze / gaze avoidance；
- vulnerability；
- touch permission / rejection；
- disclosure；
- trust state；
- rupture / repair。

### Plan

```json
{
  "profile": "emotional_intimacy",
  "emotional_start": "guarded",
  "emotional_end": "open",
  "distance_start": "separated",
  "distance_end": "shared_space",
  "vulnerability_turns": [],
  "gaze_plan": [],
  "touch_or_distance_changes": [],
  "silence_points": [],
  "camera_strategy": "..."
}
```

### 规划原则

- 情感靠近不等于必须推镜；
- 关系变化优先通过人物行为、距离、视线呈现；
- 重要告白/拒绝后要给足反应读取时间；
- 不要用无根据的微表情替代剧本事实；
- 双人同框在关系变化前后往往比机械单人近景更有价值。

## 4. Group Dialogue / Meeting

如果 3 人以上：

先建立：

- seating/standing map；
- speaking alliance；
- silent observer；
- current focus；
- reaction priority。

不要每次发言都切一个新角色。可以用 master / group two-shot / selective singles 保持关系网。

## 5. Quality Gate

- [ ] 信息 turn 清楚
- [ ] 重要 reaction 有 coverage
- [ ] power / emotional distance 有状态变化时才强化镜头变化
- [ ] blocking 支持人物关系
- [ ] 没有每句台词机械切镜
- [ ] 沉默和停顿进入 timing
- [ ] 多人对白仍知道谁与谁形成当前关系
