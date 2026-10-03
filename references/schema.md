# Storyboard Data Contract v3.2

Markdown 给人评审，`storyboard.json` 给下游 Skill/自动化读取。两者必须来自同一份事实。

v3 的最重要变化：

1. `scene.shots` 是 Shot 唯一事实源；
2. `generation_segments[].shot_ids` 只引用 Shot，不再复制完整 Shot；
3. Shot 时间码统一表示**集内/成片累计时间**；
4. Segment 本地 cut 时间由 `shot_ids + duration_seconds` 派生；
5. Dialogue 显式记录语言与 timing 来源；
6. 非第一镜显式记录 `handoff_from_previous`；
7. Scene 显式记录 `director_plan`；
8. 每个 Scene 显式记录 `director_plan.sequence_type`；
9. 非战斗 Scene 使用 `sequence_plan`，战斗 Scene 使用 `combat_plan`；
10. Shot 可用 `sequence_context` / `combat_context` 认领导演层 Beat 并维护类型状态。

## 1. ID

推荐：

```text
Episode: E01
Scene: E01-S03
Beat: E01-S03-B04
Segment: E01-S03-G02
Shot: E01-S03-004
Character: C01
Scene Asset: S01
Prop: P01
```

进入生产后不要因为小修改重排全部 ID。

## 2. 顶层

```json
{
  "schema_version": "3.2",
  "project": {
    "title": "项目名",
    "aspect_ratio": "9:16",
    "target_runtime_seconds": 60,
    "mode": "faithful",
    "source_language": "zh-CN",
    "output_language": "zh-CN",
    "dialogue_language": "zh-CN",
    "target_video_model": "MiniMax H3",
    "workflow_profile": "storyboard | cinematic_previs",
    "visual_bible": {
      "status": "locked | draft | pending",
      "reference": null
    },
    "model_profile": {
      "name": "minimax-h3",
      "verified_at": "2026-10-03"
    }
  },
  "assets": {
    "characters": [],
    "scenes": [],
    "props": []
  },
  "episodes": []
}
```

`mode`：

- `faithful`
- `visual`
- `pacing`
- `story`

`source_language` / `output_language` 用于判断翻译后 timing 是否需要失效。

## 3. Asset

```json
{
  "id": "C01",
  "name": "角色名",
  "reference": "assets/characters/c01.png",
  "locked_traits": ["固定发型", "固定服装"],
  "status": "approved"
}
```

真实路径不存在时写 `null`。不要伪造路径。

若资产尚未制作，可：

```json
{
  "id": "C01",
  "name": "角色名",
  "reference": null,
  "locked_traits": [],
  "status": "pending"
}
```

## 3.1 Asset State Registry（cinematic_previs 可选）

base asset 解决 identity；state 解决剧情中的连续变化。

```json
"asset_states": [
  {
    "id": "C01-ST02",
    "asset_id": "C01",
    "costume_id": "C01-LOOK01",
    "condition": ["wet"],
    "injury": [],
    "location_context": "S01",
    "held_props": [],
    "locked_traits": []
  }
]
```

也可以为 Scene / Prop 建立状态 ID，例如 `S01-ST02`、`P03-ST04`。

完整规则见 `references/asset-state-matrix.md`。

## 4. Episode

```json
{
  "id": "E01",
  "title": "第一集",
  "target_runtime_seconds": 60,
  "hook_audit": {
    "opening": {
      "type": "information_gap",
      "source": "E01-S01-B01"
    },
    "ending": {
      "type": "threat_pending",
      "source": "E01-S05-B06",
      "note": "威胁已出现，但结果未知"
    }
  },
  "scenes": []
}
```

Hook 字段可选。

建议类型：

- `information_gap`
- `threat_pending`
- `secret_approaching`
- `choice_unresolved`
- `cognitive_reversal`
- `countdown`
- `action_unresolved`
- `result_only`
- `none`

`result_only` 允许存在，但 validator 可提示它不是未决型 hook。

## 5. Scene

```json
{
  "id": "E01-S01",
  "slugline": "INT. 仪式大厅 - NIGHT",
  "location_asset": "S01",
  "characters": ["C01", "C02"],
  "props": ["P01"],
  "entry_state": {},
  "exit_state": {},
  "story_contract": {
    "objective": "",
    "obstacle": "",
    "escalation": [],
    "information_release": [],
    "emotional_start": "",
    "emotional_end": "",
    "irreversible_change": "",
    "must_preserve": [],
    "authorized_flex": []
  },
  "director_plan": {},
  "beats": [],
  "shots": [],
  "generation_segments": []
}
```

### 5.1 director_plan

```json
{
  "dramatic_job": "让 C01 发现 P01 上的关键证据",
  "turn": "刻印暴露后，C01 意识到 C02 说谎",
  "visual_strategy": "先关系镜，证据出现后转 insert + reaction",
  "blocking_plan": "C01 画左桌边；C02 画右门边；C01 不跨桌",
  "axis_plan": "C01-C02 连线，保持南侧机位",
  "coverage_obligations": [
    "建立 C01/C02 左右关系",
    "看清 P01 刻印",
    "保留 C01 发现后的反应"
  ],
  "pacing": "neutral",
  "hook_role": "setup",
  "sequence_type": "investigation_reveal",
  "secondary_sequence_types": []
}
```

### 5.2 sequence_plan（除 combat 外）

```json
"sequence_plan": {
  "profile": "investigation_reveal",
  "sequence_goal": "让观众确认 P01 是关键证据，但幕后者仍未知。",
  "audience_question": "P01 能否证明 C02 在撒谎？",
  "sequence_beats": [
    {
      "id": "E01-S01-SQ01",
      "type": "evidence_found",
      "purpose": "让证据第一次变得可读",
      "source_beats": ["E01-S01-B01"],
      "visible_change": "P01 背面刻印被发现"
    }
  ],
  "spatial_plan": {},
  "information_plan": {},
  "rhythm_plan": ["search", "reveal", "reaction"],
  "camera_strategy": "证据 insert 后切发现者反应",
  "sound_strategy": "",
  "continuity_priorities": ["evidence_state", "knowledge_state"]
}
```

`sequence_plan.profile` 必须与主 `director_plan.sequence_type` 一致。

Sequence Beat 是导演层观看阶段，不替代 Narrative Beat。每个 Sequence Beat 应由一个或多个 Shot 的 `sequence_context.sequence_beat_ids` 认领。

### 5.3 sequence_type

v3.2 核心枚举：

`dialogue`, `confrontation_negotiation`, `emotional_intimacy`, `investigation_reveal`, `suspense_threat`, `horror_dread`, `stealth_infiltration`, `chase_escape`, `combat`, `physical_hazard_rescue`, `vehicle_action`, `disaster_survival`, `crowd_ensemble`, `comedy`, `montage_progression`, `performance_ritual`, `world_reveal_establishing`, `transition_travel`, `other`.

完整路由见 `references/sequence-router.md`。

### 5.4 combat_plan（仅战斗场）

当：

```json
"director_plan": {
  "sequence_type": "combat"
}
```

时，建议同时保存：

```json
"combat_plan": {
  "combat_goal": "C01 必须突破 C02 才能到达出口",
  "sequence_arc": "pressure -> reversal -> escalation -> finish",
  "participants": [
    {
      "character_id": "C01",
      "objective": "到达出口",
      "start_zone": "Z1",
      "start_facing": "screen-right",
      "condition": "uninjured",
      "key_prop": null
    }
  ],
  "arena": {
    "zones": [
      {"id": "Z1", "name": "门口"},
      {"id": "Z2", "name": "长桌左侧"},
      {"id": "Z3", "name": "长桌右侧"}
    ],
    "axis": "C01-C02 主交锋线",
    "screen_direction": "C01 left-to-right"
  },
  "combat_beats": [
    {
      "id": "E01-S04-CB01",
      "type": "pressure",
      "purpose": "C01 被迫离开出口方向",
      "advantage_before": "C01",
      "advantage_after": "C02",
      "zone_before": "Z1",
      "zone_after": "Z2",
      "range_before": "mid",
      "range_after": "close",
      "visible_result": "C01 被迫退到长桌左侧",
      "source_beats": ["E01-S04-B03"]
    }
  ],
  "rhythm_plan": ["setup", "exchange", "reversal", "breather", "finish", "aftermath"],
  "camera_strategy": "先 wide 建立空间，关键 reversal 再收近",
  "continuity_priorities": ["zone", "screen_direction", "range", "advantage", "prop_state"],
  "safety_note": "screen choreography only"
}
```

`combat_plan` 是 `director_plan` 的战斗子计划，不替代普通 Narrative Beat。

### Combat Beat type

推荐：

- `engage`
- `pressure`
- `reversal`
- `disarm_or_prop_change`
- `environment_shift`
- `separation`
- `reengage`
- `escalation`
- `save_or_interrupt`
- `finish`
- `aftermath`

`range_before/range_after` 仅用于银幕空间连续性：

- `far`
- `mid`
- `close`
- `grapple`

## 6. Beat

```json
{
  "id": "E01-S01-B01",
  "type": "information",
  "source_text": "她翻过徽章，看见背面的家族刻印。",
  "event": "C01 发现徽章刻印",
  "characters": ["C01"],
  "props": ["P01"],
  "dialogue": null,
  "must_preserve": true
}
```

常见 type：

- `action`
- `dialogue`
- `information`
- `reaction`
- `power_shift`
- `reveal`
- `hook`
- `resolution`

## 7. Shot

```json
{
  "id": "E01-S01-001",
  "scene_id": "E01-S01",
  "order": 1,
  "source_beats": ["E01-S01-B01"],
  "purpose": "让观众清楚读到刻印并看到 C01 的停顿",
  "director_obligation": "看清 P01 刻印",
  "cut_reason": "证据尺寸小，需要独立近景",
  "timecode_in": 0.0,
  "timecode_out": 3.0,
  "duration_seconds": 3.0,
  "shot_size": "close-up",
  "angle": "eye-level",
  "camera_movement": "static",
  "camera_position": "位于 C01-P01 轴线南侧，桌面高度",
  "lens_intent": "detail-isolation",
  "lighting_intent": "inherit visual bible",
  "composition": "P01 位于中央前景，C01 手部从画面左侧进入",
  "depth_layers": {
    "foreground": "C01 手部",
    "midground": "P01",
    "background": "soft hall texture"
  },
  "characters": ["C01"],
  "blocking": "C01 右手将 P01 翻到背面",
  "action": "刻印露出时手指停住",
  "performance": "由专注转为短暂停顿",
  "dialogue": [],
  "voiceover": [],
  "sound": ["金属轻擦声"],
  "assets": {
    "scene": "S01",
    "characters": ["C01"],
    "props": ["P01"]
  },
  "asset_state_refs": {
    "scene": "S01-ST01",
    "characters": ["C01-ST01"],
    "props": ["P01-ST02"]
  },
  "generation_constraints": [
    "no costume change",
    "P01 remains in C01 right hand"
  ],
  "start_state": {
    "C01": "画面外，仅右手进入画面",
    "P01": "正面朝上"
  },
  "end_state": {
    "C01": "右手停住",
    "P01": "背面朝上，刻印可见"
  },
  "handoff_from_previous": null,
  "continuity_notes": "下一镜保持 C01 视线向下",
  "risk": {
    "level": "low",
    "reasons": [],
    "fallback": null
  },
  "status": "planned"
}
```

第一镜 `handoff_from_previous` 可为 `null`。

### 7.1 Shot 时间码

v3 中：

```text
timecode_out - timecode_in = duration_seconds
```

`timecode_in/out` 表示集内/成片累计时间，不是 Segment 本地时间。

### 7.2 Sequence Context（非战斗镜头）

```json
"sequence_context": {
  "sequence_beat_ids": ["E01-S01-SQ01"],
  "state_start": {
    "evidence_state": "hidden",
    "knowledge_state": "uncertain"
  },
  "state_end": {
    "evidence_state": "visible",
    "knowledge_state": "confirmed"
  },
  "attention_target": "P01"
}
```

状态键由 profile 决定。相邻镜没有 `motivated_jump / time_jump / scene_cut` 时，上一镜 `state_end` 与下一镜 `state_start` 的共同键应保持一致。

### 7.3 Combat Context（战斗镜头可选/推荐）

战斗 Shot 可增加：

```json
"combat_context": {
  "combat_beat_ids": ["E01-S04-CB01"],
  "action_phase": "reaction",
  "zone_start": "Z1",
  "zone_end": "Z2",
  "range_start": "mid",
  "range_end": "close",
  "advantage_start": "C01",
  "advantage_end": "C02",
  "primary_exchange": ["C01", "C02"]
}
```

`action_phase` 推荐：

- `read_or_intent`
- `approach`
- `attack_attempt`
- `evade_or_block`
- `impact_or_near_impact`
- `reaction`
- `recovery_or_reposition`
- `aftermath`

不要把现实伤害技巧写入数据；这里追踪的是银幕动作状态。

## 8. Handoff

除 Scene 第一镜外推荐必填：

```json
{
  "from_shot_id": "E01-S01-001",
  "type": "reaction",
  "reason": "证据出现后切到 C01 的认知反应"
}
```

枚举：

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

## 9. Dialogue

```json
{
  "speaker": "C01",
  "text": "你早就知道？",
  "language": "zh-CN",
  "delivery": "压低声音",
  "timing_seconds": 1.8,
  "timing_source": "measured_tts",
  "overlap": false
}
```

`timing_source`：

- `measured_audio`
- `measured_tts`
- `scripted`
- `estimated_target_text`
- `estimated`
- `inherited_source`

跨语言时 `inherited_source` 非法。

旧字段 `timing_estimate_seconds` 在 v3 不推荐；迁移时改为 `timing_seconds` + 合适的 `timing_source`。

## 10. Voiceover

建议与 Dialogue 使用相同 timing 结构：

```json
{
  "text": "三天后，海水越过堤坝。",
  "language": "zh-CN",
  "timing_seconds": 2.4,
  "timing_source": "measured_tts",
  "overlap_with_dialogue": false
}
```

## 11. Coverage Exception

同一 Beat 被多个 shots 使用时：

```json
{
  "type": "reaction_coverage",
  "reason": "同一句对白延续到听者反应镜"
}
```

没有 exception 的重复覆盖应触发 warning。

## 12. Nonlinear Exception

若 Shot 有意倒序认领 Beat：

```json
{
  "nonlinear_exception": {
    "type": "flashback",
    "reason": "明确闪回"
  }
}
```

没有 exception 时，`source_beats` 应按 Scene Beat 顺序且连续。

## 13. Risk

```json
{
  "level": "medium",
  "reasons": [
    "two-character interaction",
    "small prop must remain readable"
  ],
  "fallback": "拆成道具 insert + 人物反应镜"
}
```

## 14. Generation Segment

v3：

```json
{
  "id": "E01-S01-G01",
  "scene_id": "E01-S01",
  "target_model": "MiniMax H3",
  "generation_mode": "Ref2VA",
  "duration_seconds": 8.0,
  "shot_ids": [
    "E01-S01-001",
    "E01-S01-002"
  ],
  "reference_assets": [
    {
      "label": "Picture 1",
      "asset_id": "C01",
      "purpose": "character_identity"
    },
    {
      "label": "Picture 2",
      "asset_id": "S01",
      "purpose": "environment"
    }
  ],
  "risk": {
    "level": "low",
    "reasons": []
  }
}
```

### 14.1 单一事实源

禁止 v3 这样写：

```json
"generation_segments": [
  {
    "shots": [
      {"id": "...完整 Shot..."}
    ]
  }
]
```

因为会形成第二份 Shot 事实。

### 14.2 Segment duration

必须满足：

```text
segment.duration_seconds
= sum(scene.shots[shot_id].duration_seconds)
```

### 14.3 Segment 本地 Cut 时间

不单独存储，按 `shot_ids` 顺序派生。

例如：

```text
shot A 3.0s → 0.00–3.00
shot B 5.0s → 3.00–8.00
```

最终 H3 Prompt Skill 再把这组本地 cut 时间写入模型 prompt。

## 15. Reference Assets

推荐 purpose：

- `character_identity`
- `environment`
- `prop_identity`
- `costume`
- `style`
- `action_reference`
- `camera_reference`
- `keyframe`
- `audio_reference`

reference label 进入生产后保持稳定。

若视频/音频参考需要验证 H3 时长，可额外记录：

```json
{
  "label": "Video 1",
  "asset_id": "V01",
  "purpose": "action_reference",
  "duration_seconds": 6.2
}
```

## 16. Asset 引用

Shot：

```json
"assets": {
  "scene": "S01",
  "characters": ["C01"],
  "props": ["P01"]
}
```

如果顶层 asset registry 已存在，引用 ID 应能解析。资产仍 pending 时也使用稳定 ID，不要每镜改名字。

## 17. Markdown 映射

| Markdown | JSON |
|---|---|
| 镜号 | `id` |
| 生成段 | 由 Segment `shot_ids` 反查 |
| 场次 | `scene_id` |
| 时间码 | `timecode_in/out` |
| 时长 | `duration_seconds` |
| 原剧本节拍 | `source_beats` |
| 镜头职责 | `purpose` |
| 切点理由 | `cut_reason` |
| 景别/角度 | `shot_size` + `angle` |
| 运镜 | `camera_movement` |
| 画面与构图 | `composition` |
| 人物/调度 | `characters` + `blocking` |
| 动作/表演 | `action` + `performance` |
| 台词/旁白 | `dialogue` + `voiceover` |
| 声音 | `sound` |
| 资产 | `assets` |
| 首帧 | `start_state` |
| 尾帧 | `end_state` |
| 衔接合同 | `handoff_from_previous` |
| 连续性/风险 | `continuity_notes` + `risk` |

## 18. Runtime

Scene/episode 的累计时间以 canonical shots 为准。

如果用户给出锁定总时长，建议：

```json
"runtime_lock": true
```

Validator 可以把 mismatch 视为 error；未锁定时视为 warning。

## 19. v2 → v3

详细迁移见 `references/migration-v2-v3.md`。

最关键：

```text
v2 Segment.shots
→ v3 Scene.shots + Segment.shot_ids
```

并将旧的：

```text
timing_estimate_seconds
```

转为：

```text
timing_seconds + timing_source
```

## 19.1 Cinematic Previs Derived Artifacts

以下属于 **derived artifacts**，不作为第二套剧情事实源：

```text
animatic-plan.json
previs-report.md
shot-packets/<SHOT_ID>.json
pickup-requests.json
```

它们必须从 locked script / storyboard / asset states / visual bible 派生。

Shot Production Packet 字段见 `references/shot-production-packet.md`；Animatic Gate 见 `references/animatic-previs.md`。

## 20. 推荐文件

```text
storyboard.md
storyboard.json
```

只有人工一次性评审时可只交 Markdown；进入关键帧、视频 Prompt 或自动化流水线时建议同时交 JSON。
