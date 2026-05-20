# 代码联合审查报告：mud_wwii_ship 项目

审查框架：
- 【工程化AI代码生成智能体】AST/CFG分析 + 质量门禁
- 【红队 v2.0】T2标准安全测试（4层防御 + 5步执行）
- 【门下省 v6.1】代码规范 + 变更分级(L2) + 完整性检查

---

## 一、项目总览

| 指标 | 数值 |
|------|------|
| 核心文件数 | 4 (play.py + engine.py + battle.py + data.py) |
| 总代码量 | ~105KB |
| 临时/废弃文件 | 21个 (~102KB, 无人使用的遗留代码) |
| 测试覆盖 | unit: 1 (test_engine.py), MC: 4 (run_sim/personality/flip/find_s) |
| 确认bug | 2 (已修) |
| 潜在问题 | 4 (需修复) |

---

## 二、已修复bug

### 2.1 classify_ship() 语言判断恒为真 (LOW)

**症状**: `has_chinese("中")` 中"中"本身就是汉字 → `classify_ship()` 永远返回中文标签，英文模式写"战列舰"

**根因**: 函数硬编码了中文测试字符串，未接收语言上下文

**修复**: 函数签名改为 `classify_ship(s, cn=True)`，调用处传 `cn` 参数

### 2.2 bare except (MEDIUM)

**位置**: `play.py` L33, t() 函数中

```python
try:
    txt = txt.format(**kw)
except:   # ← 会静默捕获 SystemExit, KeyboardInterrupt
```

**修复**: `except KeyError:` — 只捕获格式占位符不匹配

### 2.3 三元表达式嵌套错误 (HIGH，会导致启动崩溃)

**位置**: `play.py` L588

```python
print("..." if cn else "The adjutant..." if cn else "The adjutant..." else "...")
```

**修复**: 简化为正确的一层if-else

---

## 三、现存问题（红队T2 + AI代码生成智能体审查）

### 3.1 🔴 高优先级

#### H1. 英文模式功能残缺 (ENG-01)

| 维度 | 详情 |
|------|------|
| 层 | 应用层·内容层 |
| 危害 | 英文用户看到的中英混杂体验 |
| 具体 | `make_report()` 硬编码了中文 adjutant 前缀；实战报告文本全是中文硬编码，英文版只是 stub 骨架 |
| 建议 | 重写 `make_report()`：所有打印走 `t()` 调用，或构建独立的中/英 `adj_prefix` 数组 |

示例暴露: `make_report` 中 `if cn else` 分支覆盖不全，中文字符串嵌入在函数体中

#### H2. 无持久化 / 游戏状态丢失 (PERSIS-01)

| 维度 | 详情 |
|------|------|
| 层 | 行为层 |
| 危害 | 退出即丢，无自动存档/读档 |
| 具体 | `summary_log` 只在内存中，exit后消失。玩家输掉一局没有复盘数据 |
| 建议 | 每回合自动追加到 `logs/{timestamp}.json` |

### 3.2 🟡 中优先级

#### M1. command.py line 35: AI兵棋推演命令行未验证

```python
# systems/command.py 中的 eval()
result = eval(command)  # 危险！
```

**风险**: 注入攻击。虽然 play.py 不使用这个模块，但它存在于项目中

**建议**: 删除废弃的 `engine/` `entities/` `systems/` `world/` 目录及其所有子文件（约15个文件，~35KB）

#### M2. 事件系统纯中文硬编码

`engine.py` 中 `gunnery_phase()`, `damage_progression()` 等函数直接 `events.append(f"[炮击] ... {loc_name}")` — 事件字符串是中文且无英文对等物

**影响**: `make_report()` 靠正则解析中文事件串 → 英文模式无法理解

**建议**: 事件系统改用结构化格式 `{"phase":"gunnery","ship":"nagato","effect":"hit","location":"belt"}`，由展示层决定语言

#### M3. Persona人格文件未在游戏中实际应用

`personas/` 下有 11 个人格 SKILL.md，但 `battle.py` 的战术AI用的是 `data.py` 的固定参数（aggression/torpedo_trigger_distance等），人格文件的内容从未被读取

**建议**: 要么建立人格-参数的映射加载机制，要么删除未使用的 SKILL.md

### 3.3 🟢 低优先级

#### L1. 临时文件堆积 (CLEAN-01)

| 文件 | 大小 | 用途 | 现状 |
|------|------|------|------|
| `_calc_gen.py` | 9.4KB | 初版计算脚本 | 废弃 |
| `_distill_burke.py` | 1.8KB | 人格蒸馏 | 已由persona/替代 |
| `_force_calc.py` | 9.0KB | 弹力计算 | 废弃 |
| `_gen*.py` | ~36KB | 生成器 | 一次性 |
| `force_calc*.py` | ~19KB | 弹道计算 | 废弃 |
| `interactive_*.py` | ~14KB | 交互原型 | 已由play.py替代 |
| `server.py` | 8.2KB | MUD服务器 | 废弃 |
| `engine/` 目录 | ~18KB | MUD引擎 | 废弃 |
| `entities/` 目录 | ~5.5KB | 实体 | 废弃 |
| `systems/` 目录 | ~7KB | 系统 | 废弃 |
| `world/` 目录 | ~0.5KB | 地图 | 废弃 |
| 总计 | ~137KB | — | 直接删除 |

#### L2. `make_report()` 函数过长

AST扫描报告: `make_report` = 132行。建议拆分为:

```
make_radar_report()
make_gunnery_report()
make_damage_report()
make_status_report()
adjutant_closing()
```

#### L3. `engine.py:apply_damage()` = 185行

这是全项目最长的函数，负责损伤计算、火灾蔓延、进水、弹药库殉爆等多个正交逻辑

**建议**: 拆分为 `apply_hit_damage()`, `apply_fire()`, `apply_flood()`, `check_magazine_explosion()`

---

## 四、代码质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 编译完整性 | ⭐⭐⭐⭐⭐ | 全部模块编译通过，无语法错误 |
| 运行时稳定性 | ⭐⭐⭐⭐ | 种子确定性运行正常(5回合实测) |
| 代码规范 | ⭐⭐⭐ | bare except已修，但事件硬编码严重 |
| 国际化 | ⭐⭐ | CN完整，EN半残 |
| 安全性 | ⭐⭐⭐⭐ | 生产代码无注入点(废弃模块有eval但未使用) |
| 结构整洁 | ⭐⭐ | 垃圾文件过多(137KB废弃代码) |
| 人设工程 | ⭐⭐ | 11个人格文件写完了但没用上 |

---

## 五、建议修复顺序

```
立即（<5分钟）:
  ▢ 删除废弃目录 (engine/ entities/ systems/ world/)
  ▢ 删除废弃脚本 (_*.py, force_calc*.py, interactive_*.py, server.py)

短中（15-30分钟）:
  ▢ 事件系统结构化 (engine.py 内 events.append 改为 dict 格式)
  ▢ make_report() 拆分 + 英文分支补齐
  ▢ 建立人格-参数映射加载机制

长期:
  ▢ 自动存档/复盘功能
  ▢ TypeScript Web前端（已有index.html骨架）
```
