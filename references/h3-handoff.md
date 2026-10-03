# MiniMax H3 Handoff

资料核对日期：2026-10-03。

本文件只规定分镜数据如何交给下游 H3 Prompt Skill；本 Skill **不生成最终 H3 Prompt**。

## 1. 当前官方约束

MiniMax 官方仓库当前给出：

- 输出时长：4–15 秒；
- 帧率：24 FPS；
- 输出音频：32 kHz stereo；
- H3-Base-FL2VA：0/1/2 张图，可用于 T2VA / I2VA / L2VA / FL2VA；
- H3-Base-Ref2VA：
  - 图片 ≤ 9；
  - 视频 ≤ 3，每段 2–15 秒，总参考视频时长 ≤ 15 秒；
  - 音频 ≤ 3，每段 2–15 秒，总参考音频时长 ≤ 15 秒；
  - 混合文件总数 ≤ 12；
- 官方 `h3-prompt-writing` Skill 区分 T2VA、I2VA、FL2VA、L2VA、Ref2VA；
- 最终 Prompt 时间线必须与目标视频总时长匹配。

官方资料会更新，因此每个生产项目应在 `project.model_profile.verified_at` 记录最近核对日期。

## 2. 1 Segment = 1 H3 Request

推荐：

```text
1 Generation Segment → 1 H3 request
```

Segment：

- 不跨 Scene；
- 总时长 4–15 秒；
- shots 顺序连续；
- reference 不超当前官方限制；
- 关键人物/环境/参考职责尽量稳定；
- 内部 handoff 可解释；
- 不为了凑 15 秒加入不连续事件。

## 3. v3 单一事实源

完整 Shot 只保存在：

```text
Scene.shots
```

H3 Segment 只保存：

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
  "reference_assets": []
}
```

不要把完整 shot 再嵌入 Segment。

## 4. Segment 本地时间线必须派生

假设：

```text
Shot A = 3.0s
Shot B = 5.0s
```

则 H3 本地 cut 时间自动为：

```text
Shot A  0.00–3.00
Shot B  3.00–8.00
```

而 Shot 自身的：

```text
timecode_in/out
```

仍表示成片/集内累计时间。

这样可以避免把例如 `00:32–00:40` 错写成 H3 目标视频内部的 32–40 秒。

## 5. 模式提示

### T2VA

无图锚点，只从文本建立完整视听时间线。

### I2VA

有可靠首帧，从首帧自然向后发展。

分镜层应确保：

- Scene/Shot 的 start_state 与首帧一致；
- 不在 0 秒立刻跳到另一构图；
- 首帧中角色/道具状态被锁定。

### FL2VA

首尾帧都锁定。

分镜层应确保：

- start_state 与首帧一致；
- end_state 与尾帧一致；
- 中间动作路径物理上可完成；
- 不需要瞬移、换装或无解释换位。

### L2VA

目标尾帧最重要。

分镜层应确保动作自然收敛到 end_state，而不是最后 0.5 秒突然跳到目标画面。

### Ref2VA

适合多模态参考：人物、环境、道具、动作、摄影、声音等。

注意：

> reference file ≠ Subject。

最终 H3 Prompt 中，人物/环境/道具等可复用内容通常由 `<Subject N>` 表示；`<Picture N>` / `<Video N>` / `<Audio N>` 表示具体参考资产或结构关系。分镜层只记录 asset role，不提前写最终 Subject 定义。

## 6. Reference Asset Role

分镜层记录：

```json
{
  "label": "Picture 1",
  "asset_id": "C01",
  "purpose": "character_identity"
}
```

常见 purpose：

- `character_identity`
- `environment`
- `prop_identity`
- `costume`
- `style`
- `action_reference`
- `camera_reference`
- `keyframe`
- `audio_reference`

同一 reference 的 label 进入生产后保持稳定。

避免：

- 两张图同时给同一服装提供互相冲突的事实；
- 环境图里偶然出现的角色被误当独立角色资产；
- 多视角角色图被当成多个角色；
- `<Picture N>` 和 `<Subject N>` 职责在分镜层混为一谈。

## 7. 多视角角色/资产

如果一组图片是同一角色不同视角：

分镜层应记录：

```text
同一 asset_id
+ 多个 reference source
+ 每张图的用途
```

例如：

```text
Picture 1 → face identity
Picture 2 → front body / outfit
Picture 3 → side silhouette
Picture 4 → back hairstyle / clothing structure
```

不要创建 C01/C02/C03/C04 四个角色。

同一动物/载具/道具的多视角同理。

## 8. Shot 复杂度

H3 能理解复杂多模态上下文，不代表每镜都应该塞满动作。

高风险组合：

- 3+ 人同步精确互动；
- 多人同时长对白；
- 手部小道具 + 快速位移；
- 复杂环绕 + 精确 blocking；
- 镜内换地点/服装/时间；
- 多个 reference 同时约束同一属性。

遇到高风险：

1. 简化 camera；
2. 减少同步动作；
3. 拆 insert；
4. 拆 Shot；
5. 拆 Segment。

不要先通过增加 Prompt 字数解决。

## 9. Dialogue / Audio

H3 官方要求最终视频时间线与总时长一致，因此分镜层必须先提供可信 timing。

若语言改变：

- 不得沿用源语言 timing；
- 按目标台词/TTS 重算；
- 再重新计算 Segment duration；
- 最终 H3 Prompt Skill 按新的本地时间线输出。

H3 官方当前列出稳定支持多种对话语言，但不要据此假设不同语言具有相同时长。

## 10. Keyframe Handoff

如果工作流是“每 cut 一张关键帧”：

每张关键帧至少锁定：

- 构图；
- 人物位置与朝向；
- 关键道具状态；
- 光照；
- 起始动作相位；
- 与前一镜 handoff 对应的状态。

固定身份/服装/场景/道具优先来自母资产，不要每张关键帧重新发明。

## 11. 官方 Prompt Skill 的边界

本 Skill 交付：

```text
剧情事实
+ Director Plan
+ Beat
+ Shot
+ start/end state
+ handoff
+ 时间
+ Segment
+ reference role
+ generation_mode hint
```

MiniMax 官方 `h3-prompt-writing` 再负责最终：

### Base modes

- `integrated_multimodal_description`
- `overall_soundscape`
- `non_diegetic_music`

### Ref2VA

- `subject_definitions`
- `summary`
- `retention_analysis`
- `detailed_description`
- `overall_soundscape`
- `non_diegetic_music`

不要在本分镜 Skill 里维护第二套 H3 Prompt 规则。

## 12. 交付前检查

- `model_profile.verified_at` 是否有核对日期；
- Segment 是否 4–15 秒；
- 是否跨 Scene；
- `shot_ids` 是否都存在且顺序正确；
- Segment duration 是否等于 shots 总和；
- references 是否超限；
- reference label 是否重复；
- 视频/音频 reference 时长是否超限；
- target language 的对白是否重新计时；
- handoff 是否能支持 segment 内连续生成；
- 是否存在过载镜头。

出现问题时先修分镜，再交 H3 Prompt Skill。
