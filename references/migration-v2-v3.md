# Migration Guide: schema 2.0 → 3.0

v3 解决三个 v2 容易产生歧义的问题：

1. Shot 可能既出现在 `scene.shots` 又完整复制到 `generation_segments[].shots`，形成双事实源；
2. `timecode_in/out` 容易被同时解释为成片累计时间和 Segment 本地时间；
3. 翻译对白后缺少可机器检查的 timing 失效标记。

## 1. 先保留原 ID

不要重排：

- Episode ID
- Scene ID
- Beat ID
- Shot ID
- Asset ID

Segment ID 可继续使用旧值；新项目推荐 `E01-S01-G01` 形式。

## 2. Shot 只保留一份

### v2

```json
{
  "generation_segments": [
    {
      "id": "E01-G01",
      "shots": [
        {
          "id": "E01-S01-001",
          "...": "完整 Shot"
        }
      ]
    }
  ]
}
```

### v3

```json
{
  "shots": [
    {
      "id": "E01-S01-001",
      "...": "完整 Shot"
    }
  ],
  "generation_segments": [
    {
      "id": "E01-S01-G01",
      "shot_ids": ["E01-S01-001"]
    }
  ]
}
```

如果 v2 同时有 scene-level shot 和 segment-level shot，以用户已批准/实际投产版本为准，不要自动猜两份谁更新。

## 3. 时间码统一为成片累计时间

v3：

```text
Shot.timecode_in/out = Episode/finished-cut timeline
```

Segment 本地时间不保存，按：

```text
shot_ids + duration_seconds
```

派生。

如果旧 JSON 的 shot timecode 是 Segment 本地时间，迁移时必须重新累计。

## 4. Dialogue timing

### v2

```json
{
  "text": "你早就知道？",
  "timing_estimate_seconds": 1.8,
  "timing_source": "estimated"
}
```

### v3

```json
{
  "text": "你早就知道？",
  "language": "zh-CN",
  "timing_seconds": 1.8,
  "timing_source": "estimated_target_text"
}
```

如果文本经过翻译：

- 不得保留 `inherited_source`；
- 重新估算或测量；
- 重算 shot/scene/segment runtime。

## 5. 增加 handoff

Scene 第一镜之外，为每镜补：

```json
"handoff_from_previous": {
  "from_shot_id": "前一镜 ID",
  "type": "direct",
  "reason": "说明为什么这里能接"
}
```

不要为了过校验全部机械写 `direct`；如果实际是 eyeline、reaction、insert、time jump，应写真实类型。

## 6. 增加 Director Plan

每个 Scene 补最小：

```json
"director_plan": {
  "dramatic_job": "...",
  "turn": "...",
  "blocking_plan": "...",
  "axis_plan": "...",
  "coverage_obligations": [],
  "visual_strategy": "...",
  "pacing": "neutral",
  "hook_role": "none"
}
```

已有上游导演计划时直接映射，不要二次改写。

## 7. Model Profile

H3 项目建议补：

```json
"model_profile": {
  "name": "minimax-h3",
  "verified_at": "2026-10-03"
}
```

日期表示“这些硬限制最后一次与官方资料核对的时间”，不是模型发布日期。

## 8. 验证

迁移后运行：

```bash
python scripts/validate_storyboard.py storyboard.json
```

再运行：

```bash
python scripts/validate_storyboard.py storyboard.json --strict
```

先修 error，再决定 warning 是否属于有意例外。
