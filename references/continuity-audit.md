# Continuity Audit v4

本文件定义 **Draft Storyboard → Approved Storyboard** 之间的连续性审计。

目标不是增加镜头数量，而是回答一个更严格的问题：

> 上一镜的可见世界状态，能否在下一镜的首帧被继续读取；若发生变化，观众能否看懂变化如何发生？

## 1. 审计位置

```text
Script Lock
→ Director / Sequence Plan
→ Geography / Blocking
→ Beat / Coverage
→ Draft Storyboard
→ Continuity Audit
→ Continuity Repair
→ Approved Storyboard
→ Animatic / Previs
→ AI Video Shot Production Packet
```

Storyboard 生成完成后必须先进入 Continuity Audit。发现断裂时先修 Shot / Handoff / Blocking，不先通过增加 Prompt 字数解决。

## 2. 三层连续性

### 2.1 Narrative continuity

检查：

- must-preserve Beat 是否完整；
- cause → effect 是否成立；
- action → reaction 是否有落点；
- 结果镜之前是否缺原因；
- 原因镜之后是否缺结果；
- 位置或状态突变是否有剧情依据。

### 2.2 World-state continuity

v4 的 `start_state` / `end_state` 使用机器可读对象。只记录下游真正需要继承的连续性事实，不复制整份角色资产。

推荐结构：

```json
{
  "characters": {
    "C01": {
      "zone": "deck-rail-left",
      "body_position": "standing",
      "facing": "sea",
      "gaze_target": "C02"
    }
  },
  "props": {
    "P01": {
      "holder": "C01",
      "hand": "right",
      "state": "closed"
    }
  },
  "environment": {
    "location": "S01",
    "time": "night",
    "weather": "storm"
  }
}
```

不要在这里重复固定脸型、发色、服装设计等 Visual Bible / Asset Registry 已锁定的事实；这里只记录会随剧情变化、且下一镜需要继承的状态。

## 3. Handoff 的 state_inheritance

v4 的连续切镜必须显式声明需要从上一镜尾状态继承的 dot paths：

```json
{
  "handoff_from_previous": {
    "from_shot_id": "E01-S01-001",
    "type": "reaction",
    "reason": "证据露出后切发现者反应。",
    "state_inheritance": [
      "characters.C01.zone",
      "characters.C01.body_position",
      "props.P01.holder",
      "props.P01.hand",
      "props.P01.orientation",
      "environment.location"
    ]
  }
}
```

Validator 将读取：

```text
previous.end_state[path]
==
current.start_state[path]
```

以下 Handoff 可以不要求完整继承：

- `motivated_jump`
- `time_jump`
- `scene_cut`

但仍必须在 `reason` 中说明为什么允许不连续。

## 4. Action State

涉及明显连续物理动作时，为 Shot 增加：

```json
{
  "action_state": {
    "action_id": "ACT-PUSH-01",
    "phase_start": "contact",
    "phase_end": "execution"
  }
}
```

通用 phase：

```text
prepare
→ approach
→ contact
→ execution
→ result
→ reaction
→ recovery
→ aftermath
```

不是所有动作都需要经过全部 phase；但同一个 `action_id` 跨镜时：

- phase 不能倒退；
- 无明确 jump 时不要跨过多个观众必须理解的 phase；
- `match_on_action` 必须继续同一个 `action_id`；
- 复杂动作优先减少运镜复杂度，而不是同时增加动作和 camera 负载。

## 5. Geography Audit

逐 Sequence 建立空间锚点：

- zone / anchor；
- 人物初始位置；
- 出入口；
- 关键障碍；
- 高低差；
- 主要移动路径；
- 180° axis；
- screen direction。

逐镜检查：

- 人物是否无解释换区；
- 左右关系是否无意反转；
- 移动方向是否突然相反；
- 角色交叉换位后是否重建空间；
- insert / cutaway 返回时主动作是否偷偷变化。

## 6. Character Audit

对每个在相邻镜持续存在的人物检查：

- zone / anchor；
- body position；
- facing；
- gaze target；
- action phase；
- prop ownership；
- costume state；
- wetness / dirt / injury / damage state；
- 已获得的信息状态。

如果某项变化属于当前 Shot 的动作结果，写进 `end_state`；如果变化发生在镜头之间，则必须有明确 jump / transition 原因。

## 7. Prop Audit

关键道具检查：

- holder；
- hand；
- location；
- orientation；
- open / closed；
- full / empty；
- intact / damaged；
- visible / hidden。

“道具突然换手”属于高优先级连续性错误。

## 8. Environment Audit

检查：

- time；
- weather；
- light direction；
- door/window state；
- vehicle position；
- damage stage；
- water/fire/smoke 等环境阶段。

环境状态变化应由事件、时间跳跃或明确 transition 导致。

## 9. Editing / Camera Audit

连续性不是要求每镜机位相同。Camera 可以变化，但变化必须可读。

检查：

- 180° axis；
- eyeline match；
- screen direction；
- 30° jump-cut 风险；
- match on action；
- insert return；
- cause → effect；
- action → reaction；
- sound bridge。

如果两个相邻 Shot 能安全合并且合并后不损害信息、动作、表演或节奏，应优先合并，避免机械碎切。

## 10. Continuity Repair 顺序

出现断裂时按以下顺序修复：

1. 修正下一镜 start_state，使其继承上一镜 end_state；
2. 修正 blocking / action phase；
3. 调整切点为 match-on-action / reaction / eyeline；
4. 合并不必要的碎镜；
5. 必要时补一个真正缺失的动作/空间镜；
6. 只有剧情确实允许省略时使用 motivated_jump；
7. 若仍不可读，再回到 Director / Sequence Plan。

不要默认“多加一个镜头”就是修复。

## 11. 通过标准

Continuity Audit 通过至少满足：

- 所有连续切镜有合法 handoff；
- v4 连续切镜有非空 `state_inheritance`；
- state_inheritance 对应的上一镜尾状态与下一镜首状态相同；
- 同一连续动作不倒退；
- 关键动作没有无法理解的相位跳跃；
- geography / screen direction / eyeline 可读；
- 关键道具、服装、伤势、环境状态无漂移；
- 不存在可以无损删除的明显冗余碎镜。

通过后 Storyboard 状态才可从 `draft` 进入 `approved_for_previs`。
