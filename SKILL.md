# Midway North Night Battle — 中途岛北方夜战 MUD

> **AI-native WWII naval combat MUD engine.**
> Drive 2 US battleships against 9 IJN ships through Monte Carlo simulation.
> You command. AI captains execute. The engine runs the numbers.

---

## Quick Start

```bash
# Install (anywhere)
skillhub install midway-night-battle

# Or clone & run
git clone https://github.com/eluckydog/WWII-NAVAL-MIDWAY-MUD.git
cd WWII-NAVAL-MIDWAY-MUD
python3 play.py
```

**Requirements:** Python 3.6+ (stdlib only, no third-party dependencies)

---

## Who This Is For

- **Historians & wargamers**: Experience 1942 Midway night battle from the bridge
- **AI/ML researchers**: Test decision-making against 9 independent agent personalities
- **MUD/roguelike fans**: Natural-language command interface, no mouse required
- **OpenClaw skill developers**: Reference implementation of a playable game skill

---

## How to Play

You are **Commander Arleigh Burke**, leading TF 34 through the Midway North night engagement.

### Your First Commands

Try these in order:

```
你准备做什么？> 报告当前态势
[Shows fleet status, enemy positions, distances]

你准备做什么？> 主炮瞄准雾岛
[Locks main battery on Kirishima]

你准备做什么？> 开火
[Runs MC simulation — hit chance, damage, magazine checks]

你准备做什么？> 我方舰船损伤
[Damage report by zone]
```

### Core Loop

```
Perceive → Decide → Command → Simulate → Assess → Repeat
  │           │          │          │          │
 Read        Choose     Natural    MC engine  Battle
 situation   target     language   computes   report
```

### Key Rules

| Rule | Detail |
|:-----|:-------|
| **You command** | Strategic orders only (target, formation, ammo type) |
| **AI executes** | Captains handle tactics (speed, precise aim, evasion) |
| **Arleigh Burke** | Your persona — radar night-fighting expert, may DC |
| **MacArthur 30% defy** | USS South Dakota captain may disobey orders |
| **XO = textbook USN** | His advice is standard doctrine — sometimes wrong in radar night combat |

### Ammo Types

| Type | Use against |
|:-----|:------------|
| **AP** (Armor Piercing) | Heavy armor, magazine penetration possible |
| **HE** (High Explosive) | Light armor, superstructure, fire-starting |

---

## Game Engine Architecture

```
play.py          ← User interaction layer (NLP → commands → reports)
monte_carlo/
  ├── engine.py  ← Core MC engine: hit %, damage, magazine, near-miss
  ├── battle.py  ← Battle flow: detect → target → fire → assess
  ├── data.py    ← Ship stats, weapon tables, zone damage effects
  ├── buffs.py   ← Special abilities (Yukikaze luck system)
  └── persona_registry.py ← 9 IJN captain personality parameters
```

### The Monte Carlo Engine

Each combat round runs **one complete simulation** with all random factors resolved in a single pass:

- Hit probability: range × target size × visibility × radar (22% fail rate) × maneuver
- Damage zones: 13 regions with independent effects (bridge, turret, magazine, engine, hull)
- Magazine detonation: AP penetration check → stored propellant → progressive flooding
- Near-miss: Shockwave damage at close miss distances

### Yukikaze Buff System

IJN destroyer **Yukikaze** has 5 independent luck rolls each round:

| Buff | Trigger | Effect |
|:-----|:--------|:-------|
| Evasion | 20% | Avoids hits outright |
| Protection | 15% | Hit lands on non-critical zone |
| Transfer | 10% | Damage assigned to adjacent ship |
| Duds | 20% | Shell fuse fails to arm |
| Miracle | 8% | Fatal hit = critical damage instead |

---

## Captain Personalities

9 IJN ships, each with independent AI:

| Ship | Type | Style |
|:-----|:-----|:------|
| Kirishima | Battlecruiser | Cautious, formation-aware, secondary priority |
| Myoko | Heavy Cruiser | Aggressive, close-range, main battery focus |
| Haguro | Heavy Cruiser | Balanced, situation-evaluating |
| Nachi | Heavy Cruiser | Stand-off, precision shooting |
| Ashigara | Heavy Cruiser | Banzai, full-speed charge, knife-fight |
| Yukikaze | Destroyer | Opportunistic, evade-first |
| Hayashio | Destroyer | Coordinated, cross-fire directed |
| Kuroshio | Destroyer | Speed, hit-and-run tactics |
| Oyashio | Destroyer | Ambush, torpedo traps |

---

## Triggers — Auto-activate on These Terms

| User says | What the skill does |
|:---------|:--------------------|
| "中途岛" / "Midway" + "游戏" / "game" / "MUD" | Activate, offer to play |
| "开战" / "play" / "start battle" | Launch `play.py`, walk through first command |
| "阿利·伯克" / "Arleigh Burke" | Explain his role + the defiance mechanic |
| "蒙特卡洛" / "Monte Carlo" + "海战" / "naval" | Explain engine architecture |
| "雪风" / "Yukikaze" | Describe the 5-buff luck system |
| "跑模拟" / "run sim" | Provide MC batch sim instructions |
| "日语" / "日本語" | Switch to Japanese-language interface mode |
| TUTORIAL / 教程 / 快速上手 | Point to TUTORIAL.md |
| "AP" / "HE" / "弹药" / "ammo" | Explain ammo types and use cases |
| "副官" / "XO" / "作战官" | Explain the doctrinal-trap mechanic |

---

## Batch Simulation

```bash
python3 monte_carlo/run_sim.py
```

Runs N rounds of engine-only simulation (no UI), outputs win/draw/loss stats.

---

## FAQ

**Q:** Missing module error?
```
cd WWII-NAVAL-MIDWAY-MUD
python3 play.py
```
All imports are relative to `monte_carlo/` — run from project root.

**Q:** Commands not working?
Use direct language: "报告态势" not "我想了解一下敌我双方的情况"

**Q:** Why can't I hit anything?
Night + range. Close to 10-15km before engaging.

**Q:** XO's advice seems wrong?
That's intentional. It's standard USN daytime doctrine — your radar makes it obsolete.

---

## Files

```
SKILL.md               ← This file
TUTORIAL.md            ← Full walkthrough (新人必读)
monte_carlo/data.py    ← 9 ships, 4 weapons, 13 damage zones (has Easter eggs)
personas/              ← 10 captain persona SKILL.md files
web/                   ← HTML/JS/CSS web interface
```
