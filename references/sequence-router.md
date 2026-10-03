# Sequence Planning Router

本文件是 `script-to-storyboard-table` 的“场型路由层”。

核心原则：

> **先判断这一段戏在导演层属于什么 Sequence Type，再调用对应规划语法，最后才拆 Beat / Shot。**

同样是两个人站在房间里：
- 谈判戏关注 power / information；
- 爱情戏关注 emotional distance / intimacy；
- 悬疑戏关注 withheld information / threat；
- 喜剧戏关注 setup / expectation / payoff；
- 战斗戏关注 geography / advantage / action phase。

不能只因为“地点相同、人物相同”就使用同一套镜头逻辑。

---

## 1. 总流程

```text
Scene / Sequence
→ Sequence Type Router
→ Director Plan
→ Type-specific Sequence Plan
→ Narrative Beat
→ Atomic Shot
→ Handoff
→ Timing / Segment
→ Type-specific Audit
```

战斗场为：

```text
Director Plan
→ Combat Plan
→ Combat Beat
→ Action Phase
→ Atomic Shot
```

---

## 2. sequence_type

推荐核心枚举：

- `dialogue`
- `confrontation_negotiation`
- `emotional_intimacy`
- `investigation_reveal`
- `suspense_threat`
- `horror_dread`
- `stealth_infiltration`
- `chase_escape`
- `combat`
- `physical_hazard_rescue`
- `vehicle_action`
- `disaster_survival`
- `crowd_ensemble`
- `comedy`
- `montage_progression`
- `performance_ritual`
- `world_reveal_establishing`
- `transition_travel`
- `other`

如果一场同时包含多个类型，使用：

```json
{
  "sequence_type": "suspense_threat",
  "secondary_sequence_types": ["investigation_reveal"]
}
```

主类型决定主要规划语法；次类型只补充必要规则。

不要因为一场戏有一句笑话就标为 comedy，也不要因为有人跑两步就标为 chase。

---

## 3. Router 判断顺序

先问这一段戏的**主要观众任务**：

### A. 观众主要在听人物交换信息/立场？

- 普通交流 → `dialogue`
- 权力争夺、逼问、交易、审讯 → `confrontation_negotiation`
- 关系靠近/疏远、告白、分手、亲密情绪 → `emotional_intimacy`

### B. 观众主要在等待“答案/威胁/发现”？

- 搜证、拼线索、发现事实 → `investigation_reveal`
- 已知或半知威胁，等待发生 → `suspense_threat`
- 恐惧来自未知空间、负空间、不可确认存在 → `horror_dread`
- 核心目标是不被发现 → `stealth_infiltration`

### C. 观众主要在追踪空间移动和即时目标？

- 追/逃 → `chase_escape`
- 连续攻防 → `combat`
- 坠落、火灾、塌陷、溺水等即时物理危险 / 救援 → `physical_hazard_rescue`
- 车辆本身是主要运动主体/危险源 → `vehicle_action`

### D. 观众主要在理解大尺度状态变化？

- 灾害、多点危机、生存阶段 → `disaster_survival`
- 多角色同时存在、关系网/群体反应重要 → `crowd_ensemble`
- 世界、地点、规模、规则首次重要呈现 → `world_reveal_establishing`

### E. 观众主要通过剪辑节奏理解意义？

- 笑点结构 → `comedy`
- 时间压缩、训练、建设、准备、生活变化 → `montage_progression`
- 舞台、演讲、仪式、比赛、演出 → `performance_ritual`
- 从 A 到 B 的必要过渡 / 旅行 → `transition_travel`

---

## 4. Generic Sequence Plan

除简单 dialogue / transition 外，建议在 Scene 中增加：

```json
"sequence_plan": {
  "profile": "investigation_reveal",
  "sequence_goal": "观众在本段结束前确认 C01 找到关键证据，但仍不知道幕后者身份。",
  "audience_question": "P03 是否证明 C02 在撒谎？",
  "entry_condition": {},
  "exit_condition": {},
  "sequence_beats": [],
  "spatial_plan": {},
  "information_plan": {},
  "rhythm_plan": [],
  "camera_strategy": "",
  "sound_strategy": "",
  "continuity_priorities": [],
  "failure_modes": []
}
```

不是所有 profile 都需要所有字段。

---

## 5. Sequence Beat

Sequence Beat 与 Narrative Beat 不同：

- Narrative Beat：原剧情事实变化；
- Sequence Beat：导演层的观看/节奏阶段。

例如追逐戏：

```text
acquire target
→ pursuit begins
→ gap closes
→ obstacle
→ temporary loss
→ reacquire
→ escape / capture
```

这些阶段可以映射多个 Narrative Beats。

建议：

```json
{
  "id": "E01-S03-SQ01",
  "type": "gap_closes",
  "purpose": "让追击者第一次明显逼近",
  "source_beats": ["E01-S03-B03", "E01-S03-B04"],
  "visible_change": "C02 与 C01 的距离由 far 变为 mid"
}
```

---

## 6. 类型不能替代剧情

Sequence Profile 负责回答：

- 观众现在最需要知道什么？
- 哪个状态必须被持续追踪？
- 何时切镜最有效？
- 什么信息不能过早泄露？
- 什么镜头属于必要 coverage？
- 这一类型最常见的连续性错误是什么？

它不负责：

- 自动增加反转；
- 自动增加惊吓；
- 自动增加笑点；
- 自动增加爱情动作；
- 自动增加灾难；
- 改变用户原剧情。

---

## 7. 复杂 Scene 的分段

一场戏可能发生 profile 变化：

```text
dialogue
→ confrontation_negotiation
→ combat
→ aftermath dialogue
```

如果变化明显，应拆成多个 **Sequence Block**，即使仍属于同一 Scene：

```text
E01-S02-Q01 dialogue
E01-S02-Q02 confrontation
E01-S02-Q03 combat
E01-S02-Q04 aftermath
```

不要让一个 `sequence_type` 强行解释整场完全不同的导演任务。

---

## 8. Profile 优先级

如果多个 profile 同时成立，按“最支配镜头组织的机制”选择主类型。

例如：

- 恐怖片里逃跑：如果重点是路线与距离 → chase；
- 逃跑过程中怪物不可见、重点是未知威胁 → horror/suspense；
- 恋爱戏里争吵：如果重点是关系权力变化 → confrontation；
- 灾难里两人打斗：局部 block 用 combat，大场总体仍可属 disaster；
- 演唱会后台追凶：可拆 performance block + investigation block。

---

## 9. AI 视频场型路由

不同 profile 的 AI 风险也不同：

- dialogue：口型 + reaction timing；
- confrontation：多人 blocking + power shifts；
- emotional：微表情 + body distance；
- investigation：小道具/文字可读性；
- suspense/horror：连续空间 + visibility control；
- stealth：视线/遮挡/位置；
- chase：screen direction + route + speed；
- combat：肢体 + identity + action phase；
- disaster：多人 + 环境状态变化；
- crowd：身份数量 +群体运动；
- comedy：精确 timing；
- montage：镜头数量 + 风格/时间状态变化；
- performance：同步节奏 + 多主体；
- transition：场景身份变化。

Segment 拆分必须根据 profile 风险，而不是只看秒数。

---

## 10. Router Quality Gate

- [ ] sequence_type 反映主要导演任务，而不是题材标签
- [ ] 混合场型已决定主/次类型或拆 Sequence Block
- [ ] 复杂类型存在 sequence_plan / combat_plan
- [ ] Sequence Beat 与 Narrative Beat 可以追溯
- [ ] 类型规划没有擅自增加剧情
- [ ] type-specific continuity 已进入 Shot / Handoff
- [ ] Segment 边界考虑了场型状态变化
