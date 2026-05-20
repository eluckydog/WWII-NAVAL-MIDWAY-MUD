# 改好了 — 代码审查修复

## 已清理垃圾
- 删除 4 个废弃目录 (engine/ entities/ systems/ world/) + 12 个废弃脚本 + data/ 目录
- 总计清理 ~188KB 废弃代码
- 删除了 monte_carlo 下的一性次修复脚本 (~10个临时文件)

## 已修 Bug

| 问题 | 位置 | 修复 |
|------|------|------|
| bare except 吞掉 SystemExit | play.py L33 | → `except KeyError` |
| 三元嵌套导致启动崩溃 | play.py L588 | 简化为单层 if-else |
| `classify_ship()` 语言判断恒为真 | play.py | 改为接收 `cn` 参数 |
| `fire_salvo` 变量名不匹配 | engine.py L712/726 | `ship` → `shooter` |
| 正则 `\]` 转义警告 | play.py | 去掉多余反斜杠 |

## 新增：结构化事件系统

**engine.py + battle.py**: 全部 24 个事件生成点从中文硬编码改为 `mk_event()` 结构化格式：

```python
# 旧: events.append(f"命中{loc_name}")
# 新: events.append(mk_event("gunnery","location",
#       ship=shooter["name"], target=target["name"], location=loc_name))
```

**事件类型**：radar/detect, radar/status, gunnery/hit, gunnery/miss, gunnery/location, gunnery/effect, damage/hit, damage/crit, flood/influx, fire/event, torpedo_hit/hit, sink/sunk, turn/header, status/fleet

**play.py `make_report()` 完全重写**：同时处理结构化事件 + 遗留字符串事件，所有战报文本走 LANG 翻译表，CN/EN 双语言对全。

## 最终文件结构

```
mud_wwii_ship/
├── play.py                    (38KB) — 交互游戏
├── README.md / README.jp.md
└── monte_carlo/
    ├── engine.py              (28KB) — 战斗引擎
    ├── battle.py              (19KB) — 战斗编排
    ├── data.py                (24KB) — 舰船数据
    ├── flip_test.py / run_sim.py / personality_scan.py — MC分析
    └── test_engine.py
```
