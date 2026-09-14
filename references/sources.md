# Research Sources

资料整理日期：2026-09-15。

本 Skill 不是复制某一个现成仓库，而是把传统影视分镜方法、2026 年 Agent Skill 规范和 AI 视频生产约束做了重新抽象。以下是主要参考来源及采用点。

## 1. Agent Skills Specification

Source:
- https://agentskills.io/specification
- https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx

采用：
- Skill 根目录至少包含 `SKILL.md`。
- `name` / `description` YAML frontmatter 约束。
- 主 `SKILL.md` 保持精炼，详细内容拆入 `references/` / `assets/` / `scripts/`。
- 使用相对路径引用资源，采用 progressive disclosure。

## 2. MiniMax H3 Official

Source:
- https://github.com/MiniMax-AI/MiniMax-H3
- https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing
- https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md

采用：
- T2VA / I2VA / FL2VA / L2VA / Ref2VA 模式区分。
- 当前官方 Prompt Skill 使用 4–15 秒目标视频时长。
- Ref2VA 的参考图片、视频、音频数量边界。
- reference label 必须稳定一致。
- 分镜层只准备时间、资产、状态和 mode hint；最终 Prompt 交给 H3 专用 Skill。

## 3. eternityspring/shuohao-skills — novel-storyboard

Source:
- https://github.com/eternityspring/shuohao-skills/tree/main/skills/novel-storyboard
- https://github.com/eternityspring/shuohao-skills/blob/main/skills/novel-storyboard/references/storyboard-pass.md

采用并重新设计：
- “镜头认领剧本节拍”的可追溯思想。
- Scene 不应被一个生成段跨越。
- AI 短剧中关键动作、反应镜、正反打、段尾衔接的重要性。
- 生成段与 cut 应区分。

没有照搬：
- 本仓库不把 H3 Prompt 生成塞进同一个 Skill。
- 不绑定其 `script.json`、Node 脚本或特定上游工程。

## 4. seaartpublic/skills — storyboard-prompt-assistant

Source:
- https://github.com/seaartpublic/skills/tree/main/storyboard-prompt-assistant

采用：
- 忠实保留剧情事实。
- 单个 AI 视频镜头不应过载多个地点、跳时空和复杂动作。
- 参考图应说明用途：人物身份、产品、地点、风格、动作或关键帧。
- 增量修改时只改变用户指定镜头，并最小修复受影响连续性。

## 5. script-to-shootable-storyboard

Source:
- https://github.com/zyz254009-crypto/script-to-shootable-storyboard

采用并简化：
- 原子镜头概念。
- `start_state` / `end_state` 连续性合同。
- 先 blocking、再 camera。
- 抽象心理描写转为可见/可听证据。
- 生成风险与失败降级思路。

本仓库刻意更轻：不在一个 Skill 中承担完整 Seedance 任务编译、权利审查和全套生产管理。

## 6. StudioBinder

Source:
- https://www.studiobinder.com/blog/shot-list-template-free-download/
- https://www.studiobinder.com/blog/how-to-make-a-shot-list/
- https://www.studiobinder.com/storyboard-blocking/

采用：
- Shot list 是导演/摄影/制作沟通的可执行文档。
- 记录 shot size、angle、camera movement 和 blocking。
- 人物移动与摄影机位置应在 pre-production 阶段明确。
- 180°轴线作为空间连续性的重要原则。

## 7. Boords

Source:
- https://boords.com/shot-list-template
- https://boords.com/docs/script-to-storyboard
- https://help.boords.com/en/articles/3492880-best-practice-guide-to-storyboarding
- https://boords.com/blog/16-types-of-camera-shots-and-angles-with-gifs

采用：
- 剧本和 storyboard/shot list 应保持同步。
- 分镜是决策文档，不是最终美术作品。
- notes 应包含 action、sound、lighting、camera、transition/props 等实际沟通信息。
- shot size、camera angle、movement 必须服务叙事，而不是随机变化。

## 8. 资料优先级

当来源冲突时：

1. **模型硬限制**：目标模型官方最新文档/官方仓库优先。
2. **Agent Skill 格式**：agentskills.io 最新规范优先。
3. **摄影/剪辑方法**：成熟影视语法优先，AI 工具教程只能作为生产启发。
4. **社区 Skill**：只吸收可验证的方法，不把其模型假设直接当行业标准。

## 9. 更新策略

以下内容应定期重新核对：

- H3 / Seedance / Kling / Veo 等模型时长、参考文件数量、模式名称；
- Agent Skills frontmatter 与目录规范；
- AI 视频平台对首帧、尾帧、多参考和音频的限制。

以下内容相对稳定，不应因某一模型升级而频繁改动：

- Beat → Shot 可追溯；
- 原子镜头；
- coverage；
- blocking；
- 180°空间连续；
- match on action / eyeline；
- start/end state；
- 资产 ID 和版本稳定性。
