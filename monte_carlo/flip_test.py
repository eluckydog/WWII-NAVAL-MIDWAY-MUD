#!/usr/bin/env python3
"""
Flip test: put each of the 9 Japanese captain personalities on US Iowa,
replace the Burke player. See how well each personality commands US forces.
"""
import sys, os, json, math
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo')
import battle as bt
import engine as mc

# ============================================================
# MAP Japanese personalities to US command behavior
# ============================================================

PERSONA_MAP = {
    # BB Captains
    "xiucai": {
        "name": "秀才·長門舰长",
        "desc": "战术学院派，纸上谈兵，反应慢，分析瘫痪",
        "us_aggression": 0.40,
        "us_range_close": 10,   # prefers 10-18km
        "us_range_open": 18,
        "us_decisiveness": 0.35,  # Slow to decide
        "us_adaptability": 0.30,
        "us_torpedo_aversion": 0.0,  # Not relevant for US
        "us_retreat_threshold": 0.30,
    },
    "gaoqiu": {
        "name": "豪胆·陸奥舰长",
        "desc": "大舰巨炮狂热，冲脸近战，藐视雷达",
        "us_aggression": 0.95,
        "us_range_close": 3,
        "us_range_open": 12,
        "us_decisiveness": 0.90,
        "us_adaptability": 0.20,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.05,
    },
    "duanyu": {
        "name": "断雨·金剛舰长",
        "desc": "闪电快刀，实战派，高适应，冷静果断",
        "us_aggression": 0.70,
        "us_range_close": 5,
        "us_range_open": 14,
        "us_decisiveness": 0.85,
        "us_adaptability": 0.85,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.20,
    },
    "siming": {
        "name": "志明·榛名舰长",
        "desc": "帝国守门人，耐心消耗，防御优先",
        "us_aggression": 0.40,
        "us_range_close": 8,
        "us_range_open": 18,
        "us_decisiveness": 0.70,
        "us_adaptability": 0.70,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.35,
    },
    # DD Captains (now commanding a BB - interesting adaptation)
    "yukikaze_sim": {
        "name": "雪風精神",
        "desc": "被命运眷顾的赌徒——'反正打不中我'",
        "us_aggression": 0.92,
        "us_range_close": 3,
        "us_range_open": 13,
        "us_decisiveness": 0.88,
        "us_adaptability": 0.40,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.15,
    },
    "kagero_sim": {
        "name": "陽炎精神",
        "desc": "武士道——荣誉高于生死的标准指挥官",
        "us_aggression": 0.75,
        "us_range_close": 5,
        "us_range_open": 15,
        "us_decisiveness": 0.70,
        "us_adaptability": 0.45,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.15,
    },
    "isokaze_sim": {
        "name": "磯風精神",
        "desc": "海狼猎人——小搏大专家，战术诡诈",
        "us_aggression": 0.60,
        "us_range_close": 6,
        "us_range_open": 16,
        "us_decisiveness": 0.65,
        "us_adaptability": 0.80,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.30,
    },
    "shiranui_sim": {
        "name": "不知火精神",
        "desc": "鬼火——心理战，欺骗，永远让敌人猜不透",
        "us_aggression": 0.50,
        "us_range_close": 7,
        "us_range_open": 17,
        "us_decisiveness": 0.55,
        "us_adaptability": 0.85,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.35,
    },
    "kuroshio_sim": {
        "name": "黒潮精神",
        "desc": "沉默暗杀者——冷静、致命、无废话",
        "us_aggression": 0.70,
        "us_range_close": 5,
        "us_range_open": 14,
        "us_decisiveness": 0.90,
        "us_adaptability": 0.65,
        "us_torpedo_aversion": 0.0,
        "us_retreat_threshold": 0.15,
    },
}


# ============================================================
# MODIFIED BATTLE with US personality override
# ============================================================

class PersonalityBattle(bt.Battle):
    """Extended Battle that accepts US-side personality overrides."""

    def __init__(self, name, seed, us_cfg):
        super().__init__(name, seed)
        self.us_cfg = us_cfg
        # JP uses the mixed baseline (no override)
        self.personality_config = None

    def get_us_personality(self):
        return getattr(self, "us_cfg", None)

    def move_ship(self, ship):
        """Override: apply US personality when moving US ships."""
        if ship["sunk"]:
            return
        spd = min(ship["speed_kt"], ship["max_speed_kt"])
        enemies = [e for e in self.active_ships() if e["side"] != ship["side"]]
        nearest = min(enemies, key=lambda e: self.distance_between(ship, e)) if enemies else None

        if nearest and ship["rudder_state"] not in ["jammed", "lost"]:
            dist = self.distance_between(ship, nearest)
            bearing = self.bearing_between(ship, nearest)

            if ship["side"] == "US":
                us_cfg = self.get_us_personality()
                if us_cfg:
                    agg = us_cfg.get("us_aggression", 0.65)
                    close_r = us_cfg.get("us_range_close", 6)
                    open_r = us_cfg.get("us_range_open", 16)

                    if dist > open_r:
                        speed_f = 0.3 + agg * 0.4
                        desired = (bearing + 180) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        ship["heading"] += max(-6, min(6, diff * speed_f))
                    elif dist < close_r:
                        desired = (bearing + 80) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        turn_r = 1 + agg * 2
                        ship["heading"] += max(-turn_r, min(turn_r, diff * 0.15))
                    else:
                        desired = (bearing + 80) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        turn_r = 2 + agg * 2
                        ship["heading"] += max(-turn_r, min(turn_r, diff * 0.25))
                else:
                    # Default US
                    if dist > 14:
                        desired = (bearing + 180) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        ship["heading"] += max(-6, min(6, diff * 0.4))
                    elif dist < 6:
                        desired = (bearing + 60) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        ship["heading"] += max(-4, min(4, diff * 0.2))
                    else:
                        desired = (bearing + 80) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        ship["heading"] += max(-4, min(4, diff * 0.25))
            else:
                # JP: baseline mixed
                if dist > 16:
                    desired = (bearing + 180) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-6, min(6, diff * 0.4))
                elif dist < 6:
                    desired = (bearing + 120) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-4, min(4, diff * 0.2))
                else:
                    desired = (bearing + 280) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-4, min(4, diff * 0.25))

        ship["heading"] = (ship["heading"] + 360) % 360
        dist_moved = spd * 1.852 * (3.0 / 60.0)
        hdg_rad = math.radians(ship["heading"])
        ship["position"][0] += dist_moved * math.sin(hdg_rad)
        ship["position"][1] += dist_moved * math.cos(hdg_rad)


# ============================================================
# RUN TESTS
# ============================================================

RUNS = 50

def test_persona(persona_key, persona_data):
    runs = []
    for i in range(RUNS):
        b = PersonalityBattle(f"Test_{persona_key}_{i}", None, persona_data)
        list(b.run_battle(60))
        runs.append({
            "us_alive": len(b.active_ships("US")),
            "jp_alive": len(b.active_ships("JP")),
            "turn": b.turn,
            "iowa_alive": b.get_ship("iowa") and not b.get_ship("iowa")["sunk"],
            "sodak_alive": b.get_ship("south_dakota") and not b.get_ship("south_dakota")["sunk"],
            "iowa_hp": b.get_ship("iowa")["hp"] if b.get_ship("iowa") else 0,
            "sodak_hp": b.get_ship("south_dakota")["hp"] if b.get_ship("south_dakota") else 0,
        })

    us_win = sum(1 for r in runs if r["us_alive"] > 0 and r["jp_alive"] == 0)
    jp_win = sum(1 for r in runs if r["jp_alive"] > 0 and r["us_alive"] == 0)
    draws = sum(1 for r in runs if r["us_alive"] > 0 and r["jp_alive"] > 0)
    total_loss = sum(1 for r in runs if r["us_alive"] == 0 and r["jp_alive"] == 0)
    iowa_surv = sum(1 for r in runs if r["iowa_alive"])
    sodak_surv = sum(1 for r in runs if r["sodak_alive"])
    avg_iowa_hp = sum(r["iowa_hp"] for r in runs) / RUNS
    avg_sodak_hp = sum(r["sodak_hp"] for r in runs) / RUNS
    avg_turn = sum(r["turn"] for r in runs) / RUNS

    return {
        "persona": persona_key,
        "name": persona_data["name"],
        "desc": persona_data["desc"],
        "us_win": us_win,
        "jp_win": jp_win,
        "draws": draws,
        "total_loss": total_loss,
        "iowa_surv": iowa_surv,
        "sodak_surv": sodak_surv,
        "avg_iowa_hp": avg_iowa_hp,
        "avg_sodak_hp": avg_sodak_hp,
        "avg_turn": avg_turn,
    }


def print_result(r):
    print(f"\n{'='*60}")
    print(f"[{r['persona']}] {r['name']}")
    print(f"  {r['desc']}")
    print(f"{'='*60}")
    print(f"  US win: {r['us_win']:3d} ({r['us_win']/RUNS*100:5.1f}%)")
    print(f"  JP win: {r['jp_win']:3d} ({r['jp_win']/RUNS*100:5.1f}%)")
    print(f"  Draw:   {r['draws']:3d} ({r['draws']/RUNS*100:5.1f}%)")
    print(f"  Iowa存活: {r['iowa_surv']/RUNS*100:5.1f}%  (残HP:{r['avg_iowa_hp']:.0f})")
    print(f"  SoDak存活:{r['sodak_surv']/RUNS*100:5.1f}%  (残HP:{r['avg_sodak_hp']:.0f})")
    print(f"  平均回合: {r['avg_turn']:.1f}")

    # Difficulty rating
    if r["us_win"] == 0:
        diff = "地狱级 Impossible"
    elif r["us_win"]/RUNS < 0.10:
        diff = "非常困难 Very Hard"
    elif r["us_win"]/RUNS < 0.30:
        diff = "困难 Hard"
    elif r["us_win"]/RUNS < 0.50:
        diff = "中等 Medium"
    else:
        diff = "简单 Easy"
    print(f"  难度评级: {diff}")
    return r


if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"人格翻转测试：9个日军舰长指挥美军 vs 标准日军")
    print(f"每人 {RUNS} 场蒙特卡洛")
    print(f"{'='*60}")

    results = []
    for pk, pd in PERSONA_MAP.items():
        r = test_persona(pk, pd)
        results.append(r)
        print_result(r)

    # Rankings
    print(f"\n{'='*60}")
    print(f"最终排名（按美军胜率排序）")
    print(f"{'='*60}")
    print(f"{'排名':<5} {'人格':<16} {'美军胜率':<12} {'日胜率':<10} {'Iowa生存':<10}")
    print(f"{'─'*55}")
    sorted_results = sorted(results, key=lambda r: r["us_win"], reverse=True)
    for i, r in enumerate(sorted_results):
        print(f"  {i+1:<3} {r['persona']:<16} {r['us_win']/RUNS*100:<10.1f}%"
              f"{r['jp_win']/RUNS*100:<8.1f}% {r['iowa_surv']/RUNS*100:<8.1f}%")

    # Also show Arleigh Burke comparison from earlier
    print(f"\n{'─'*55}")
    print(f"  参考: 阿利·伯克(人类) 胜率预估 ~5-10%")
    print(f"{'─'*55}")

    # Bonus: hardest and easiest
    best = max(results, key=lambda r: r["us_win"])
    worst = min(results, key=lambda r: r["us_win"])
    print(f"\n🎖 最佳美舰指挥官: {best['persona']} ({best['name']})")
    print(f"   胜率 {best['us_win']/RUNS*100:.1f}%")
    print(f"\n💀 最差美舰指挥官: {worst['persona']} ({worst['name']})")
    print(f"   胜率 {worst['us_win']/RUNS*100:.1f}%")
