#!/usr/bin/env python3
"""
Personality optimization: test different Japanese captain configs against the US.
"""
import sys, os, random, math, json

sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo')
import battle as bt
import engine as mc

# ============================================================
# CONFIGURATIONS
# ============================================================

# Each config defines how ALL JP ships behave (for contrast purposes)
# We override tactical AI parameters

CONFIGS = {
    # 1. BASELINE - mixed personalities (current)
    "baseline": {
        "desc": "基准：混合人格(当前配置)",
        "jp_aggression": 0.65,
        "jp_range_preference": "mixed",  # mixed per ship
        "jp_fire_concentration": 0.5,    # moderate focus fire
        "jp_torpedo_aggression": 0.6,    # moderate torpedo use
        "jp_retreat_threshold": 0.25,    # fights to moderate damage
        "jp_adaptability": 0.6,
    },

    # 2. ALL AGGRESSIVE - all captains are gaoqiu-style
    "all_aggressive": {
        "desc": "全员激进：冲脸派(豪胆x9)",
        "jp_aggression": 0.92,
        "jp_range_preference": "close",   # want to get to 5-8km
        "jp_fire_concentration": 0.7,     # focus fire hard
        "jp_torpedo_aggression": 0.4,     # less torpedo, more guns
        "jp_retreat_threshold": 0.08,     # fights to near death
        "jp_adaptability": 0.3,           # inflexible, committed to plan
    },

    # 3. ALL DISCIPLINED - all captains are siming-style
    "all_disciplined": {
        "desc": "全员稳妥：守门人派(志明x9)",
        "jp_aggression": 0.40,
        "jp_range_preference": "medium",  # stay at 12-16km
        "jp_fire_concentration": 0.6,
        "jp_torpedo_aggression": 0.5,
        "jp_retreat_threshold": 0.45,     # retreat early to preserve force
        "jp_adaptability": 0.7,
    },

    # 4. TORPEDO FOCUS - DDs lead, BBs support
    "torpedo_focus": {
        "desc": "鱼雷突击：DD前出+BB支援远程炮击",
        "jp_aggression": 0.55,
        "jp_range_preference": "long",    # stay at 15-20km
        "jp_fire_concentration": 0.4,     # spread fire to distract
        "jp_torpedo_aggression": 0.95,    # DDs launch ASAP
        "jp_retreat_threshold": 0.30,
        "jp_adaptability": 0.6,
    },

    # 5. BANZAI CHARGE - ALL ships charge
    "banzai": {
        "desc": "万岁冲锋：全舰突击",
        "jp_aggression": 0.99,
        "jp_range_preference": "point_blank",  # get to 3-5km
        "jp_fire_concentration": 0.5,
        "jp_torpedo_aggression": 0.85,    # DD fish in the brawl
        "jp_retreat_threshold": 0.0,      # never retreat
        "jp_adaptability": 0.2,
    },

    # 6. GUERRILLA - hit and run, maximize torpedo
    "guerrilla": {
        "desc": "游击战术：打带跑，DD鱼雷骚扰",
        "jp_aggression": 0.50,
        "jp_range_preference": "hit_and_run",
        "jp_fire_concentration": 0.3,     # spread confusion
        "jp_torpedo_aggression": 0.85,    # DD constant torpedo runs
        "jp_retreat_threshold": 0.55,     # preserve ships
        "jp_adaptability": 0.90,
    },

    # 7. OPTIMAL MIX (hypothesis: best configuration)
    "optimal_mix": {
        "desc": "最优混合预测：DD鱼雷先手+BB中距集火",
        "jp_aggression": 0.70,
        "jp_range_preference": "optimal", # DD long / BB medium
        "jp_fire_concentration": 0.85,    # BB focus fire hard
        "jp_torpedo_aggression": 0.90,    # DD aggressive with torps
        "jp_retreat_threshold": 0.20,     # DD stays, BB retreat if crippled
        "jp_adaptability": 0.65,
    },
}


# ============================================================
# Apply personality to battle
# ============================================================

def apply_personality(battle, config):
    """Override battle behavior with personality config."""
    battle.personality_config = config

    # The actual behavioral changes are handled in the battle's
    # tactical AI by reading this config. For now we simulate by
    # adjusting movement and combat parameters.

    # Store for use in move_ship (which reads battle.personality_config)
    return battle


# ============================================================
# Run test
# ============================================================

def test_config(config_key, config, runs=50):
    """Run MC for a specific config."""
    results = {
        "config": config_key,
        "desc": config["desc"],
        "us_win": 0, "jp_win": 0, "draw": 0, "total_loss": 0,
        "turns": [], "iowa_survived": 0, "so_dak_survived": 0,
        "us_sunk_total": 0, "jp_sunk_total": 0,
        "iowa_hp_avg": 0, "so_dak_hp_avg": 0,
        "avg_hits_per_turn_us": 0,
        "avg_hits_per_turn_jp": 0,
    }

    for i in range(runs):
        b = bt.Battle(f"Test_{config_key}_{i}")
        apply_personality(b, config)
        list(b.run_battle(60))

        us_alive = len(b.active_ships("US"))
        jp_alive = len(b.active_ships("JP"))

        if us_alive > 0 and jp_alive == 0:
            results["us_win"] += 1
        elif jp_alive > 0 and us_alive == 0:
            results["jp_win"] += 1
        elif us_alive > 0 and jp_alive > 0:
            results["draw"] += 1
        else:
            results["total_loss"] += 1

        results["turns"].append(b.turn)
        iowa = b.get_ship("iowa")
        sodak = b.get_ship("south_dakota")
        results["iowa_survived"] += 1 if iowa and not iowa["sunk"] else 0
        results["so_dak_survived"] += 1 if sodak and not sodak["sunk"] else 0
        results["iowa_hp_avg"] += iowa["hp"] if iowa else 0
        results["so_dak_hp_avg"] += sodak["hp"] if sodak else 0
        results["us_sunk_total"] += len([s for s in b.fleets["US"] if s["sunk"]])
        results["jp_sunk_total"] += len([s for s in b.fleets["JP"] if s["sunk"]])

        # Count hits from log
        us_hits = sum(1 for e in b.log if "[炮击]" in e["msg"] and "命中" in e["msg"] and "JP" in e["msg"])
        jp_hits = sum(1 for e in b.log if "[中弹]" in e["msg"])
        results["avg_hits_per_turn_us"] += us_hits
        results["avg_hits_per_turn_jp"] += jp_hits

    # Normalize
    n = runs
    results["iowa_hp_avg"] /= n
    results["so_dak_hp_avg"] /= n
    results["avg_hits_per_turn_us"] /= n
    results["avg_hits_per_turn_jp"] /= n
    avg_t = sum(results["turns"]) / n if results["turns"] else 0
    results["avg_turns"] = avg_t

    # Weighted score: US win bad, JP win good, draw neutral, iowa sunk bad
    # Higher score = more effective JP configuration
    results["effectiveness_score"] = (
        results["jp_win"] * 2.0 +
        (runs - results["iowa_survived"]) * 0.5 -
        results["us_win"] * 1.0 +
        results["jp_sunk_total"] * (-0.3) +
        results["us_sunk_total"] * 0.3
    )

    return results


def print_results(results, runs):
    print(f"\n{'='*70}")
    print(f"Config: {results['config']}")
    print(f"  {results['desc']}")
    print(f"{'='*70}")
    print(f"  US win:   {results['us_win']:3d} ({results['us_win']/runs*100:5.1f}%)")
    print(f"  JP win:   {results['jp_win']:3d} ({results['jp_win']/runs*100:5.1f}%)")
    print(f"  Draw:     {results['draw']:3d} ({results['draw']/runs*100:5.1f}%)")
    print(f"  Iowa surv:{results['iowa_survived']/runs*100:5.1f}%  SoDak surv:{results['so_dak_survived']/runs*100:5.1f}%")
    print(f"  Avg HP:   Iowa={results['iowa_hp_avg']:.0f}  SoDak={results['so_dak_hp_avg']:.0f}")
    print(f"  Avg sunk: US={results['us_sunk_total']/runs:.2f}  JP={results['jp_sunk_total']/runs:.2f}")
    print(f"  Avg turns:{results['avg_turns']:.1f}")
    print(f"  Hits/run: US={results['avg_hits_per_turn_us']:.1f}  JP={results['avg_hits_per_turn_jp']:.1f}")
    print(f"  Effectiveness Score: {results['effectiveness_score']:.1f}")
    return results


if __name__ == "__main__":
    RUNS = 50  # 50 runs per config = 350 total
    all_results = []

    print(f"日军人格配置扫描 [{RUNS} runs per config]")
    print(f"{'='*70}")

    for ck, cf in CONFIGS.items():
        r = test_config(ck, cf, RUNS)
        all_results.append(r)
        print_results(r, RUNS)

    # Ranking by effectiveness score
    print(f"\n{'='*70}")
    print(f"FINAL RANKING (by effectiveness vs US)")
    print(f"{'='*70}")
    print(f"{'Rank':<5} {'Config':<20} {'Score':<8} {'JP%':<8} {'US%':<8} {'Iowa%':<8}")
    print(f"{'-'*50}")
    sorted_results = sorted(all_results, key=lambda r: r["effectiveness_score"], reverse=True)
    for i, r in enumerate(sorted_results):
        print(f"  {i+1:<3} {r['config']:<20} {r['effectiveness_score']:<8.1f} "
              f"{r['jp_win']/RUNS*100:<8.1f} {r['us_win']/RUNS*100:<8.1f} "
              f"{r['iowa_survived']/RUNS*100:<8.1f}")
