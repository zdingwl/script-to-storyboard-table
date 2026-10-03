# Visual Bible / Cinematic Bible Contract

Visual Bible 是项目级视觉规则，不应在每个 Shot Prompt 里重新发明。

本 Skill **消费并传播** Visual Bible；如果用户没有提供，可输出 `visual_bible_requirements`，但不应无授权替美术/视觉开发阶段决定完整风格。

## 1. 建议结构

```json
"visual_bible": {
  "status": "locked | draft | pending",
  "reference": "path-or-id",
  "cinematography": {
    "capture_language": "spherical / anamorphic / custom",
    "camera_height_logic": "",
    "depth_of_field_logic": "",
    "handheld_policy": "",
    "movement_policy": "",
    "extreme_wide_policy": ""
  },
  "lens_intent": {
    "wide": "",
    "normal": "",
    "telephoto": ""
  },
  "lighting": {
    "key_logic": "",
    "shadow_temperature": "",
    "highlight_temperature": "",
    "contrast_policy": ""
  },
  "color": {
    "skin_tone_policy": "",
    "saturation_policy": "",
    "black_level_policy": "",
    "palette": []
  },
  "composition": {
    "headroom": "",
    "negative_space_logic": "",
    "foreground_policy": "",
    "balance_policy": ""
  },
  "material_rendering": {
    "skin": "",
    "hair": "",
    "fabric": "",
    "environment": ""
  },
  "do_not_change": []
}
```

## 2. Lookbook 与 Bible

Lookbook 适合展示参考与视觉方向；Bible 更强调可执行规则。

StudioBinder 对 film lookbook 的描述也将其作为 cinematography、production design、casting、color、lighting、mood 等部门共享的视觉参考。

## 3. Shot 层只写 Intent

Shot 不要重新写完整 Visual Bible。

Shot 只记录：

- `lens_intent`
- `lighting_intent`
- `composition_intent`
- 必要的例外

例如：

```json
"lens_intent": "wide-spatial",
"lighting_intent": "preserve storm backlight",
"visual_bible_exception": null
```

## 4. Visual Lock

下游 Shot Packet 必须包含：

- style lock reference；
- do-not-change；
- 本镜例外；
- 参考资产职责。

这样模型负责执行，而不是重新决定项目视觉风格。
