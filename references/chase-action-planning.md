# Chase, Escape, Vehicle Action & Physical Hazard Planning

用于：`chase_escape`、`vehicle_action`、`physical_hazard_rescue`。

## 1. Chase / Escape

追逐戏核心不是“跑得快”，而是观众始终能回答：

```text
谁追谁？
目标是什么？
往哪里去？
距离在缩短还是拉开？
路线发生了什么变化？
失败意味着什么？
```

StudioBinder 对追车戏的分析强调 screen direction、eye-line、neutral shots 和把重要动作保持在容易读取的位置，用来在高速混乱中维持方向感。citeturn650571search0

### Plan

```json
{
  "profile": "chase_escape",
  "pursuer": ["C02"],
  "target": ["C01"],
  "escape_goal": "Z5",
  "route": ["Z1", "Z2", "Z3", "Z5"],
  "lead_gap_start": "far",
  "gap_turns": [],
  "obstacles": [],
  "route_changes": [],
  "orientation_resets": [],
  "capture_or_escape_condition": "..."
}
```

### Chase Beat

常见：

- acquire target；
- pursuit begins；
- gap closes；
- gap widens；
- obstacle；
- route choice；
- temporary loss；
- reacquire；
- shortcut / detour；
- near capture；
- escape / capture；
- aftermath。

### 镜头原则

- 高速不等于频繁乱切；
- 先建立 route / screen direction；
- 改方向时用 eyeline、POV、neutral/reorientation shot；
- 重要信息尽量落在观众容易读取的画面区域；
- 障碍要先建立存在，再拍反应/通过，除非故意 surprise 且剧情允许。

## 2. Vehicle Action

增加追踪：

- vehicle identity；
- lane/path；
- relative position；
- heading；
- speed relation（不是精确 km/h）；
- occupant state；
- damage state；
- interior/exterior handoff。

### Plan

```json
{
  "profile": "vehicle_action",
  "vehicles": [],
  "route": [],
  "relative_positions": [],
  "heading_plan": "...",
  "interior_exterior_links": [],
  "damage_progression": [],
  "orientation_resets": []
}
```

车辆大幅换位必须有建立镜头/动作原因。

## 3. Physical Hazard / Rescue

用于：

- 坠落；
- 火灾；
- 洪水；
- 塌陷；
- 溺水；
- 被困；
- 环境危险中的救援。

核心状态：

- hazard source；
- hazard progression；
- victim location/state；
- rescuer goal；
- safe zone；
- route blocked/open；
- time pressure；
- rescue phase。

### Rescue Phase

```text
hazard recognized
→ target located
→ access attempt
→ obstruction
→ contact
→ extraction
→ safe state / failure
```

### Plan

```json
{
  "profile": "physical_hazard_rescue",
  "hazard": "...",
  "hazard_state_start": "...",
  "hazard_progression": [],
  "victims": [],
  "safe_zones": [],
  "blocked_routes": [],
  "rescue_phases": [],
  "deadline": null,
  "aftermath": "..."
}
```

### 镜头原则

- 环境危险必须有状态演化，而不是背景特效随机变化；
- 角色位置与危险边界要持续可读；
- rescue 不能从“伸手”直接跳到“已获救”；
- 大型环境变化适合 wide/re-establish；
- 角色关键决定/失败适合 close/reaction；
- AI Segment 遇到环境大变化应主动断段。

## 4. Quality Gate

- [ ] route 与 screen direction 清楚
- [ ] lead gap / relative position 可追踪
- [ ] 障碍先后关系成立
- [ ] 转向/换路线有 orientation reset
- [ ] hazard 有明确 progression
- [ ] rescue phase 不跳关键状态
- [ ] aftermath 重新建立安全/危险状态
