# 《项目名》分镜表 v3.2

> 人工评审主视图。进入关键帧、图片 Prompt、视频 Prompt 或自动化流水线时，同步维护 `storyboard.json`。

## 一、项目信息

| 项目 | 内容 |
|---|---|
| 项目名 |  |
| 集数/范围 |  |
| 模式 | faithful / visual / pacing / story |
| 画幅 | 9:16 / 16:9 / other |
| 源语言 |  |
| 输出/对白语言 |  |
| 目标总时长 |  |
| runtime_lock | true / false |
| 目标视频模型 |  |
| 模型规则核对日期 |  |
| 场次数 |  |
| 镜头数 |  |
| Generation Segments |  |

## 二、Director Plan

| Scene | Sequence Type | Secondary Types | Dramatic Job | Turn | Blocking / Axis | Coverage Obligations | Pacing | Hook Role |
|---|---|---|---|---|---|---|
| E01-S01 | investigation_reveal |  |  |  |  |  | neutral | none |

## 二-A、Sequence Plan（非战斗场）

| Scene | Profile | Sequence Goal | Audience Question | Sequence Beats | Rhythm | Camera Strategy | Continuity Priorities |
|---|---|---|---|---|---|---|---|
| E01-S01 | investigation_reveal |  |  | SQ01–SQ03 |  |  |  |

### Sequence Beat 明细

| Sequence Beat | 类型 | 导演职责 | Source Beats | 可见变化 |
|---|---|---|---|---|
| E01-S01-SQ01 | evidence_found |  | E01-S01-B01 |  |

## 二-B、Combat Plan（仅战斗场）

| Scene | Combat Goal | Participants | Arena Zones | Combat Beats | Rhythm | Camera Strategy | Continuity Priorities |
|---|---|---|---|---|---|---|---|
| E01-S04 |  | C01 / C02 | Z1 / Z2 / Z3 | CB01–CB05 | setup → reversal → finish |  |  |

### Combat Beat 明细

| Combat Beat | 类型 | 剧情职责 | 优势前→后 | Zone 前→后 | Range 前→后 | 可见结果 | Source Beats |
|---|---|---|---|---|---|---|---|
| E01-S04-CB01 | pressure / reversal / escalation / finish / aftermath |  | C01 → C02 | Z1 → Z2 | mid → close |  | E01-S04-B03 |

### 战斗连续性检查

- [ ] Combat Goal 明确，不是单纯“打得很燃”
- [ ] Arena zones 已建立，跨区移动可读
- [ ] 重要 Combat Beat 有 advantage_before / advantage_after
- [ ] range 没有无解释从 far 跳到 grapple
- [ ] 关键冲击有来向/预备、冲击 cue、结果/反应
- [ ] 多人混战有 primary exchange / secondary threat / theater
- [ ] 武器/关键道具持有人、持有手、掉落/损坏状态连续
- [ ] 战斗结束后的 aftermath 已记录
- [ ] AI Segment 没有塞入过多 Combat Beats

## 三、角色索引

| ID | 角色 | 参考资产 | 本次状态/服装 | 锁定特征 | 状态 |
|---|---|---|---|---|---|
| C01 |  |  |  |  | approved / pending |

## 四、场景索引

| ID | 场景 | 时间/光照 | 参考资产 | 空间锚点 | 状态 |
|---|---|---|---|---|---|
| S01 |  |  |  |  | approved / pending |

## 五、道具索引

| ID | 道具 | 参考资产 | 初始状态 | 连续性重点 | 状态 |
|---|---|---|---|---|---|
| P01 |  |  |  |  | approved / pending |

## 六、剧情 Beat 清单

| Beat ID | 场次 | 原文/来源 | 状态变化 | 类型 | 必须保留 |
|---|---|---|---|---|---|
| E01-S01-B01 | E01-S01 |  |  | action / dialogue / information / reaction / reveal | 是 |

## 七、Generation Segment 规划（AI 视频流程）

> v3：Segment 只引用 `shot_ids`，不复制完整 Shot。Segment 本地 cut 时间由每镜时长自动派生。

| Segment | Scene | 时长 | 目标模型 | 模式建议 | Shot IDs | 参考资产 | 风险 |
|---|---|---:|---|---|---|---|---|
| E01-S01-G01 | E01-S01 | 8s | MiniMax H3 | Ref2VA | 001, 002 | C01, S01 | low |

## 八、完整分镜表

| 镜号 | 生成段 | 场次 | 时间码 | 时长 | 原剧本节拍 | Sequence / Combat Context | 镜头职责 | 切点理由 | 景别/角度 | 运镜 | 画面与构图 | 人物/调度 | 动作/表演 | 台词/旁白 + timing | 声音 | 资产 | 首帧状态 | 尾帧状态 | 衔接合同 | 连续性/风险 |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E01-S01-001 | E01-S01-G01 | E01-S01 | 00:00–00:03 | 3s | E01-S01-B01 |  |  | 中近景 / 平视 | 固定 |  |  |  |  |  |  |  |  | first shot |  |
| E01-S01-002 | E01-S01-G01 | E01-S01 | 00:03–00:06 | 3s | E01-S01-B02 |  |  | 近景 / 平视 | 固定 |  |  |  |  |  |  |  |  | reaction from 001 |  |

## 九、对白 / 配音 Timing Audit

| 镜号 | Speaker/VO | 文本语言 | Timing | 来源 | 镜头时长 | 占用率 | 是否需重算 |
|---|---|---|---:|---|---:|---:|---|
| E01-S01-002 | C01 | zh-CN | 1.8s | measured_tts | 3s | 60% | 否 |

### 跨语言检查

- [ ] 如果输出语言与源语言不同，所有旧 timing 已失效并重新计算
- [ ] 最终台词与 timing 对应同一版本文本
- [ ] TTS/实录可用时已替换纯估算
- [ ] 对白后仍有必要的反应/停顿/切点空间
- [ ] Scene / Episode / Segment runtime 已重新累计

## 十、节奏与 Hook 节点

| 节点 | 对应镜头 | 类型 | 说明 |
|---|---|---|---|
| 开场钩子 |  | information_gap / other |  |
| 第一次升级 |  |  |  |
| 信息揭示 |  |  |  |
| 高潮/反转 |  |  |  |
| 情绪落点 |  |  |  |
| 结尾钩子 |  | threat_pending / result_only / other |  |

## 十一、Missing-Shot / Handoff Audit

逐镜检查：

- [ ] 上一镜结束状态能到达下一镜开始状态
- [ ] 非第一镜有明确 handoff
- [ ] 动作相位没有跳过必须看清的阶段
- [ ] eyeline 后有目标
- [ ] insert 后能安全返回主动作
- [ ] 位置变化有可见路径或明确省略理由
- [ ] 时间跳跃明确
- [ ] 没有因为 Segment 时长限制把跨 Scene 内容硬拼

## 十二、连续性检查

### 人物

- [ ] 左右位置与朝向连续
- [ ] 视线方向合理
- [ ] 动作相位连续
- [ ] 服装/发型/伤痕/污渍一致

### 道具

- [ ] 位置连续
- [ ] 持有人连续
- [ ] 持有手连续
- [ ] 开/关、完整/损坏、空/满状态连续

### 空间 / Camera

- [ ] 180°轴线无无意跳轴
- [ ] 同一主体连续切换无无意小角度 jump cut
- [ ] 屏幕运动方向连续
- [ ] 门窗/大型物体位置连续
- [ ] 光照、天气、时间连续

### 声音

- [ ] 对白没有被镜头时长截断
- [ ] VO / J-cut / L-cut 有明确跨镜说明
- [ ] 环境声与动作一致
- [ ] 声音桥与画面切点一致

## 十三、AI 生成风险

| 镜号/Segment | 风险 | 原因 | 建议降级 |
|---|---|---|---|
|  | low / medium / high |  |  |

## 十四、交付摘要

- 总镜数：
- 总时长：
- Beat 覆盖：
- Director Plan 覆盖：
- 跨语言 timing：
- Hook audit：
- 未解决 error：
- 未解决 warning：
- 下一阶段建议读取：`storyboard.json` + 角色/场景/道具资产。
