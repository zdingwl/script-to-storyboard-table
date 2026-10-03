# Animatic / Previs Gate

Storyboard 是静态决策；Animatic / Previs 是把这些决策放进时间里验证。

StudioBinder 将 animatic 描述为 storyboard images 按时间剪接并加入 sound/dialogue/motion，用来测试 sequence 如何流动；动画与复杂动作/VFX 场景尤其适合在最终高成本制作前完成这一验证。

## 1. 本 Skill 输出什么

如果用户要求 cinematic previs，输出：

- `animatic-plan.json`
- `previs-report.md`

本 Skill 不一定直接渲染视频，但必须生成可进入 NLE/Animatic 工具的时间线计划。

## 2. Animatic Timeline

建议字段：

```json
{
  "shot_id": "E01-S01-001",
  "time_in": 0.0,
  "time_out": 3.0,
  "duration": 3.0,
  "panel_ref": "storyboards/001.png",
  "camera_preview": "slow push",
  "dialogue_ref": "temp/C01_001.wav",
  "sfx": [],
  "music_cue": null,
  "transition": "cut",
  "notes": ""
}
```

## 3. 临时素材

允许：

- storyboard panels；
- 灰盒/简单 blocking；
- 临时 TTS；
- 临时 ambience；
- temp music；
- 简单 pan/zoom；
- black frames；
- subtitle placeholders。

目的不是“看起来成片”，而是验证结构。

## 4. Previs Audit

逐 Sequence 检查：

### Comprehension

- 不看剧本能否知道谁在做什么；
- 地理关系是否清楚；
- 信息是否按计划释放。

### Timing

- dialogue 是否说得完；
- reaction 是否有时间读；
- action 是否过快；
- establishing 是否过久；
- hook 是否过早泄底。

### Continuity

- end/start 是否自然；
- asset states 是否连续；
- screen direction 是否成立；
- Sequence Context 是否跳状态。

### Editing

- 是否缺 cause / effect；
- 是否缺 reaction；
- 是否存在无意义重复镜头；
- 节奏是否全部同一速度；
- climax 前后是否有对比。

## 5. Previs Gate Status

```json
"previs_gate": {
  "status": "pass | revise | blocked",
  "issues": [],
  "required_pickups": [],
  "approved_runtime_seconds": 0
}
```

只有 `pass` 才建议进入正式逐镜生成。

## 6. Animatic 的价值

它能在低成本阶段暴露：

- 缺镜；
- 镜头顺序错误；
- shot duration 不成立；
- dialogue timing 错误；
- 战斗/追逐空间不清；
- montage 无 progression；
- suspense 提前泄底；
- transition 断裂。

因此“Storyboard 通过”与“Previs 通过”是两个不同质量门。
