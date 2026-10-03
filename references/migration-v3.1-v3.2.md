# Migration Guide: v3.1 → v3.2 Sequence-Aware Storyboarding

v3.2 将“战斗场专用 Combat Plan”的思想推广到所有主要场型。

## 1. schema_version

新项目使用：

```json
"schema_version": "3.2"
```

旧 `3.0` 数据仍可读取；只有 v3.2 才强制完整 Sequence Plan。

## 2. Director Plan 增加 sequence_type

```json
"director_plan": {
  "sequence_type": "investigation_reveal",
  "secondary_sequence_types": []
}
```

类型列表见 `references/sequence-router.md`。

## 3. 非战斗 Scene 增加 sequence_plan

```json
"sequence_plan": {
  "profile": "investigation_reveal",
  "sequence_goal": "...",
  "sequence_beats": [],
  "rhythm_plan": [],
  "camera_strategy": "...",
  "continuity_priorities": []
}
```

Combat Scene 继续使用 `combat_plan`。

## 4. Shot 增加 sequence_context

```json
"sequence_context": {
  "sequence_beat_ids": ["E01-S01-SQ01"],
  "state_start": {},
  "state_end": {}
}
```

状态键按 profile 定义，例如：

- chase：route / gap / heading
- suspense：threat_visibility / knowledge
- stealth：detection_state / cover
- negotiation：power_holder / leverage
- montage：progress_stage / chronology

## 5. 连续性

没有明确 `motivated_jump / time_jump / scene_cut` 时：

```text
previous.sequence_context.state_end
→ current.sequence_context.state_start
```

同名键必须连续。

## 6. Sequence Beat Coverage

每个 `sequence_plan.sequence_beats[].id` 必须至少被一个 Shot 的：

```text
sequence_context.sequence_beat_ids
```

引用。

这样 Sequence Plan 不会退化成一份没人执行的说明文档。
