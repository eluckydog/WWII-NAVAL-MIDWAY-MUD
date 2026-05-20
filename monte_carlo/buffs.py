#!/usr/bin/env python3
"""
Yukikaze Buff System.
Historical sources: CombinedFleet.com, NHHC, Japan Center for Asian Historical Records
"""
import random

# Each buff: id, names, desc, probability, modifiers, immunities
BUFFS = []

def reg(id_, cn, en, dcn, den, prob, mods, imms):
    BUFFS.append({
        "id": id_,
        "name_cn": cn,
        "name_en": en,
        "desc_cn": dcn,
        "desc_en": den,
        "probability": prob,
        "applies_to": "self",
        "modifiers": mods,
        "immunities": imms,
        "active": True,
    })

reg("yukikaze_heavens_protection",
    "天命加护", "Heaven's Protection",
    "雪风号携带着一种无形的庇佑——弹片绕着她走，引信在她身边熄灭。她活过了所有战斗，从未沉没。",
    "Yukikaze carries an invisible protection: shrapnel veers around her, fuses sputter out. She outlived every battle, never sunk.",
    0.20,
    {"evasion_bonus_pct": 35, "critical_resist_pct": 60, "fire_spread_chance_mult": 0.4,
     "torpedo_dodge_pct": 25, "flood_severity_mult": 0.5,
     "magazine_safe_pct": 70},
    ["catastrophic_magazine", "flood_critical"])

reg("yukikaze_adjacent_misfortune",
    "身边的厄运", "Nearby Misfortune",
    "跟她编队出击的舰船，沉没率高于统计平均。也许因为她拒绝沉没，厄运必须找上别人。",
    "Ships sortieing with Yukikaze sink above statistical average. Perhaps because she refuses to sink, misfortune finds others.",
    0.15,
    {"ally_critical_mult": 1.5, "ally_evasion_reduction": -15},
    [])

reg("yukikaze_survivor_will",
    "归乡意志", "Will to Return",
    "雪风的舰长有一种近乎偏执的信念：这条船一定会回去。轮机舱的老兵说这艘船自己就想回家。",
    "Her captain carries a paranoid conviction: this ship will return. Old engine hands say the ship itself wants to go home.",
    0.10,
    {"hull_integrity_regen": 5, "speed_retention_pct": 25, "crew_recovers_pct": 20},
    [])

reg("yukikaze_curse_of_luck",
    "幸运的诅咒", "Curse of Luck",
    "雪风的龙骨里嵌着一枚明治时期的铜钱。没有人亲眼见过。但她从未战沉——她只是在每一场败仗中活了下来。",
    "A Meiji-era copper coin is embedded in her keel. No one has seen it. But she never sank in battle — merely survived every defeat.",
    0.20,
    {"evasion_bonus_pct": 20, "last_stand_hp_threshold": 25},
    ["one_hit_kill"])

reg("yukikaze_spectre_fleet",
    "幽灵舰队", "Spectre Fleet",
    "莱特湾后，瞭望哨发誓说他看到了三条驱逐舰的轮廓跟在雪风的尾迹里。那些舰本该早在几天前就沉了。舰长没有记录。有些事还是不提为好。",
    "After Leyte, a lookout swore he saw three destroyer silhouettes in Yukikaze's wake. Ships that should have sunk days ago. The captain didn't log it. Some things are better left at sea.",
    0.08,
    {"ghost_ship_decoy_chance": 25},
    [])


def roll_buffs():
    """Roll all buffs, return list of active buff IDs."""
    active = []
    for b in BUFFS:
        if random.random() < b["probability"]:
            active.append(b["id"])
    return active


def get_modifiers(buff_ids):
    """Aggregate modifier values from active buffs."""
    agg = {}
    for b in BUFFS:
        if b["id"] in buff_ids:
            for k, v in b["modifiers"].items():
                agg[k] = agg.get(k, 0) + v
    return agg


def get_immunities(buff_ids):
    """Aggregate immunity list."""
    imms = set()
    for b in BUFFS:
        if b["id"] in buff_ids:
            imms.update(b["immunities"])
    return imms


def describe_buffs(buff_ids, cn=True):
    """Return list of flavor strings for active buffs."""
    out = []
    for b in BUFFS:
        if b["id"] in buff_ids:
            out.append(f"[{b['name_cn'] if cn else b['name_en']}] {b['desc_cn'] if cn else b['desc_en']}")
    return out


if __name__ == "__main__":
    from collections import Counter
    cnt = Counter()
    N = 50000
    for _ in range(N):
        active = roll_buffs()
        cnt[len(active)] += 1
    print(f"Yukikaze buff distribution ({N} trials):")
    print(f"  No buffs: {cnt[0]/N*100:.1f}%")
    print(f"  1 buff:   {cnt[1]/N*100:.1f}%")
    print(f"  2 buffs:  {cnt[2]/N*100:.1f}%")
    print(f"  3+ buffs: {sum(cnt[i] for i in range(3,10))/N*100:.1f}%")
    print(f"\nExpected probability: at least 1 buff = {1 - (1-0.20)*(1-0.15)*(1-0.10)*(1-0.20)*(1-0.08):.1%}")
