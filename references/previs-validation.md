# Previs Validation Gate v4

本文件定义 Storyboard 在进入正式 AI 视频生成前的最终导演审片门。

## 1. 两个不同质量门

```text
Draft Storyboard
→ Continuity Audit
→ Continuity Repair
→ Approved Storyboard
→ Animatic / Previs
→ Previs Validation Gate
→ Production Ready
```

**Storyboard 通过**：静态镜头逻辑成立。  
**Previs 通过**：把镜头放进真实时间顺序后，场面仍然清楚、连续、可剪。

两者不能合并成一次检查。

## 2. Gate A — Story / Causality

必须满足：

- must-preserve Beat 全覆盖；
- cause → effect 可理解；
- action → reaction 有必要落点；
- 没有未经授权改剧情；
- hook 没有被镜头顺序提前泄底；
- 结果不会无来源出现。

## 3. Gate B — Geography / Blocking

必须满足：

- 第一处需要空间理解的位置已经建立；
- 人物 zone / route 清楚；
- 180° axis 有定义或有意越轴；
- 角色换位有可读过程；
- screen direction 连续；
- 关键出入口/障碍/高低差没有漂移。

## 4. Gate C — Shot Continuity

必须满足：

- `previous.end_state → handoff → current.start_state` 成立；
- v4 连续切镜的 `state_inheritance` 通过；
- action_state 不倒退；
- match-on-action 继续同一 action_id；
- insert/cutaway 返回时主动作状态没有偷偷变化；
- 关键人物/道具/伤势/湿度/环境状态连续。

任何高优先级状态断裂都应标记 `revise`，而不是进入生产。

## 5. Gate D — Timing / Performance

放入时间线后检查：

- dialogue / VO 能说完；
- 反应有时间读；
- 关键动作不是“看不到就结束”；
- establishing 不过长；
- 相邻镜时长不机械一致；
- climax 前后有节奏对比；
- 目标语言改变后 timing 已重算。

## 6. Gate E — Coverage / Editability

检查：

- 是否缺关键 cause；
- 是否缺关键 effect；
- 是否缺 reaction；
- 是否存在无意义重复 coverage；
- 两镜是否应该合并；
- 是否出现没有理由的 jump cut；
- sound bridge 是否可执行；
- Sequence Beat / Combat Beat 是否都能在剪辑里读到。

## 7. Gate F — AI Generation Readiness

每个进入正式生成的 Shot / Segment 检查：

- references 已绑定；
- Visual Bible / Asset State 已锁；
- start/end state 完整；
- state_inheritance 完整；
- action_state（需要时）完整；
- camera / composition 不是互相冲突的多任务；
- do_not_change 可从 canonical state 派生；
- fallback 已为 medium/high risk Shot 定义；
- Segment 没有超过模型能力边界或动作复杂度预算。

## 8. Gate 状态

统一使用：

```json
{
  "previs_gate": {
    "status": "pass | revise | blocked",
    "issues": [],
    "required_pickups": [],
    "approved_runtime_seconds": 0
  }
}
```

### pass

可以进入正式逐镜/逐 Segment 生成。

### revise

当前问题可通过修改 Storyboard / timing / blocking / handoff 修复。

### blocked

缺少必要剧情事实、资产、关键参考或用户决定，无法可靠进入生产。

## 9. Issue 优先级

### blocker

- 核心因果缺失；
- Scene geography 无法理解；
- 连续动作断裂导致事件意义改变；
- 关键角色/道具状态冲突；
- 必要资产完全缺失。

### major

- 位置跳变；
- 动作 phase 跳跃；
- 反应缺失；
- timing 明显不成立；
- Segment 明显过载。

### minor

- 景别节奏单调；
- 可优化的重复 coverage；
- 声音桥可增强；
- 非关键构图连续性。

## 10. Repair Loop

```text
issue
→ 找到最早发生断裂的 Shot
→ 判断是 state / action / geography / timing / coverage 问题
→ 做最小修复
→ 重新运行 deterministic validator
→ 重新进入 Animatic/Previs
```

不要从最后一个表现异常的镜头开始盲目重写整场。

## 11. Production-ready 条件

只有以下条件同时成立才建议生成正式视频：

- deterministic validator 无 error；
- strict 模式无未接受 warning；
- Continuity Audit 通过；
- Previs Gate = pass；
- medium/high risk Shot 有 fallback；
- Shot Production Packet 可以从 canonical storyboard 无歧义派生。

