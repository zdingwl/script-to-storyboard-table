# MiniMax H3 Handoff

资料核对日期：2026-09-15。本文件只规定分镜表如何交给下游 H3 Prompt Skill；本 Skill 不生成最终 H3 Prompt。

## 当前官方约束

MiniMax 官方 `h3-prompt-writing` Skill 当前区分 T2VA、I2VA、FL2VA、L2VA、Ref2VA，并要求目标视频描述匹配 4–15 秒时长。

官方 H3 仓库当前列出的 Ref2VA 上限：参考图片最多 9 张；参考视频最多 3 段且总参考视频时长最多 15 秒；参考音频最多 3 段且总参考音频时长最多 15 秒；混合参考文件合计最多 12 个。模型更新较快，投产前应重新核对官方仓库。

## Segment 对应一次生成任务

推荐：

```text
1 Generation Segment → 1 H3 request
```

每个 Segment：

- 不跨 Scene；
- 总时长符合当前 H3 范围；
- cut 时间线连续；
- 参考素材不超当前限制；
- 内部 shots 的 `start_state/end_state` 可连续；
- 同一参考资产的标签顺序保持稳定。

不要为了凑满时长把不同地点或不连续事件硬塞进一个 Segment。

## 交接字段

```json
{
  "target_model": "MiniMax H3",
  "generation_mode": "Ref2VA",
  "duration_seconds": 12,
  "reference_assets": [
    {"label": "Picture 1", "asset_id": "C01", "purpose": "character_identity"},
    {"label": "Picture 2", "asset_id": "S01", "purpose": "environment"}
  ],
  "shots": ["E01-S01-001", "E01-S01-002", "E01-S01-003"]
}
```

这里只记录事实和规划，不写 `subject_definitions`、`integrated_multimodal_description` 等最终 Prompt 字段。

## 模式提示

- `I2VA`：已有可靠首帧，从首帧状态自然向后发展。
- `FL2VA`：首尾状态都要精确锁定，重点是中间连续路径。
- `L2VA`：终点构图最重要，需要自然收敛到指定尾帧。
- `Ref2VA`：需要多角色、场景、道具、动作、镜头或声音参考。

分镜层只给 `generation_mode` 建议；最终 Prompt 结构由 H3 Prompt Skill 决定。

## 参考资产职责

每个 reference 应有唯一主要职责，例如：

```text
Picture 1 → C01 人物身份
Picture 2 → C02 人物身份
Picture 3 → S01 场景结构
Picture 4 → P03 道具外观
Video 1   → 动作或摄影机参考
Audio 1   → 节奏或声音参考
```

避免两个参考对同一属性给出冲突事实。编号一旦进入生产，不要无理由重排。

## Cut 时间线

例如 12 秒 Segment：

```text
Shot 1  0.00–3.00
Shot 2  3.00–7.00
Shot 3  7.00–12.00
```

必须满足：从 0 开始、相邻 cut 连续、最后结束时间等于 Segment 总时长。

最终 H3 中的切点和参考对齐，应由下游 Prompt Skill 从这些数据生成，避免人工重复计算后产生漂移。

## 关键帧交接

如果生产方式是“每个 cut 一张关键帧 + 多图参考生成”，每张关键帧至少锁定：

- 构图；
- 人物位置与朝向；
- 关键道具状态；
- 光线状态；
- 该 cut 起始动作相位。

固定人物长相、服装、场景和道具外观优先来自母资产，不要每格重新发明。

## 交付前检查

- Segment 时长是否符合当前 H3 范围；
- 是否跨 Scene；
- reference 数量是否超限；
- reference label 是否稳定；
- cut 时间是否覆盖整个 Segment；
- start/end state 是否连续；
- 是否存在多人、复杂手部、多个小道具和复杂运镜同时发生的过载镜头。

出现过载时优先拆 Shot 或 Segment，而不是先增加 Prompt 字数。

## 下游

推荐将本 Skill 的结果继续交给 MiniMax 官方 `h3-prompt-writing` Skill。接口关系：

```text
本 Skill：剧情事实 + 镜头结构 + 时间 + 资产 + 首尾状态 + mode hint
        ↓
H3 Prompt Skill：最终 MiniMax H3 Prompt
```
