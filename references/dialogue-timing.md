# Dialogue & Multilingual Timing Reference

本文件专门处理对白、旁白、配音和翻译后的镜头时长。核心规则只有一句：

> **语言变化后，镜头时长必须基于目标语言重新计算，不能继承源语言时长。**

原因不是某一种语言一定“更快”或“更慢”，而是不同语言在音节结构、信息密度、表达长度、说话者熟练度和停顿习惯上都存在差异。跨语言研究也表明 speech rate 并不恒定，因此不能把原语言的秒数当作翻译后的可靠时长。

## 1. Timing 优先级

从高到低：

1. `measured_audio`：最终真人录音实测；
2. `measured_tts`：目标 TTS 最终文本实测；
3. `scripted`：制作方明确给定的锁定时长；
4. `estimated_target_text`：按目标语言文本估算；
5. `estimated`：粗略估算；
6. `inherited_source`：只允许源语言与目标语言相同且文本未变化；跨语言时禁止。

JSON 示例：

```json
{
  "speaker": "C01",
  "text": "你早就知道？",
  "language": "zh-CN",
  "timing_seconds": 1.6,
  "timing_source": "measured_tts",
  "delivery": "压低声音，句尾短停"
}
```

## 2. 翻译后的失效规则

只要发生以下任一变化，旧 timing 就不能直接复用：

- 语言改变；
- 台词内容改变；
- 语序大幅改变；
- 增删称呼、语气词、重复；
- delivery 从平静改成哭喊/犹豫/急促；
- 角色由母语者改成明显非母语表达；
- TTS voice / speed 设置变化；
- 句间停顿策略变化。

可保留旧秒数作为“预算参考”，但不能继续标 `measured_*`。

## 3. 推荐工作流

### A. 有目标音频

直接测：

```text
音频真实时长
+ 前置反应/吸气
+ 必要尾停
= 最小镜头对白容量
```

### B. 有目标 TTS

先用最终台词生成或测目标 TTS，再把实际 duration 写回 storyboard。

这是最优方法，因为它同时吸收：

- 语言差异；
- 声线；
- 语速；
- 情绪；
- 停顿；
- 标点节奏。

### C. 只有目标文本

可以估算，但必须：

- `timing_source = estimated_target_text`
- 为情绪停顿留余量；
- 后续有 TTS 后重新测量；
- 不把估算值写成口型精确值。

## 4. Shot Speech Budget

单镜容量不是只看台词读完没有。

建议拆成：

```text
shot duration
= pre_action
+ speech
+ reaction/hold
+ transition margin
```

例如一个 4 秒镜头里，3.9 秒都被对白占满，往往会导致：

- 开口太急；
- 动作没有落点；
- 听者反应消失；
- 切点卡在最后一个字；
- AI 视频里嘴型和动作争夺同一时间。

Validator 对对白时间接近镜头总长会给 warning；不是说一定错误，而是提醒检查。

## 5. 多人对白

如果两个人严格轮流说：

```text
speech_load = line1 + line2 + ...
```

如果明确重叠：

```json
{
  "overlap": true
}
```

不要通过假设“他们可以一起说”来挤时长。

多人争吵时，如果台词辨识重要，优先：

- 拆为多个 shot；
- 使用 OTS / reaction；
- 让一人的声音跨镜延续；
- 避免多人同时精准口型。

## 6. Voiceover

VO 可以覆盖人物动作，但不代表没有容量限制。

记录：

```json
{
  "text": "...",
  "language": "en-US",
  "timing_seconds": 2.8,
  "timing_source": "measured_tts",
  "overlap_with_dialogue": false
}
```

如果 VO 与对白同时存在，需要明确是否真的重叠；默认不要把两个完整语句强行叠在一起。

## 7. Pauses 是内容

这些停顿不能被自动删掉：

- 角色发现真相后的停顿；
- 说出名字前的犹豫；
- 威胁后的 silence；
- 对方没有回答的空白；
- 电话接通前等待；
- 倒计时最后一拍。

建议用：

- `pre_speech_hold_seconds`
- `post_speech_hold_seconds`
- 或在 performance / sound 中写出。

不要为了卡进固定时长把所有停顿压没。

## 8. Subtitle 与 Spoken Dialogue 分离

字幕字数不等于口语时长。

以下情况尤其不能按字幕字符数直接算：

- 中文字幕对应英语配音；
- 英文字幕省略口头语；
- 日语/韩语翻译重组句子；
- 旁白字幕做了压缩；
- 屏幕文字不是说出来的内容。

Storyboard 的 `dialogue.text` 应是实际说出的目标文本；字幕如不同，应另存 caption/subtitle 字段。

## 9. Language Fields

项目级建议：

```json
"project": {
  "source_language": "zh-CN",
  "output_language": "en-US",
  "dialogue_language": "en-US"
}
```

每行对白仍显式保存 `language`，因为：

- 可能中英混说；
- 人名/外语词不变；
- 歌词/广播/电话可能使用其他语言。

## 10. Translation Workflow

当用户说“把这版改成英语/日语/西语”时，不能只替换台词文本。

必须重新执行：

1. 目标台词锁定；
2. Dialogue timing 重算；
3. Shot duration 重算；
4. 相邻镜 timecode 重排；
5. Scene runtime 重算；
6. Segment duration 重算；
7. H3 等模型 duration 约束重新检查；
8. 如果镜头超载，重新拆 Shot/Segment。

这一步是 v3 的硬规则。

## 11. Timing 与镜头拆分

如果一段台词比原计划长，优先顺序：

1. 检查是否本来就该分成说话人 + reaction；
2. 允许声音跨镜（L-cut/J-cut）；
3. 延长镜头；
4. 若模型 Segment 超限，拆 Segment；
5. 只有用户允许时才改短台词。

不要默认删词解决时长问题。

## 12. Timing 与口型

精确口型任务要优先使用实测音频时长。

只用估算时：

- 标记风险；
- 不承诺 frame-accurate lip sync；
- 给下游音频/视频 Prompt Skill 留出重新对齐空间。

## 13. 数据字段

推荐：

```json
"dialogue": [
  {
    "speaker": "C01",
    "text": "You knew all along?",
    "language": "en-US",
    "delivery": "low voice, restrained",
    "timing_seconds": 1.9,
    "timing_source": "estimated_target_text",
    "overlap": false
  }
]
```

`timing_source` 枚举：

- `measured_audio`
- `measured_tts`
- `scripted`
- `estimated_target_text`
- `estimated`
- `inherited_source`

跨语言且仍为 `inherited_source` 时应视为 error。

## 14. 研究依据的正确用法

跨语言语速研究用于支持“不能假设时长恒定”这一原则，而**不是**给所有项目硬编码“英语 X 词/秒、中文 Y 字/秒”。

实际制作的最佳计时仍是目标声音实测，因为：

- 角色语气不同；
- 同语言不同文本信息密度不同；
- 停顿不同；
- TTS voice 不同；
- 母语/非母语表达速度不同。

因此本 Skill 不内置一个看似精确但会误导的多语言固定语速表。
