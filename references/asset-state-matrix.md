# Asset State Matrix

AI 视频连续性不能只管理“角色是谁”，还必须管理“角色此刻处于什么状态”。

核心模型：

```text
Asset
× Costume
× Physical State
× Location
× Prop State
× Time
× Damage / Wetness / Dirt
```

## 1. Character State

示例：

```text
C01-ST01  normal / dry / uninjured
C01-ST02  storm-wet
C01-ST03  injured-arm
C01-ST04  underwater
```

建议：

```json
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
```

## 2. Environment State

```text
S01-ST01 storm / intact rail
S01-ST02 storm / damaged rail
S02-ST01 ocean surface
S03-ST01 underwater
```

## 3. Prop State

例如：

```text
P01-ST01 intact / C01 right hand
P01-ST02 dropped / floor Z3
P01-ST03 damaged
```

## 4. State Transition

状态变化必须来自 Narrative Beat / Sequence Beat / Combat Beat。

不允许：

```text
Shot 10: dry
Shot 11: soaked
```

除非中间有：

- 入水；
- 暴雨暴露；
- time jump；
- explicit state transition。

## 5. Shot 引用

推荐：

```json
"asset_state_refs": {
  "characters": ["C01-ST02", "C02-ST01"],
  "scene": "S01-ST01",
  "props": ["P03-ST01"]
}
```

下游生成优先读取 state ID，而不是只读取 base asset ID。

## 6. 为什么比普通 Asset List 更重要

普通 Asset List 解决 identity。

State Matrix 解决：

- 换装；
- 湿身；
- 伤势；
- 污渍；
- 道具换手；
- 环境损坏；
- 昼夜变化；
- underwater / surface 等剧情状态。

这类变化正是 AI 视频连续性最容易漂移的部分。
