# AI Video Shot Transition Contract v4

本文件解决 AI 视频生产中最常见的失败：

> 单镜本身好看，但下一镜不是从上一镜真正结束的位置、姿态和动作阶段继续。

本文件不生成 MiniMax H3 / Kling / Veo 的最终 Prompt；它定义下游 Prompt Skill 必须读取的导演连续性合同。

## 1. 核心原则

AI 视频 Shot 不能只描述“这一镜发生什么”，还必须知道：

```text
上一镜结束世界状态
→ 哪些状态必须继承
→ 当前镜头首帧锚点
→ 当前动作
→ 当前镜头结束世界状态
```

因此生产级 Shot 至少应提供：

- `start_state`
- `action`
- `end_state`
- `handoff_from_previous`
- 连续动作时的 `action_state`

## 2. Start-frame Anchor

`start_state` 只写当前镜头首帧必须成立的连续性事实。

推荐优先级：

1. 人物 zone / body position / facing；
2. 正在进行的 action phase；
3. 关键道具 holder / hand / state；
4. 关键环境状态；
5. 只有会影响连续性的 gaze / wetness / injury / damage。

不要把完整资产描述复制进 `start_state`。

## 3. End-frame Anchor

`end_state` 是下一镜可继承的尾帧状态。

必须明确：

- 人物最后在哪里；
- 身体处于什么阶段；
- 关键道具在哪里；
- 动作做到哪一步；
- 哪个信息/反应已经完成；
- 哪些环境状态已经改变。

如果尾帧状态无法成为下一镜输入，说明 Shot 还没有真正设计完成。

## 4. Handoff Contract

连续切镜示例：

```json
{
  "handoff_from_previous": {
    "from_shot_id": "E01-S03-004",
    "type": "match_on_action",
    "reason": "推力已经发生，在失衡动作中切到侧面。",
    "state_inheritance": [
      "characters.C01.zone",
      "characters.C02.zone",
      "characters.C01.body_position",
      "props.P01.holder",
      "environment.location"
    ]
  }
}
```

`state_inheritance` 是 AI 视频交接的关键：下游模型 Prompt 必须把这些状态当成不可随意重置的输入事实。

## 5. Action State

对于跨镜连续动作：

```json
{
  "action_state": {
    "action_id": "ACT-RAIL-PUSH-01",
    "phase_start": "contact",
    "phase_end": "execution"
  }
}
```

下一镜继续：

```json
{
  "action_state": {
    "action_id": "ACT-RAIL-PUSH-01",
    "phase_start": "execution",
    "phase_end": "result"
  }
}
```

这样下游不会把“推人”重新从准备动作开始，也不会直接跳到完全无关的姿态。

## 6. 什么时候拆镜

不要按句子拆镜。满足以下任一条件才优先切：

- 注意力中心真正变化；
- 需要独立读取证据/细节；
- 反应本身承担剧情信息；
- geography 需要重建；
- 当前构图无法同时完成两个关键叙事任务；
- 单镜动作/口型/多角色/运镜负载过高；
- 模型无法可靠执行当前连续动作。

如果一个连续动作在同一机位中可以清楚完成，优先保持为一个 Shot。

## 7. 什么时候不拆镜

例如：

```text
角色走到电话旁 → 拿起电话 → 直接求救
```

如果 geography 已清楚、动作简单、没有独立反应/证据任务，可以作为一个连续 Shot，不需要机械拆成“走过去”和“求救”两镜。

v4 的目标是 **最少但足够的镜头**。

## 8. Generation Segment

Segment 不等于 Shot，但必须满足：

- 同一 Scene；
- geography 连续；
- 状态继承清楚；
- 不包含互相冲突的多组动作；
- 不把明显 discontinuity 硬塞进一个模型调用；
- Segment 内 Shot 顺序与 canonical Storyboard 一致。

对于高风险动作，优先：

```text
一个 Segment
≈ 一个清楚动作目标
≈ 1–2 个关键状态变化
```

不要为了“多参生视频一次做更多”而牺牲动作可读性。

## 9. 长镜头

长镜头不是错误。

允许在一个连续 Shot 内完成多个小动作，只要：

- 时空连续；
- 主体和叙事目标稳定；
- geography 可读；
- camera path 简单；
- 每个动作自然承接；
- 不要求模型同时精确完成多角色复杂互动、细道具、口型和复杂运镜。

长镜头若失败，fallback 才是拆成更稳定的 Shot。

## 10. 下游 Prompt 编译

模型专用 Skill 应读取：

```text
visual/asset locks
+ previous end state
+ state_inheritance
+ current start state
+ action_state
+ current action
+ current end state
+ camera/composition
+ do_not_change
```

而不是只把 Storyboard 的“动作描述”复制成 Prompt。

## 11. 失败诊断

生成后若出现：

- 人物位置重置；
- 道具换手；
- 动作重新开始；
- 角色突然面对反方向；
- 上一镜已发生的结果被撤销；

优先回查：

1. `end_state` 是否明确；
2. `state_inheritance` 是否覆盖关键状态；
3. `start_state` 是否真的继承；
4. `action_state` 是否保持同一 action_id；
5. 是否本应合并为一个 Shot；
6. 是否 Segment 负载过高。

不要第一反应只增加形容词或负面 Prompt。
