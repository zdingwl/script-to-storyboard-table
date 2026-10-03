# Research Sources

资料整理/复核日期：2026-10-03。

本 Skill 不是复制某一个现成仓库，而是把：

- Agent Skill 编写规范；
- 传统影视导演/分镜/连续性方法；
- AI 视频生成的可执行性约束；
- MiniMax H3 官方输入/Prompt 规则；
- 多语言对白 timing 研究；
- 公开社区 storyboard Skill 的有效设计；

重新抽象成一套独立、可校验的数据流程。

## 1. OpenAI / Agent Skill 规范

Source:

- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/skills-and-plugins
- https://agentskills.io/specification

采用：

- Skill 聚焦单一工作流；
- 根目录 `SKILL.md`；
- 详细方法放入 `references/`；
- 模板放 `assets/`；
- 确定性检查放 `scripts/`；
- 使用 progressive disclosure，主 Skill 不堆所有知识；
- `description` 明确触发范围和边界；
- 可选 `agents/openai.yaml` 提供 UI 元数据。

## 2. MiniMax H3 Official

Source:

- https://github.com/MiniMax-AI/MiniMax-H3
- https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing
- https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
- https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt
- https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt

2026-10-03 核对到的官方要点：

- 输出 4–15 秒；
- 24 FPS；
- 32 kHz stereo；
- FL2VA 变体支持 0/1/2 图，对应文本、首帧、尾帧、首尾帧模式；
- Ref2VA 图片 ≤9；
- Ref2VA 视频 ≤3，每段 2–15 秒，总时长 ≤15 秒；
- Ref2VA 音频 ≤3，每段 2–15 秒，总时长 ≤15 秒；
- 混合参考文件 ≤12；
- 官方 Prompt Skill 要求 timeline 与目标时长匹配；
- Ref2VA 中 `<Subject N>` 与 `<Picture/Video/Audio N>` 角色不同，reference label 必须稳定。

本仓库采用：

- Segment 对应一次生成任务；
- 本地 cut 时间从 Shot 时长派生；
- 分镜层只记录 reference role / mode hint；
- 最终 H3 Prompt 交给官方 Skill。

没有采用：

- 不把官方最终 Prompt 结构复制进本 Skill；
- 不把 H3 的易变限制写成通用影视规则。

## 3. StudioBinder — Shot List / Blocking / Continuity Editing

Source:

- https://www.studiobinder.com/storyboard-blocking/
- https://www.studiobinder.com/blog/what-is-continuity-editing-in-film/
- https://www.studiobinder.com/blog/what-is-a-match-on-action-cut/
- https://www.studiobinder.com/blog/how-to-make-a-shot-list/

采用：

- blocking 应在镜头设计前明确；
- 180°规则用于保持空间关系；
- match on action 用动作连续隐藏切点；
- 同一主体连续机位需要足够角度/构图变化，避免无意 jump cut；
- shot list 是制作/剪辑沟通文档，而不是形容词集合。

## 4. Boords — Storyboard / Shot List

Source:

- https://boords.com/shot-list-template
- https://boords.com/how-to-storyboard
- https://boords.com/docs/script-to-storyboard

采用：

- Shot list 从剧本提取并与 storyboard 同步；
- 记录 shot size、camera angle、movement；
- 按 Scene / setup 分组；
- 分镜是决策与沟通工具；
- 动作、声音、道具、转场等信息应能被后续制作读取。

## 5. Google Veo Prompt Guide

Source:

- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide

采用为“AI 视频通用启发”，不是 H3 硬规则：

- 动作应以具体动词描述；
- camera angle / movement 需要明确；
- 时间变化和动作演化必须符合短片可完成性；
- 不把多个长期过程塞进过短片段。

## 6. Cross-language Speech Rate Research

Primary references:

- Pellegrino, Coupé & Marsico (2011), *A Cross-Language Perspective on Speech Information Rate*
  - DOI: 10.1353/lan.2011.0057
  - https://hub.hku.hk/handle/10722/262830
- Coupé et al. (2019), *Different languages, similar encoding efficiency: Comparable information rates across the human communicative niche*
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC6984970/
- Bradlow et al. / related L1-L2 timing work:
  - https://pmc.ncbi.nlm.nih.gov/articles/PMC8942379/

采用：

- 不同语言 speech rate / syllable structure / information density 不恒定；
- 不能因为语义相同就假定翻译前后配音秒数相同；
- 非母语表达也可能显著改变 timing。

没有采用：

- 不把学术平均值硬编码成“某语言固定 X 字/秒”；
- 实际生产优先使用目标 TTS/录音实测。

## 7. eternityspring/shuohao-skills — novel-storyboard

Source:

- https://github.com/eternityspring/shuohao-skills
- https://github.com/eternityspring/shuohao-skills/tree/main/skills/novel-storyboard

采用并重新设计：

- Beat ownership；
- generation segment 与 cut 分离；
- AI 短剧镜头需要确定性质量门；
- Segment 不能跨 Scene；
- 下游时间线最好由结构派生，而不是重复手写。

本仓库 v3 进一步改为：

```text
Scene.shots = canonical truth
Segment.shot_ids = references only
```

避免完整 Shot 被复制两份。

## 8. seaartpublic/skills — storyboard-prompt-assistant

Source:

- https://github.com/seaartpublic/skills/tree/main/storyboard-prompt-assistant

采用：

- 忠实剧情；
- 避免 overloaded shot；
- reference 需说明用途；
- 增量修改时冻结未指定内容；
- 长故事先做结构再做细镜。

没有采用：

- 本仓库不在分镜表中生成最终 AI positive/negative prompt。

## 9. script-to-shootable-storyboard

Source:

- https://github.com/zyz254009-crypto/script-to-shootable-storyboard

采用并深化：

- atomic shot；
- start/end state；
- blocking before camera；
- 心理 → 可见/可听证据；
- continuity / generation risk / fallback。

v3 新增：

- `handoff_from_previous`；
- Director Plan；
- multilingual timing；
- canonical Shot；
- derived Segment local timeline。

## 10. 其他公开 AI 短剧 Skill

参考：

- https://github.com/towardsyoung/video-agent-skills
- https://github.com/zenstory-ai/drama-skills

主要用于对照：

- 上游剧本、资产、分镜、视频 Prompt 的职责边界；
- “不要为了补齐流程伪造上游事实”；
- 生产前先冻结事实层；
- 角色/场景/道具连续性应由可读文档持久化。

没有直接复制其字段或工作流。

## 11. 本次 v3 的独立设计结论

### 11.1 Director Plan 必须在 Shot 前

原因：

- Scene 的 turn / blocking / coverage 不先确定，单镜容易各自正确但组合失效；
- “缺镜”通常不是 prompt 问题，而是 action phase / transition 没被规划。

### 11.2 Handoff 是独立合同

仅有：

```text
previous.end_state → current.start_state
```

还不足以解释为什么能切。

v3 增加：

```text
previous.end_state
→ handoff_from_previous
→ current.start_state
```

### 11.3 Segment 不复制 Shot

重复保存完整 Shot 会形成冲突源。

v3：

```text
Scene.shots
+ Segment.shot_ids
```

### 11.4 翻译后 timing 失效

源语言时长只对源文本有效。目标语言变化必须重算，并向下游传播到：

- Shot duration；
- Scene runtime；
- Episode runtime；
- Segment duration；
- H3 target duration。

### 11.5 Hook Audit 不替代编剧

Storyboard 只检查“未决问题是否被镜头准确保留”，不在 faithful 模式凭空制造新悬念。

## 11.6 Fight / Combat Storyboarding Research

Source:

- https://www.studiobinder.com/blog/how-to-storyboard-a-fight-scene/
- https://www.studiobinder.com/blog/best-fight-scenes-sherlock-ritchie/
- https://www.studiobinder.com/blog/how-to-shoot-dynamic-fight-scenes-that-keeps-audience-attention/
- https://www.studiobinder.com/blog/what-is-a-match-on-action-cut/
- https://nofilmschool.com/Jean-Paul-Ly-guest
- https://nofilmschool.com/battle-of-the-gullet

采用：

- fight choreography / rehearsal / previz 应先于最终 shot design；
- 战斗场本身需要 mini-story：目标、优势变化、反转、升级、结果；
- wide / medium / close 应承担不同的空间、动作和情绪职责；
- camera 应配合 choreography，而不是用复杂运动掩盖动作规划缺失；
- match on action 对动作连续有效，但过度切动作会削弱 choreography 的可读性；
- 大规模战斗可拆成多个 spatial theaters，再围绕 POV / story beat 交叉剪辑；
- 战斗规划应通过 previz / rehearsal 验证人物和摄影机路线。

本仓库进一步抽象为：

```text
Director Plan
→ Combat Plan
→ Combat Beat
→ Action Phase
→ Atomic Shot
→ Combat Handoff
→ Aftermath
```

没有采用：

- 不把某一影片的具体打法当成通用规则；
- 不提供真实格斗、武器使用或伤害优化；
- 不把“镜头更碎”当作动作更有冲击力的默认结论。

## 12. 来源优先级

冲突时：

1. 用户当前明确要求；
2. 目标模型官方最新文档；
3. OpenAI / Agent Skill 官方规范；
4. 成熟影视导演/剪辑方法；
5. 学术研究；
6. 公开社区 Skill；
7. 工具博客和经验规则。

## 13. 更新策略

经常复核：

- H3 / Seedance / Kling / Veo 的输入限制；
- Agent Skills 格式；
- 模型多参考、音频、关键帧能力。

相对稳定：

- Director Plan → Beat → Shot；
- atomic shot；
- blocking；
- coverage；
- 30°/180°；
- match on action / eyeline；
- start/end state；
- handoff；
- asset ID；
- 单一事实源；
- 翻译后重新 timing。
