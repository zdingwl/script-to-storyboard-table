# Migration v3.3 → v4.0

v4 不要求重做剧情分析。升级重点是把“人工能看懂的连续性”变成“下游和 validator 能执行的连续性”。

## 1. schema_version

```json
"schema_version": "4.0"
```

Validator 仍兼容 3.0 / 3.2；只有 4.0 启用新的硬连续性规则。

## 2. start_state / end_state

v3 可以写自由文本：

```json
"start_state": {
  "C01": "长桌左侧"
}
```

v4 推荐改为稳定嵌套对象：

```json
"start_state": {
  "characters": {
    "C01": {
      "zone": "table-left",
      "body_position": "standing"
    }
  },
  "props": {},
  "environment": {
    "location": "S01"
  }
}
```

只迁移会影响下一镜的状态，不复制完整资产定义。

## 3. handoff_from_previous

v3：

```json
{
  "from_shot_id": "E01-S01-001",
  "type": "reaction",
  "reason": "..."
}
```

v4 连续切镜增加：

```json
"state_inheritance": [
  "characters.C01.zone",
  "props.P01.holder"
]
```

`motivated_jump` / `time_jump` / `scene_cut` 可不提供完整 inheritance，但必须说明原因。

## 4. 连续动作

只有真正跨镜的连续物理动作需要增加：

```json
"action_state": {
  "action_id": "ACT-01",
  "phase_start": "contact",
  "phase_end": "execution"
}
```

不要给普通对话机械添加 action_state。

## 5. 推荐迁移顺序

1. 保留现有 Scene / Beat / Director / Sequence / Combat 数据；
2. 把关键 Shot 的 start/end state 结构化；
3. 为每个连续 handoff 添加最小 state_inheritance；
4. 为跨镜动作添加 action_state；
5. 运行 validator；
6. 修复 continuity error；
7. 做 Animatic / Previs；
8. Previs Gate 通过后再生成 Shot Production Packet。

## 6. 不要做的事

- 不要为了 v4 把每一个资产属性复制进每个 Shot；
- 不要把固定外观当跨镜动态状态；
- 不要给所有镜头强行增加动作 phase；
- 不要因为 validator 报错就无脑加镜；
- 不要把 motivated_jump 当成逃避连续性设计的默认方案。

