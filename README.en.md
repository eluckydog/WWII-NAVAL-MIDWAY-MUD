# Midway North Night Battle — Arleigh Burke Trainer

[**中文**](README.md) · [**日本語**](README.jp.md)

> **02:00, June 5, 1942 | 30°N 178°E | Overcast, moonless night**

> **AI-native MUD game logic engine prototype**
> The engine layer is architected for AI agent control: AI handles battlefield awareness, tactical decisions, and action execution
> Current build: MUD interaction prototype — you command, AI captains and engine execute
> A gaming experience unlike any other.

---

## The Battlefield

In the early hours of June 5, 1942, the Battle of Midway is over. The Japanese fleet is withdrawing.

But in the northern waters, a US task force is moving to intercept. USS Iowa (BB-61) and USS South Dakota (BB-57) have been ordered to block the First Fleet's retreat route.

Iowa is the fastest battleship in the US Navy — 33 knots, nine 16-inch/50-caliber Mark 7 main guns, SG radar. South Dakota is on your quarter, with General Douglas MacArthur on her bridge. He commanded the Philippines campaign. He is a five-star Army general. He is not a naval tactician. His radio messages are sometimes insightful, sometimes irrelevant to the battle at hand.

Your opponent: four battleships (Nagato, Mutsu, Kongo, Haruna) and five Kagero-class destroyers (Yukikaze, Kagero, Isokaze, Shiranui, Kuroshio) — nine ships armed with Type 93 "Long Lance" oxygen torpedoes: faint wake, 22-40km range, 490kg warhead.

---

## Weapons System

### Main / Secondary Battery
Iowa carries 20 × 5-inch/38-caliber dual-purpose guns (10 per side); South Dakota carries 16. The secondary battery fires automatically during battle, prioritizing destroyers. A single hit causing more than 30HP damage temporarily suppresses one of the destroyer's main guns — reducing its torpedo launch capacity.

### Ammunition Types
- **AP (Armor-Piercing)**: Default load. Effective against capital ships — penetrates belt armor with internal blast effects. Against destroyers: overpenetration (15-40HP damage).
- **HC (High-Capacity / HE)**: Tears destroyer superstructures and starts fires (80-140HP+). Against battleships: high ricochet probability.

Ammunition type can be selected before battle. Wrong ammunition means a wasted salvo.

### Near-Miss Damage
When 16-inch shells land within 4km of a destroyer and all shells miss, there is approximately a 20% chance of a near-miss shockwave: 20-80HP structural damage, 22% probability of minor flooding. Japanese captains do not report near-miss damage, but speed reduction is observable.

### Yukikaze
Yukikaze (8th Kagero-class destroyer, Kure Naval Arsenal, 1940) has a unique probabilistic system. Before each battle, independent rolls determine active buffs:
- Heaven's Protection (20%): +35% evasion, +60% critical hit resistance, +70% magazine protection
- Nearby Misfortune (15%): Allied ships in formation take increased damage
- Will to Return (10%): Hull self-repair, speed retention, crew recovery
- Curse of Luck (20%): +20% evasion, one-hit-kill immunity
- Spectre Fleet (8%): Chance of decoy targets appearing

Approximately 61% chance she enters battle with at least one buff active.

---

## Japanese Commanders (9 Independent AI Personas)

| Ship | Callsign | Tactical Profile |
|:-----|:---------|:-----------------|
| Nagato | Scholar | Academic tactician. Seeks optimal solutions. |
| Mutsu | Brawler | Close-range aggression. Presses the attack. |
| Kongo | Blade | Combat veteran. Decisive, no wasted moves. |
| Haruna | Gatekeeper | Defensive posture. Waits for opponent error. |
| Yukikaze | Gambler | High-risk, high-reward playstyle. |
| Kagero | Warrior | Honor-driven. Reluctant to disengage. |
| Isokaze | Seawolf | Hunter tactics. Ambushes from disadvantaged positions. |
| Shiranui | Phantom | Deception and disruption. Difficult to predict. |
| Kuroshio | Assassin | Waits for the optimal moment, then strikes and withdraws. |

These nine have internal conflicts. The Scholar and the Brawler disagree on tactics. The Blade has no patience for the Naval Academy. The Gatekeeper understands the danger of Type 93 torpedoes but lacks command authority. These fractures can be exploited.

---

## Monte Carlo Simulation Data

Over 1,800 simulated engagements yielded the following:

| Configuration | US Win | JP Win | Draw |
|:-------------|:------:|:------:|:----:|
| AI vs AI (pincer formation baseline) | 0% | 8.5% | 91.5% |
| JP optimal personality configuration | 0% | 10% | 90% |
| JP worst personality configuration | 0% | 2% | 98% |
| Personality flip test (JP personas commanding US) | 0% | 14-0% | — |

The flip test conclusion is clear: victory does not depend on AI parameter tuning. It depends on whether the human commander can recognize the gap between textbook doctrine and battlefield reality.

---

## Tactical Notes

1. SG radar is your primary advantage in night combat — 32km detection range versus 10-12km visual range for the Japanese. Protect the radar and prioritize engagement distance.
2. Concentrate fire on a single Japanese ship. The fleet has internal command fractures; losing a flagship amplifies them.
3. Iowa's 33-knot top speed provides engagement initiative — you choose when to close and when to disengage.
4. Secondary batteries are effective against destroyers within 8km. Entering secondary gun range early reduces Japanese torpedo attack capability.
5. Type 93 torpedoes cannot be detected by sonar or radar. By the time a wake is spotted visually, the window for evasive action is extremely narrow.

---

*"A good officer doesn't get killed. Only bad officers get killed."*
— Rear Admiral Arleigh Burke
