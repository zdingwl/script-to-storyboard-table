# Storyboard Method Reference v4

本文件是正式拆镜细则。目标不是堆摄影术语，而是让结果具备：

**可追溯、可拍、可剪、可生成、可校验、可修复。**

先完成 `director-plan.md` 的场次预规划，再进入本文件。

## 1. Scene Ledger

每个 Scene 抽取：

- `scene_id`
- 内/外景、地点、时间
- 出场人物
- entry state / exit state
- 关键道具及状态
- 已知资产 ID
- 场次目标、阻力、turn
- 未决问题
- 下一场承接条件

地点、时间或连续空间发生实质变化时开新 Scene。不要为了减少 Scene 数把跨时空内容塞在一起。

## 2. Beat 是状态变化

Beat 优先切在：

1. 目标变化；
2. 信息变化；
3. 权力变化；
4. 物理状态变化；
5. 可观察的情绪阈值变化；
6. 问题被提出、延期、兑现或替换；
7. 关键动作完成一个不可逆阶段。

示例：

```json
{
  "id": "E01-S02-B03",
  "source_text": "她翻过徽章，看见背面的刻印。",
  "event": "C01 发现家族刻印",
  "type": "information",
  "must_preserve": true
}
```

Beat 不等于句子；一句话可能有多个 Beat，多句也可能只是一个 Beat。

## 3. Beat → Shot 决策

先问：

> 观众为了理解这个 Beat，必须看见或听见什么？

再问：

- 必须看到过程还是结果？
- 说话人重要，还是听者反应更重要？
- 证据是否需要独立 insert？
- 空间关系是否第一次出现或已经改变？
- 动作是否需要跨镜连续？
- 同一画面是否同时承担两个竞争的注意力中心？

如果“必须看到”的信息要求不同机位、不同景别或不同注意力中心，就拆。

## 4. 镜头必要性测试

每个 Shot 写：

- `purpose`：这镜让观众获得什么；
- `cut_reason`：为什么此处需要独立镜头；
- `source_beats`：它认领什么；
- `director_obligation`：它满足哪个 coverage obligation（可选 ID/文本）。

可以删除一个镜头而不损害理解、节奏、表演或连续性时，它可能是冗余。

## 5. Atomic Shot

正常原子镜头可以一句话说清：

> 中近景固定：C01 翻过 P01，刻印露出时手指停住。

它只有：

- 一个连续时空；
- 一个主要主体/注意力；
- 一个主导景别；
- 一个主行动；
- 一个主要摄影机意图；
- 一个明确结果。

### 过载例

> 跟拍她跑进大厅，绕到正面推近，她看见父亲后停下，再给徽章特写，父亲说话，她回头落泪。

这里至少包含：进入、绕拍、推近、发现、insert、对白、反应。应拆镜或重构长镜头。

## 6. Action Phase

复杂动作先拆相位：

```text
准备 → 接近 → 接触 → 施力/执行 → 结果 → 反应/恢复
```

v4 需要跨镜追踪同一个连续物理动作时，同时写机器字段：

```json
"action_state": {
  "action_id": "ACT-01",
  "phase_start": "contact",
  "phase_end": "execution"
}
```

同一 `action_id` 跨镜 phase 不得倒退；`match_on_action` 必须继续同一 action_id。

并不是每相位一镜，但不能无解释跳过观众必须理解的相位。

示例：

```text
Shot A：C01 的手伸向门把，尚未接触。
Shot B：手部近景，接触并下压门把。
Shot C：门打开，C01 穿过门框。
```

如果 Shot A 结束时手还没碰到，Shot C 开始时人已站在门外，就要解释中间省略，或补足动作。

## 7. Coverage

### 7.1 Dialogue

常见 coverage：

- master / two-shot：空间和关系；
- OTS：保持双方关系与轴线；
- single medium/close：高信息量台词；
- reaction：权力或认知变化；
- insert：证据。

切镜条件优先是：

- 说话权发生变化；
- 一句话改变关系；
- 听者反应承载信息；
- 小道具需要独立读取；
- 同镜口型/动作负载过高。

不要每人一句机械正反打。

### 7.2 Action

优先：

- match on action；
- screen direction；
- eyeline match；
- cause → effect；
- action → reaction。

动作中切通常比动作完全结束后再切更流畅，但切点必须共享可识别的动作相位。

### 7.3 Information

重要证据必须满足：

```text
观众知道它在哪里
→ 看清关键内容
→ 看见角色如何理解它
```

并非每次都需要 3 镜；但三项信息不能缺。

## 8. Shot Size

| 景别 | 主要任务 |
|---|---|
| Extreme Wide / Establishing | 世界、尺度、地理 |
| Wide / Full | 身体、多人站位、动作路线 |
| Medium Wide / Cowboy | 人物 + 手部/道具 |
| Medium | 对话、普通动作 |
| Medium Close | 高信息量对白、情绪加强 |
| Close-Up | 决定、反应、重要信息 |
| ECU / Insert | 证据、小动作、冲击点 |

连续多个镜头同一景别时，检查切换是否真的带来信息增量。

## 9. Angle

- Eye level：中性；
- High：弱势、暴露、空间；
- Low：压迫、规模、权力；
- OTS：人物关系；
- POV：主观信息，必须标明属于谁；
- Overhead：空间布局；
- Profile：侧向动作/对峙；
- Dutch：失衡，慎用。

角度不是情绪滤镜；要服务叙事关系。

## 10. Camera Movement

### Static

人物动作已足够时优先。对 AI 视频也通常更稳定。

### Push / Dolly In

用于发现、压力、决定。要说清推向谁/什么。

### Pull / Dolly Out

用于后果、孤立、收束或空间揭示。

### Pan / Tilt / Truck

用于重新分配注意力、跟随、揭示旁侧信息或保持运动连续。

### Tracking

明确跟随方位：后跟、侧跟、正向后退。

### Arc

适合关系变化，但与多人交互、小道具、复杂动作叠加时风险高。

不要每镜都运镜。

## 11. Blocking

每镜至少知道：

- 主体起始位置；
- 朝向；
- 视线目标；
- 移动路径；
- 道具持有手；
- 结束位置。

两人场景：

```text
C01：画左，面向右
C02：画右，面向左
Axis：C01 ↔ C02
```

## 12. 180° 与 Screen Direction

检查：

- 正反打视线方向是否成立；
- 上一镜向画右移动，下一镜是否无理由改向；
- 道具是否换手；
- OTS/POV 是否让观众误认位置；
- 角色交叉换位后是否重建关系。

违反 180°并非绝对错误，但必须是有意且可读。

## 13. 30° 与无意 Jump Cut

同一主体连续镜头若：

- 时间连续；
- 构图相似；
- 角度/景别变化太小；

容易产生无意 jump cut。

可通过：

- 更明显的机位/景别变化；
- cut on action；
- reaction / insert / cutaway；
- 有意标记 jump cut；

解决。

## 14. Eyeline

标准链：

```text
人物看向画外
→ 切目标
→ 必要时回人物反应
```

目标镜头的方向、高度和距离要符合上一镜视线。

## 15. Insert / Cutaway Return

Insert 常导致连续性错误，因为主动作在 insert 期间“偷偷变化”。

记录：

- insert 前主体状态；
- insert 显示的内容；
- 返回主动作时允许变化的范围。

如果返回时人物已换位置、道具已换手，必须有足够理由。

## 16. Sound Bridge

允许：

- J-cut：下一镜声音提前进入；
- L-cut：上一镜声音延续到下一镜；
- ambience bridge：环境底声跨镜保持；
- motivated sound cut：声音触发切镜。

在 `sound` 与 `handoff_from_previous` 中写清，不要只写“自然转场”。

## 17. Start / End State

不合格：

```text
start_state: 紧张
end_state: 更紧张
```

合格：

```text
start_state:
- C01 画右前景，右手垂下，P01 在桌上
- C02 左后景，面对 C01

end_state:
- C01 右手已拿起 P01，身体左转约 30°
- C02 后撤半步，仍在画左
```

状态要能被下一镜直接读取。

## 18. Handoff Contract

每个非第一镜写：

```json
{
  "from_shot_id": "E01-S01-001",
  "type": "eyeline",
  "reason": "C01 看向门外，下一镜揭示来人"
}
```

### direct

上一镜结束状态与下一镜开始状态直接连续。

### match_on_action

共享同一动作相位。

### eyeline

前镜视线触发目标镜。

### reaction

前镜信息/动作触发反应。

### insert

从主动作切细节。

### insert_return

从细节回主动作。

### sound_bridge

声音跨镜连接。

### reframe

空间/构图重建。

### motivated_jump

故意省略中间过程，但观众可理解。

### time_jump

明确跳时。

### scene_cut

Scene 边界。

如果只写 `transition: cut`，等于没有解释。

### v4 state_inheritance

连续切镜还必须声明真正需要继承的状态路径：

```json
{
  "from_shot_id": "E01-S01-001",
  "type": "reaction",
  "reason": "动作/信息触发反应",
  "state_inheritance": [
    "characters.C01.zone",
    "props.P01.holder",
    "props.P01.hand"
  ]
}
```

Validator 比较：

```text
previous.end_state[path]
==
current.start_state[path]
```

因此 v4 的 `start_state / end_state` 应使用稳定嵌套对象表达动态连续状态。完整规则见 `continuity-audit.md`。

## 19. Continuity Ledger

### Character

- left/center/right；
- foreground/mid/background；
- 朝向和视线；
- 姿势；
- 动作阶段；
- 服装/配件；
- 发型、污渍、伤势；
- 关键已知信息。

### Prop

- 位置；
- 持有人；
- 持有手；
- 开/关；
- 完整/损坏；
- 空/满。

### Environment

- 时间；
- 天气；
- 光照；
- 门窗；
- 大型移动物体。

### Audio

- 环境声；
- 对白；
- VO；
- 音乐；
- J/L cut。

## 20. 抽象 → 可见/可听

原文：

> 他意识到被骗了。

可视化：

- 目光从转账记录移到被拉黑提示；
- 手指停住；
- 手机从耳边放下。

原文：

> 她重新掌握主动。

可视化：

- 把签好的合同翻到最后一页；
- 推给对方；
- 对方伸出的手停住；
- 她坐下，对方仍站着。

心理结果不能直接替代画面证据。

## 21. Shot Rhythm

不要“全部 3 秒”。

检查：

- 景别是否长时间不变；
- 时长是否机械一致；
- 每句台词是否都切；
- 关键反转与普通信息是否同权；
- 高潮前是否有压缩；
- 高潮后是否有落点；
- 建立镜头是否过长；
- reaction 是否短到读不出来。

节奏由信息密度和表演需要决定。

## 22. Hook Rendering

Storyboard 不负责凭空创造 hook。

对已有 hook：

- 让最后一个可见/可听信息停在未决点；
- 不提前展示下一拍答案；
- 不用“黑屏+轰鸣”假装存在信息缺口；
- 如果结尾其实是结果落点，照实标记。

## 23. AI 可执行性

高风险组合：

- 3 人以上同步精确互动；
- 两个以上关键手部/小道具动作；
- 多人同时长对白；
- 快速位移 + 环绕镜头 + 精确道具；
- 同镜换地点/服装/时间；
- 长可读文字；
- 复杂镜面/反射和精确身份同时要求。

降级顺序：

1. 固定机位；
2. 减少同步主体；
3. 手部动作拆 insert；
4. 对白与复杂动作分开；
5. 拆 Shot；
6. 拆 Segment；
7. 将文字/声音后期处理；
8. 必要时换生产方式。

## 24. Segment Grouping

可进同一 Segment 的 shots 通常满足：

- 同一 Scene；
- 时间连续；
- 环境和光照稳定；
- 人物组合变化小；
- 参考资产集合稳定；
- 总时长符合目标模型；
- 内部 cut 有清晰 handoff。

优先断 Segment：

- Scene 变化；
- 明确时间跳；
- 服装/伤势大变；
- 高风险复杂交互；
- 首/尾关键帧必须独立锁定；
- 参考资产角色发生实质变化；
- 模型时长上限。

Segment 是生成任务，不是剧情层。

## 25. 审查顺序

遇到问题按上游到下游修：

1. 剧情事实；
2. Director Plan；
3. Beat；
4. Blocking；
5. Action phase；
6. Coverage；
7. Atomic Shot；
8. Timing；
9. Camera；
10. Start/end state；
11. Handoff；
12. Segment；
13. Model handoff。

不要用下游 Prompt 修补上游错误分镜。
