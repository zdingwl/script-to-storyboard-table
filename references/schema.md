# Storyboard Data Contract

本文件定义 Markdown 分镜表与 `storyboard.json` 的统一字段。Markdown 给人评审，JSON 给下游 Skill/自动化读取；两者必须来自同一份事实。

## ID

推荐稳定编号：

```text
Episode: E01
Scene: E01-S03
Beat: E01-S03-B04
Segment: E01-G05
Shot: E01-S03-004
Character: C01
Scene Asset: S01
Prop: P01
```

进入生产后不要因为小修改而重排全部 ID。

## 顶层

```json
{
  "schema_version": "2.0",
  "project": {
    "title": "项目名",
    "aspect_ratio": "9:16",
    "target_runtime_seconds": 60,
    "mode": "faithful",
    "target_video_model": "MiniMax H3"
  },
  "assets": {
    "characters": [],
    "scenes": [],
    "props": []
  },
  "episodes": []
}
```

`mode` 可取 `faithful` / `visual` / `pacing` / `story`。

## Asset

```json
{
  "id": "C01",
  "name": "角色名",
  "reference": "assets/characters/c01.png",
  "locked_traits": ["固定发型", "固定服装"]
}
```

场景和道具使用相同思路。真实路径不存在时写 `null`，不要伪造文件。

## Episode

```json
{
  "id": "E01",
  "title": "第一集",
  "target_runtime_seconds": 60,
  "scenes": []
}
```

## Scene

```json
{
  "id": "E01-S01",
  "slugline": "INT. 仪式大厅 - NIGHT",
  "location_asset": "S01",
  "characters": ["C01", "C02"],
  "props": ["P01"],
  "entry_state": {},
  "beats": [],
  "generation_segments": [],
  "exit_state": {}
}
```

## Beat

```json
{
  "id": "E01-S01-B01",
  "type": "information",
  "source_text": "她翻过徽章，看见背面的家族刻印。",
  "event": "角色发现徽章背面的家族刻印",
  "characters": ["C01"],
  "props": ["P01"],
  "dialogue": null,
  "must_preserve": true
}
```

常见 `type`：`action`、`dialogue`、`information`、`reaction`、`power_shift`、`reveal`、`hook`、`resolution`。

## Generation Segment

```json
{
  "id": "E01-G01",
  "scene_id": "E01-S01",
  "target_model": "MiniMax H3",
  "generation_mode": "Ref2VA",
  "duration_seconds": 12,
  "reference_assets": [
    {"label": "Picture 1", "asset_id": "C01", "purpose": "character_identity"},
    {"label": "Picture 2", "asset_id": "S01", "purpose": "environment"}
  ],
  "shots": []
}
```

`duration_seconds` 应等于该 Segment 内 shots 的时长总和。

## Shot

```json
{
  "id": "E01-S01-001",
  "scene_id": "E01-S01",
  "segment_id": "E01-G01",
  "source_beats": ["E01-S01-B01"],
  "timecode_in": 0.0,
  "timecode_out": 3.0,
  "duration_seconds": 3.0,
  "shot_size": "close-up",
  "angle": "eye-level",
  "camera_movement": "static",
  "composition": "C01 位于画面右侧，P01 位于中央前景",
  "characters": ["C01"],
  "blocking": "C01 低头，右手将 P01 翻到背面",
  "action": "刻印露出时手指停住",
  "performance": "由专注转为短暂停顿",
  "dialogue": [],
  "voiceover": [],
  "sound": ["衣料轻响", "金属轻擦声"],
  "assets": {
    "scene": "S01",
    "characters": ["C01"],
    "props": ["P01"]
  },
  "start_state": {
    "C01": "画面右侧，低头，右手持 P01 正面朝上",
    "P01": "正面朝上"
  },
  "end_state": {
    "C01": "仍在画面右侧，手指停住，目光锁定 P01",
    "P01": "背面朝上，刻印可见"
  },
  "transition": "cut_on_gaze",
  "continuity_notes": "下一镜保持视线方向",
  "risk": {"level": "low", "reasons": []},
  "status": "planned"
}
```

## 建议枚举

### shot_size

`extreme-wide`, `wide`, `full`, `medium-wide`, `medium`, `medium-close`, `close-up`, `extreme-close-up`, `insert`

### angle

`eye-level`, `high-angle`, `low-angle`, `overhead`, `ots`, `pov`, `dutch`, `profile`, `other`

### camera_movement

`static`, `push-in`, `pull-out`, `pan-left`, `pan-right`, `tilt-up`, `tilt-down`, `truck-left`, `truck-right`, `tracking`, `arc`, `handheld`, `crane`, `other`

这些枚举只为数据统一，不代表下游模型必须使用同名术语。

## Dialogue

```json
"dialogue": [
  {
    "speaker": "C01",
    "text": "你早就知道？",
    "delivery": "压低声音",
    "timing_estimate_seconds": 1.8,
    "timing_source": "estimated"
  }
]
```

`timing_source`：`measured` / `scripted` / `estimated`。不要把估算值写成实测值。

## Risk

```json
"risk": {
  "level": "medium",
  "reasons": ["two-character interaction", "small prop must remain readable"],
  "fallback": "拆成道具 insert + 人物反应镜"
}
```

## 时间码

机器 JSON 推荐使用数值秒：

```text
timecode_out - timecode_in = duration_seconds
next.timecode_in = current.timecode_out
```

如有刻意重叠声音，仍保持视频剪辑时间码连续，声音跨镜状态写在 `sound` / `continuity_notes`。

## Beat Coverage

- `must_preserve=true` 的 Beat 必须被覆盖。
- 默认一个 Beat 由一个 Shot 认领。
- 若同一 Beat 需要多个 coverage 镜头，使用 `coverage_exception` 说明原因。

```json
"coverage_exception": {
  "type": "reaction_coverage",
  "reason": "同一句对白延续到听者反应镜"
}
```

## Markdown 映射

| Markdown | JSON |
|---|---|
| 镜号 | `id` |
| 生成段 | `segment_id` |
| 场次 | `scene_id` |
| 时间码 | `timecode_in/out` |
| 时长 | `duration_seconds` |
| 原剧本节拍 | `source_beats` |
| 景别/角度 | `shot_size` + `angle` |
| 运镜 | `camera_movement` |
| 画面与构图 | `composition` |
| 人物/调度 | `characters` + `blocking` |
| 动作/表演 | `action` + `performance` |
| 台词/旁白 | `dialogue` + `voiceover` |
| 声音 | `sound` |
| 场景/道具/资产 | `assets` |
| 首帧状态 | `start_state` |
| 尾帧/衔接 | `end_state` + `transition` |
| 连续性/风险 | `continuity_notes` + `risk` |

推荐同时保存：

```text
storyboard.md
storyboard.json
```

如果只做一次性人工评审，可只交 Markdown；若下游继续生成关键帧、分镜图或视频 Prompt，建议同时输出 JSON。
