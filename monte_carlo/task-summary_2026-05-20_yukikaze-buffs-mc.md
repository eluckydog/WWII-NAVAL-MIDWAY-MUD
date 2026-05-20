# 雪风号 Buff 系统 + 蒙特卡洛预检 — 完成

## 历史资料整理

雪风号驱逐舰（阳炎级）的传奇"幸运"基于真实历史：

- **参战但不沉**：参加了中途岛、瓜岛运输、马里亚纳、莱特湾等几乎所有IJN主战
- **带刀护卫**：每战同行舰（野分、时雨、初霜等）相继战沉，只有雪风暴风雨中归港
- **近失弹奇迹**：美军空袭中250kg近失弹将雪风掀出水面，落回后仅轻伤
- **战后生存**：1945年移交中华民国海军，改名丹阳号（DD-12），服役至1966年
- **舰魂传说**：锚链和舵轮至今保存在台湾海军（1966）和日本海自（锚链1970年打捞复刻）

## Buff 库（5种命运祝福）

| Buff | 概率 | 机制 |
|------|------|------|
| 天命加护 | 20% | +35%闪避，-60%暴击，-50%进水，+70%弹药库保护 |
| 身边的厄运 | 15% | 友军暴击率x1.5，闪避-15%（历史：同行沉她不沉） |
| 归乡意志 | 10% | 每回合恢复5HP，25%免减速 |
| 幸运的诅咒 | 20% | +20%闪避，免疫一击必杀 |
| 幽灵舰队 | 8% | 25%概率敌人打中"幽灵"而非本体 |

预检结果显示：约55%概率至少获得1层buff

## 集成方式

```
play.py Game.__init__() → pre_battle_mc()
  ├── buffs.roll_buffs()     # 蒙特卡洛骰子
  ├── yuki["_buffs"]/"_mods" # 挂在舰船dict上
  └── 战报首回合输出推演文本

engine.py:
  ├── apply_yukikaze_evasion() # compute_hit_pct中-35%命中
  ├── _magazine_protect检查    # 弹药库殉爆→大幅减伤
  ├── _crit_resist检查         # 暴击概率-8%
  
battle.py: 
  └── torpedo阶段 _torpedo_evade-25%
```

## 最终文件清单

```
mud_wwii_ship/
├── play.py                    (911行) — 交互游戏 + Buff系统
├── README.md / README.jp.md
├── personas/                  (11个人格)
└── monte_carlo/
    ├── engine.py              — 战斗引擎 + 闪避/防爆/抗暴
    ├── battle.py              — 战斗编排 + 鱼雷规避
    ├── data.py                — 舰船数据
    ├── bufs.py               ← NEW: 雪风Buff库(5buff)
    ├── flip_test.py / run_sim.py / personality_scan.py
    └── code-review_*.md / task-summary_*.md
```
