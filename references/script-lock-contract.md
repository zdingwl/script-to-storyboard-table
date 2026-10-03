# Script Lock / Story Contract

Script Lock 不是“不能再改一个字”，而是明确哪些剧情事实在进入导演规划后不得被静默改写。

## 1. Scene Story Contract

每场至少记录：

```json
"story_contract": {
  "objective": "C01 想得到什么",
  "obstacle": "谁/什么阻止",
  "escalation": ["冲突怎样升级"],
  "information_release": [
    "何时观众/角色得到什么信息"
  ],
  "emotional_start": "A",
  "emotional_end": "B",
  "irreversible_change": "这场结束后无法回到原状态的变化",
  "must_preserve": [],
  "authorized_flex": []
}
```

## 2. must_preserve

适合锁定：

- 核心剧情因果；
- 谁先做什么；
- 生死/受伤事实；
- 关键对白事实；
- 道具归属；
- 身份揭露顺序；
- 反转；
- 结尾钩子；
- 场次结果。

## 3. authorized_flex

可允许导演调整：

- 表现性反应；
- 纯视觉过渡；
- 不改变事实的小动作；
- 镜头拆合；
- J/L cut；
- 非事实型环境反馈。

## 4. Script Lock 与 Beat

Narrative Beat 必须从 Story Contract 与原稿中派生。

若镜头规划发现必须新增剧情动作才能成立：

- 不得偷偷添加；
- 标记 `story_conflict`；
- 给出最小修复建议；
- 只有用户授权后才进入 story 模式。

## 5. 为什么有用

它阻止两个常见问题：

1. Director / AI 为了镜头“更电影”擅自改剧情；
2. 不同阶段各自重新理解剧本，导致版本漂移。
