# AI Video Shot Production Packet

正式 AI 视频生成不应只接收一句 Prompt，而应接收已经被导演系统约束好的 Shot Packet。

## 1. 目标

视频模型负责：

> 执行一个已设计好的镜头。

而不是：

> 自己决定剧情、blocking、camera、style 和 continuity。

## 2. Packet

建议：

```json
{
  "shot_id": "E01-S01-001",
  "sequence_type": "suspense_threat",
  "source_beats": [],
  "sequence_beat_ids": [],
  "references": [],
  "subject_states": [],
  "scene_state": null,
  "prop_states": [],
  "start_state": {},
  "end_state": {},
  "action": "",
  "blocking": "",
  "character_movement": "",
  "camera_position": "",
  "shot_size": "",
  "angle": "",
  "lens_intent": "",
  "camera_movement": "",
  "composition": "",
  "depth_layers": {
    "foreground": "",
    "midground": "",
    "background": ""
  },
  "duration_seconds": 0,
  "dialogue": [],
  "sound": [],
  "continuity_from_previous": {},
  "continuity_into_next": {},
  "visual_bible_ref": null,
  "do_not_change": [],
  "generation_constraints": [],
  "risk": {},
  "fallback": null
}
```

## 3. Lens Intent

优先写叙事功能，不强迫虚假精确焦段：

- `wide-spatial`
- `natural-relation`
- `compressed-isolation`
- `subjective-distortion`
- `detail-isolation`

只有项目已有镜头/传感器体系时再写具体 mm。

## 4. Camera Position

应该比“低机位/高机位”更清楚：

- 相对人物；
- 位于轴线哪一侧；
- 与空间 anchor 的关系；
- 高度；
- 是否移动。

## 5. Depth Layers

明确：

- foreground；
- midground；
- background。

这会帮助关键帧/AI 视频保持构图层次，而不是只描述“人物在画面中央”。

## 6. Generation Constraints

例如：

- no costume change；
- P01 remains in right hand；
- C01 stays screen-left；
- no extra characters；
- preserve rain direction；
- do not reveal threat face；
- no new readable text。

## 7. Packet 与模型 Prompt

Packet 是模型无关的导演数据。

H3 / Kling / Veo Prompt Skill 再根据 Packet 编译成各自格式。

不要把模型 Prompt 反过来当 canonical storyboard。
