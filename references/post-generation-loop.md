# Post-generation Feedback Loop

本 Skill 不负责最终剪辑，但需要定义生成结果如何反馈到导演/previs层。

## 1. Assembly Review

粗剪后按 Shot / Sequence 记录：

- continuity mismatch；
- performance mismatch；
- camera mismatch；
- missing action phase；
- timing problem；
- asset drift；
- style drift；
- audio timing problem；
- missing reaction；
- pickup required。

## 2. Pickup Request

```json
{
  "pickup_id": "PU-E01-S03-01",
  "source_shot_id": "E01-S03-004",
  "reason": "动作从准备直接跳到结果",
  "required_fix": "补一镜接触/失衡阶段",
  "locked_context": [],
  "must_not_change": [],
  "preferred_duration": 1.5
}
```

## 3. 不要整场重做

优先：

1. pickup；
2. replacement shot；
3. insert / reaction；
4. timing adjustment；
5. only then redesign sequence。

这样可以把昂贵的重新生成限制在真正有问题的部分。
