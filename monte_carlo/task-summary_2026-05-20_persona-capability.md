# 9位日军舰长海战技能已挂载 — 完成

## 技能注入方式

`persona_registry.py` 读取每个 `persona_id` 的4维战斗参数，`battle.py` 中 `get_personality()` 按船查表，不再用全局配置。

## 人格→战斗行为映射

每条船现在用自己的舰长参数战斗：

| 舰长 | 所属舰 | 攻击性 | 射程偏好 | 战术特征 |
|------|--------|--------|----------|----------|
| 秀才 (Xiucai) | 长门 | 0.50 | medium | 教科书式，编队纪律极强(0.95) |
| 高丘 (Gaoqiu) | 陆奥 | **0.95** | **close** | 近战狂人，死战不退(0.10) |
| 段誉 (Duanyu) | 金刚 | 0.70 | close | 夜战专家, 适应力最强(0.85) |
| 四明 (Si Ming) | 榛名 | 0.40 | **long** | 保守型, 撤退阈值最高(0.35) |
| 雪风 | DD | 0.90 | medium | 幸运舰, 编队纪律低(0.40) |
| 阳炎 | DD | 0.80 | close | 帝国海军范本, 决死(0.10) |
| 矶风 | DD | 0.65 | **long** | 远程雷击, 独立行动 |
| 黑潮 | DD | 0.75 | close | 沉默暗杀者, 近距鱼雷(5km) |
| 不知火 | DD | 0.55 | **variable** | 电子战型, 每次随机射程! |

## 核心机制:
- **range_preference** → 吸引/交战距离
- **retreat_threshold** → HP低于此比例开始脱离
- **turn_rate_mod** → 转向敏捷度
- **formation_bond** → 编队凝聚度
- **torpedo_trigger_km** → 发射鱼雷的距离
- **decisiveness** → 高者更早在远距离发射
- **aggression** → 高者追击多损伤目标(收人头)，低者打最大威胁
- **adaptability** → 高者不定时重新评估目标
- **variable** → 不知火每回合随机抽射程

## 文件清单（更新后）
```
mud_wwii_ship/monte_carlo/
  ├── persona_registry.py   — NEW: 9位舰长战斗数据表
  ├── buffs.py              — NEW: 雪风Buff库(5种祝福)
  ├── battle.py             — 修改: get_personality()读registry, move_ship用per-captain参数
  ├── engine.py             — 修改: 雪风闪避/防爆/抗暴
  ├── data.py               — 不变
  └── (其他MC脚本)
```
