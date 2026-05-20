# 武备系统问题诊断（2026-05-20 19:08）

## 暴露的问题

### 1. 主炮/副炮未分离
- 引擎只有一套 `gunnery_phase()`，9门16英寸和20门5英寸共用一个逻辑
- 副炮的火力投射（射速快、精度高、对驱杀伤力足够）被忽略
- **后果**：玩家所说的"主炮命中矶风轻微损伤不合理"——主炮打DD不是轻微损伤，副炮才是

### 2. AP/HE 弹药未区分
- 引擎的 `fire_salvo` 没有 ammo_type 参数
- 穿甲弹对付驱逐舰大概率过穿（小孔进出），高爆弹直接掀上层建筑
- **后果**：玩家要求"单种弹药你来选"——目前选不了

### 3. 近失弹无效果
- 现实：16英寸近失弹水下冲击波对驱逐舰是毁灭性的（可以折断龙骨）
- 引擎：miss = 无任何效果
- **后果**：玩家提到"不一定要全部命中，主炮近失也可以有损伤"

### 4. 辅助舰控制缺失
- SoDak只有`跟进掩护`一种行为模式
- 没有战术指令系统（保持距离/侧翼警戒/撤退等）
- 南达科他被陆奥弹药库殉爆一发带走
- **后果**：玩家说"太倒霉了，上拉僚舰就一波流了"

### 5. 雪风buff管道中断
- `buffs.roll_buffs()` 正常工作（61%触发率）
- `pre_battle_mc()` 正确写入雪风对象
- 但 `engine.compute_hit_pct` 和 `fire_salvo` 从不读取 `_evasion_bonus`、`_torpedo_evade`、`_magazine_protect` 等属性
- **后果**：buff数据只在雪风对象上躺着，没有任何实际效果

## 待修复方案

| 模块 | 改动 | 复杂度 |
|------|------|--------|
| `data.py` | 添加副炮数据（type/caliber/rate of fire/shell weight） | 低 |
| `data.py` | 添加弹药参数（AP: penetration, HE: explosive radius, fire chance） | 低 |
| `engine.py` | `fire_salvo` 增加 ammo_type 参数 | 中 |
| `engine.py` | 新增 `secondary_gunnery_phase()` | 中 |
| `engine.py` | 近失弹冲击波伤害函数 | 中 |
| `engine.py` | 雪风buff参数接入命中计算 | 低 |
| `battle.py` | AI Target Selection 考虑副炮 | 中 |
| `play.py` | 玩家指令系统（指引SoDak行为/弹药选择/副炮目标） | 高 |
