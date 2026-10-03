# Combat Planning Reference

本文件用于战斗、近身冲突、持械对抗、多人混战等需要连续动作编排的场景。

它只负责**银幕动作的叙事、空间、镜头和连续性规划**。真实拍摄中的动作设计、安全距离、威亚、保护装备、武器道具和演员训练必须由合格的动作指导/特技团队负责；本 Skill 不提供现实伤害技巧。

## 1. 战斗场不是“动作词列表”

不要按：

```text
打一拳 → 踢一下 → 再打一拳 → 倒地
```

机械拆镜。

战斗场首先是一段小型剧情，应至少存在：

```text
目标
→ 初始优势
→ 交锋
→ 权力变化 / 反转
→ 升级
→ 决定性节点
→ 结果 / 后果
```

StudioBinder 的 fight-scene storyboard 方法同样强调：先明确动作编排/排练，再决定哪些动作应该保持 wide、哪些需要 medium/close，以及 camera 如何配合，而不是摄影机反过来支配动作。

## 2. 何时启用 Combat Plan

满足任一条件时，在 Director Plan 后增加 `combat_plan`：

- 两名或以上角色发生连续肢体冲突；
- 有明确攻防、追击、擒抱、夺取、推撞等连续动作；
- 有持械/道具参与的战斗；
- 一对多 / 多方混战；
- 战斗结果会改变人物位置、伤势、武器/道具状态或剧情权力关系；
- 用户明确要求“打戏、战斗分镜、动作戏、武打、混战”。

单次推搡、扇耳光、突然一拳等短动作可继续用普通 Action Phase，不必强制建立完整 Combat Plan。

## 3. Combat Plan 数据结构

建议：

```json
{
  "combat_plan": {
    "combat_goal": "这场战斗在剧情上必须完成什么",
    "sequence_arc": "pressure -> reversal -> escalation -> finish",
    "participants": [],
    "arena": {},
    "combat_beats": [],
    "rhythm_plan": [],
    "camera_strategy": "",
    "continuity_priorities": [],
    "safety_note": "screen choreography only"
  }
}
```

Combat Plan 不是替代 Director Plan，而是战斗场的子计划。

## 4. Combat Goal

首先回答：

> 为什么必须打这一场？

可接受：

- C01 必须突破 C02 才能离开房间；
- C01 从占优变为被压制，建立 C02 的威胁等级；
- C01 为保护 P01 被迫拖延对手；
- 战斗的真正作用是暴露 C02 身份，而不是决定胜负。

不合格：

> 很燃、很帅、打得激烈。

如果战斗不改变剧情、关系、位置、信息或角色状态，检查它是否只是冗余 spectacle。

## 5. Participants State

每名战斗参与者至少记录：

```json
{
  "character_id": "C01",
  "objective": "到达出口",
  "start_zone": "Z1",
  "start_facing": "screen-right",
  "condition": "uninjured",
  "key_prop": null,
  "end_condition_target": "forced_to_ground"
}
```

重点是银幕连续性，而不是现实格斗能力。

追踪：

- 所在 zone；
- 面朝方向；
- 与主要对手的距离级别；
- 是否站立 / 倒地 / 被限制移动；
- 关键道具/武器是否持有、在哪只手；
- 伤势/疲劳/污渍的可见状态；
- 当前优势方。

## 6. Arena Map

战斗空间必须先分区。

示例：

```text
Z1 门口
Z2 长桌左侧
Z3 长桌右侧
Z4 窗边
Z5 楼梯口
```

记录：

- entrance / exit；
- 固定障碍物；
- 高低差；
- 可被剧情使用的环境物；
- 易遮挡视线的位置；
- 角色允许经过的路径；
- 哪些区域尚未向观众建立。

战斗中人物从 Z1 突然出现在 Z4，若没有移动、切时或重新建立空间，应视为连续性错误。

## 7. Combat Beat

Combat Beat 不是“一拳”。

它是一次**战斗状态发生有意义变化**。

常见类型：

- `engage`：正式进入交锋；
- `pressure`：一方持续迫使另一方退位；
- `reversal`：优势方改变；
- `disarm_or_prop_change`：关键道具控制权变化；
- `environment_shift`：战斗转移到新区域/高低层；
- `separation`：双方拉开并重置；
- `reengage`：再次进入；
- `escalation`：威胁等级提高；
- `save_or_interrupt`：第三方/事件改变局面；
- `finish`：决定性节点；
- `aftermath`：结果和反应。

示例：

```json
{
  "id": "E01-S04-CB03",
  "type": "reversal",
  "purpose": "让 C02 从被逼退转为重新掌握主动",
  "advantage_before": "C01",
  "advantage_after": "C02",
  "zone_before": "Z2",
  "zone_after": "Z3",
  "range_before": "mid",
  "range_after": "close",
  "visible_result": "C01 被迫退到长桌另一侧",
  "source_beats": ["E01-S04-B05"]
}
```

一个 Combat Beat 通常可以包含多个简单动作，但必须有一个清楚的状态结果。

## 8. Action Phase

Combat Beat 再拆成必要的动作阶段：

```text
read / intent
→ approach
→ attack attempt
→ evade / block / intercept
→ impact or near-impact cue
→ reaction
→ recovery / reposition
```

不要求每阶段一个 Shot。

重点是：

- 观众知道动作从哪里来；
- 关键碰撞/变化可读；
- 结果不是凭空出现；
- 下一动作从上一状态自然开始。

## 9. Impact Readability

银幕上一个重要“打击/碰撞”至少要让观众读到三件事：

```text
预备 / 来向
→ 接触感或接触暗示
→ 结果 / 反应
```

可以通过：

- 构图；
- 运动方向；
- 表演反应；
- 遮挡；
- cut on action；
- 声音；
- 环境反馈；

建立冲击感。

不要求真实接触，也不应以真实击打作为镜头成立条件。

连续只拍“结果”，会像动作跳帧；连续只拍“接触”，又会失去空间和因果。

## 10. Advantage State

每个 Combat Beat 记录：

```text
advantage_before
advantage_after
```

优势不只表示“谁更强”，也可以是：

- 谁控制出口；
- 谁控制关键道具；
- 谁占据高处；
- 谁有行动自由；
- 谁被迫防守；
- 谁成功保护目标。

战斗镜头的节奏应围绕这些变化组织，而不是平均分配给每次动作。

## 11. Range Band

只为镜头/空间连续性使用：

- `far`：尚未直接接触；
- `mid`：可以快速进入接触但仍能看清双方全身关系；
- `close`：紧密交换/近距离控制；
- `grapple`：身体关系高度绑定。

若上一镜是 `far`，下一镜突然进入 `grapple`，必须：

- 在上一镜完成接近；
- 使用明确的 motivated jump；
- 或补过渡镜头。

这不是现实格斗距离模型，只是分镜连续性标签。

## 12. Rhythm Plan

战斗不应从第一秒到最后一秒都同一密度。

可用：

```text
setup
→ fast exchange
→ hold / breath
→ reversal
→ compressed escalation
→ decisive beat
→ aftermath
```

Breather 很重要，因为它可以：

- 重建空间；
- 让观众读取伤势/位置；
- 重置轴线；
- 让角色做决定；
- 给下一轮升级留对比。

短剧可以压缩 breather，但不能把所有定位信息都删掉。

## 13. Wide / Medium / Close 的战斗职责

### Wide / Full

优先用于：

- 建立双方位置；
- 展示完整动作路线；
- 让观众看清 choreography；
- 人物跨区移动；
- 多人关系重新建立。

### Medium

优先用于：

- 一次清楚的攻防交换；
- 上半身 + 手部/道具状态；
- 权力变化；
- 两人关系仍需同时可见。

### Close / Insert

优先用于：

- 关键决定；
- 表情/受击后的认知；
- 道具状态改变；
- 关键握持变化；
- 伤势/环境结果；
- 战斗中的剧情信息。

不要用大量 Close-up 掩盖空间完全没建立的问题。

## 14. Camera 与 Choreography

优先顺序：

```text
choreography / blocking
→ actor + prop path
→ camera path
→ cut points
```

不是：

```text
先决定疯狂环绕
→ 再逼人物动作适应相机
```

动作预演/previz 应同时验证人物和 camera。

如果动作本身已经复杂，camera 优先简化。

## 15. 长镜头

战斗长镜头成立条件：

- 空间关系清楚；
- 演员/角色运动路线可持续读取；
- camera 路线不会丢失主要动作；
- 关键 Combat Beat 能在一个连续观察中完成；
- AI 生成时不会因为同时动作过多而显著增加身份/肢体漂移。

使用：

```json
"long_take_exception": {
  "combat_beats": ["CB01", "CB02"],
  "camera_path": "...",
  "fallback": "拆成 wide exchange + reaction + reversal"
}
```

不要因为“长镜头更高级”强行使用。

## 16. Match on Action

战斗常用 match on action，但不能每个冲击都切。

过度 cut-on-action 会：

- 破坏动作完整性；
- 让观众失去空间；
- 把 choreography 切碎；
- 降低重要动作的视觉权重。

优先把 cut 放在：

- 注意力需要改变；
- 景别必须改变；
- 动作跨空间；
- 关键反转；
- 遮挡可自然隐藏切点；
- 结果需要独立读取。

## 17. Screen Direction

为主要交锋建立 line of action。

记录：

```text
C01 attack flow: left → right
C02 retreat flow: right → left
camera side: south
```

角色换位后必须更新 ledger。

如果 C01 连续三镜都在追击，不能无理由从：

```text
向画右推进
```

突然变成：

```text
向画左推进
```

除非镜头明确显示转身/换位或重新建立空间。

## 18. 一对多 / 多人混战

不要把所有人同时设为 active action。

建立：

```text
primary exchange
secondary threat
offscreen tracked threat
inactive / recovering participant
```

每个 Combat Beat 说明当前主要注意力是谁。

建议使用空间 zones / theaters：

```text
Theater A：C01 vs C02
Theater B：C03 正接近 P01
Theater C：出口方向
```

切换 theater 前后要重新建立：

- 位置；
- 方向；
- 时间关系；
- 哪一方先发生。

大规模战斗尤其应先分成多个“小战场”再交叉剪辑，而不是一个镜头描述所有人同时动作。

## 19. Weapon / Prop Continuity

如果战斗涉及武器或关键道具，本 Skill 只追踪银幕状态：

- 持有人；
- 持有手；
- 是否可见；
- 是否掉落；
- 是否损坏；
- 是否被夺取；
- 当前所在 zone；
- 是否仍参与剧情。

例如：

```text
Shot 12 end: P03 在 C02 右手
Shot 13 start: P03 在地面 Z3
```

若中间没有掉落动作或 motivated jump，则连续性错误。

不要在分镜 Skill 中提供现实武器使用优化或伤害方法。

## 20. Environment Interaction

环境动作只在它改变以下之一时成为重要 Combat Beat：

- 空间关系；
- 优势方；
- 移动路线；
- 道具状态；
- 可见伤势；
- 逃生/追击条件；
- 剧情信息。

“撞到桌子”如果只为增加热闹，不应自动获得独立 Shot。

## 21. Combat Handoff

战斗镜头可继续使用通用 handoff，并优先以下类型：

- `match_on_action`
- `reaction`
- `reframe`
- `motivated_jump`
- `insert`
- `insert_return`
- `sound_bridge`

每个 handoff 同时检查：

```text
position
+ facing
+ range
+ action_phase
+ advantage
+ prop state
```

## 22. Missing Combat Shot Audit

如果战斗“看起来跳”，按顺序检查：

1. 是否缺空间建立；
2. 是否缺接近阶段；
3. 是否直接从动作预备跳到结果；
4. 关键冲击是否没有任何可读 cue；
5. 受击/失衡后是否缺 reaction/recovery；
6. 是否无解释换位；
7. 道具是否突然换手/掉地；
8. 优势方是否突然改变而没有 reversal beat；
9. 多人场是否忘了跟踪画外角色；
10. 新 Combat Beat 是否其实应该另开 Segment。

## 23. AI 视频拆分原则

AI 视频中战斗是高风险任务。

优先：

- 1 个 Segment 只承载 1–2 个清楚 Combat Beats；
- 每个 Shot 保持一个主交锋；
- 复杂多人动作拆成 theater；
- 重要动作保持清楚起点和终点；
- 避免“高速连续十几招 + 环绕 camera + 多人 + 武器 + 长对白”同镜；
- 必要时用 Video reference 约束动作节奏/camera，但仍以 Shot 状态为事实源。

若某 Combat Beat 本身已经复杂，宁可让 camera 静态或简单跟随。

## 24. Combat Segment Boundary

优先断 Segment：

- 战斗进入新 zone；
- 优势方发生重大逆转；
- 武器/关键道具控制权变化；
- 新角色加入；
- 战斗从 standing 转为 ground / constrained state；
- 大幅伤势/服装状态变化；
- 环境被明显改变；
- 从主交锋切到另一个 theater；
- 模型时长/复杂度达到上限。

Segment 边界不是必须和 Combat Beat 一一对应，但应落在稳定状态点。

## 25. Aftermath

最后不能只写“对手倒地”。

至少确认：

- 谁仍能行动；
- 谁控制空间；
- 道具在哪里；
- 角色可见伤势/疲劳；
- 战斗结束还是只是短暂停止；
- 下一个剧情目标是什么；
- 声音/环境是否发生变化。

Aftermath 是下一场连续性的入口。

## 26. Combat Quality Gate

战斗场交付前检查：

### Narrative

- [ ] Combat Goal 清楚
- [ ] Combat Beats 对应剧情状态变化
- [ ] 优势变化有原因
- [ ] 结果推动剧情

### Geography

- [ ] Arena zones 已建立
- [ ] 角色跨区移动可读
- [ ] screen direction 连续
- [ ] 多人 theater 清楚

### Action

- [ ] 关键动作 phase 没跳
- [ ] impact 有可读前因/结果
- [ ] recovery/reposition 不凭空发生
- [ ] prop/weapon state 连续

### Camera / Edit

- [ ] wide 足够建立 choreography
- [ ] close-up 有叙事理由
- [ ] 没有过度 cut-on-action
- [ ] handoff 与动作相位一致
- [ ] 长镜头有 fallback

### AI

- [ ] 单镜没有过载
- [ ] Segment 没塞过多 Combat Beats
- [ ] 高风险多人战已分 theater
- [ ] 复杂动作优先简化 camera
