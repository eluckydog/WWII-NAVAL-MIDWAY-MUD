#!/usr/bin/env python3
"""
Monte Carlo battle engine for WWII naval combat.
Resolution: 3 min/turn. Probability-driven, fully cascading.
"""

import random, math, unicodedata
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data
import buffs

# ============================================================
# Structured event system (added by code review fix)
# ============================================================

def mk_event(phase, etype, **kw):
    """Create a structured event dict."""
    ev = {"phase": phase, "type": etype}
    ev.update(kw)
    return ev


def format_event(ev):
    """Format a structured event as a human-readable string (backwards compat)."""
    p = ev.get("phase", "?")
    t = ev.get("type", "?")
    ship = ev.get("ship", ev.get("ship_name", "?"))
    target = ev.get("target", "")
    
    if p == "radar" and t == "detect":
        return f"[radar] {ship} at {ev.get('dist',0):.1f}km bearing {ev.get('bearing',0):.0f} {ev.get('size','')}"
    if p == "radar" and t == "status":
        return f"[radar] {ship}: {ev.get('msg','')}"
    if p == "visual":
        return f"[visual] {ship} sighted at bearing {ev.get('bearing',0):.0f}"
    if p == "torpedo_launch":
        return f"[torpedo] {ship} fires {ev.get('tubes',6)} tubes at {target} range {ev.get('dist',0):.1f}km"
    if p == "torpedo_hit":
        return f"[torpedo_hit] {target}! dmg={ev.get('dmg',0)} flood={ev.get('flood_pct',0):.1f}%"
    if p == "gunnery" and t == "hit":
        return f"[gunnery] {ship} hits {target} x{ev.get('hits',1)} ({ev.get('location','')}) dmg={ev.get('dmg',0)}"
    if p == "gunnery" and t == "miss":
        return f"[gunnery] {ship} misses {target}"
    if p == "damage" and t == "hit":
        return f"[damage] {ship} takes {ev.get('dmg',0)}HP hit"
    if p == "damage" and t == "crit":
        return f"[damage] {ship} critical hit! {ev.get('dmg',0)}HP"
    if p == "fire":
        return f"[fire] {ship}: {ev.get('desc','')}"
    if p == "flood":
        return f"[flood] {ship}: {ev.get('desc','')}"
    if p == "sink":
        return f"[sink] {ship} sunk!"
    if p == "turn":
        return f"--- Turn {ev.get('turn','')} | {ev.get('time','')} ---"
    return str(ev)


# Seed reproducibility
SEED = None


# ============================================================
# Yukikaze buff integration
# ============================================================

def check_yukikaze_buffs(ship, mod_type):
    """Check if a ship has Yukikaze buffs for a modifier type.
    Returns the modifier value (0 if none)."""
    return ship.get(mod_type, 0)

def apply_yukikaze_evasion(hit_pct, target):
    """Reduce hit_pct based on Yukikaze evasion bonus."""
    bonus = target.get("_evasion_bonus", 0)
    if bonus > 0:
        return max(0.1, hit_pct * (1 - bonus / 100))
    return hit_pct

def apply_magazine_protection(target):
    prot = target.get("_magazine_protect", 0)
    return prot > 0 and random.random() < prot / 100

def apply_critical_resist(target):
    resist = target.get("_crit_resist", 0)
    return max(0.3, 1.0 - resist / 100) if resist > 0 else 1.0

def apply_torpedo_evasion(target):
    evade = target.get("_torpedo_evade", 0)
    return evade > 0 and random.random() < evade / 100

def set_seed(s):
    global SEED
    SEED = s
    random.seed(s)


# ============================================================
# RNG utilities
# 卢俊义上梁山的路数，跟这d100差不多了
# ============================================================

def d100():
    return random.randint(1, 100)

def d(n):
    return random.randint(1, n)

def roll_chance(pct):
    """Return True if a percentage check passes."""
    return random.random() < (pct / 100.0)

def pick_weighted(options):
    """Pick from [(value, weight), ...]"""
    total = sum(w for _, w in options)
    r = random.random() * total
    cum = 0
    for val, w in options:
        cum += w
        if r < cum:
            return val
    return options[-1][0]


# ============================================================
# SHIP STATE
# ============================================================

def create_ship_state(ship_key):
    """Create mutable battle state for a ship."""
    s = dict(data.SHIPS[ship_key])
    # Mutable state
    s["id"] = ship_key
    s["hp"] = float(data.SHIPS[ship_key]["hp"])
    s["max_hp"] = float(data.SHIPS[ship_key]["max_hp"])
    s["sunk"] = False
    s["speed_kt"] = s.get("speed_cruise_kt", 18)
    s["max_speed_kt"] = s["speed_max_kt"]
    s["heading"] = 0.0
    s["position"] = [0.0, 0.0]  # [x_km, y_km]
    s["fires"] = []  # fire severity list
    s["flood_level"] = 0.0  # accumulated flood % of displacement
    s["list_deg"] = 0.0
    s["rudder_state"] = "working"  # working / jammed / lost
    s["rudder_angle"] = 0.0
    s["fire_control"] = "working"  # working / damaged / out
    s["radar_online"] = True
    s["radar_drop_turns"] = 0  # turns remaining offline
    s["main_guns_operational"] = s["main_guns"]
    s["main_guns_total"] = s["main_guns"]
    s["secondary_guns_operational"] = s.get("secondary_guns", 0)
    s["secondary_guns_total"] = s.get("secondary_guns", 0)
    s["ammo_type"] = "AP"
    s["secondary_ammo_type"] = "HC"
    s["torpedoes_remaining"] = s.get("torpedoes", 0)
    s["aircraft"] = s.get("aircraft", 0)
    s["aircraft_operational"] = s["aircraft"]
    s["aircraft_ready"] = s["aircraft_operational"]
    s["aircraft_catapults"] = s.get("aircraft_catapults", 0)
    s["catapults_operational"] = s["aircraft_catapults"]
    s["main_barrel_length"] = s.get("main_barrel_length", 45)
    s["persona_id"] = None  # assigned at battle start
    s["tactical_state"] = "advancing"  # advancing/retreating/disabled/circling
    # Damage log
    s["damage_log"] = []
    return s


# ============================================================
# DETECTION
# ============================================================

def check_detection(sensor_ship, target_ship, distance_km, night=True, weather=1.0):
    """
    Returns True if sensor_ship detects target_ship at given distance.
    weather: 1.0 = clear, 0.7 = rain squalls
    """
    # Radar check
    if sensor_ship["radar_online"] and sensor_ship.get("has_sg_radar", False):
        max_radar_km = sensor_ship.get("sg_radar_range_m", 32000) / 1000.0
        effective_range = max_radar_km * weather * 0.9
        if distance_km <= effective_range:
            return True

    if sensor_ship.get("has_type21_radar", False) and sensor_ship["radar_online"]:
        max_type21 = sensor_ship.get("type21_range_m", 20000) / 1000.0
        effective = max_type21 * weather * 0.9
        if distance_km <= effective:
            return True

    # Optical detection (night, no moon)
    if not night:
        optical_limit = 10 * weather
    else:
        optical_limit = 5 * weather  # moonless night

    if distance_km <= optical_limit:
        # Size modifier: BB easier, DD harder
        size_mod = 1.5 if "bb" in sensor_ship.get("class", "").lower() else 1.0
        return roll_chance(max(10, 80 - distance_km * 12) * size_mod)

    return False


# ============================================================
# RADAR FAILURE
# ============================================================

def update_radar(ship):
    """Check radar reliability. Return (was_online, message)."""
    was_online = ship["radar_online"]

    if ship["radar_drop_turns"] > 0:
        ship["radar_drop_turns"] -= 1
        if ship["radar_drop_turns"] == 0:
            ship["radar_online"] = True
            return (was_online, f"雷达恢复工作")

    if ship["radar_online"]:
        # Check for SG radar failure
        if ship.get("has_sg_radar", False):
            re = ship.get("sg_reliability", 0.75)
            if random.random() > re:
                ship["radar_online"] = False
                drop_t = ship.get("sg_drop_turns", (1, 3))
                ship["radar_drop_turns"] = random.randint(*drop_t)
                return (was_online, f"SG雷达真空管故障！预计离线{ship['radar_drop_turns']}回合")

        # Type 21 radar
        if ship.get("has_type21_radar", False):
            re = ship.get("type21_reliability", 0.30)
            if random.random() > re:
                ship["radar_online"] = False
                drop_t = ship.get("type21_drop_turns", (2, 6))
                ship["radar_drop_turns"] = random.randint(*drop_t)
                return (was_online, f"21号电探故障！预计离线{ship['radar_drop_turns']}回合")

    return (was_online, None)


# ============================================================
# GUNNERY
# ============================================================

def compute_hit_pct(gun_key, distance_km, shooter, target, weather=1.0, accuracy_mod=1.0):
    """
    Compute single-gun hit probability for one salvo.
    Based on WWII statistical analysis.
    accuracy_mod: persona accuracy modifier (1.0 = baseline)
    """
    # Base hit rate at different ranges
    if distance_km < 10:
        base_pct = 8.0  # ~8% per gun at close range
    elif distance_km < 15:
        base_pct = 5.0
    elif distance_km < 20:
        base_pct = 3.0
    elif distance_km < 25:
        base_pct = 1.5
    elif distance_km < 30:
        base_pct = 0.8
    else:
        base_pct = 0.3
    
    # Persona accuracy modifier
    base_pct *= accuracy_mod

    # Fire control modifier
    if shooter["fire_control"] == "damaged":
        base_pct *= 0.4
    elif shooter["fire_control"] == "out":
        base_pct *= 0.1

    # Radar fire control bonus (US)
    if shooter.get("has_fc_radar", False) and shooter["radar_online"] and distance_km < 25:
        base_pct *= 1.5  # Mk13 radar FC = 1.5x base hit rate

    # Shooter speed penalty
    speed_penalty = 1.0 - (shooter["speed_kt"] / 40.0) * 0.3
    base_pct *= speed_penalty

    # Target speed penalty
    target_speed_mod = 1.0 - (target["speed_kt"] / 35.0) * 0.2
    base_pct *= target_speed_mod

    # Ship damage penalty
    damage_pct = 1.0 - (shooter["hp"] / shooter["max_hp"])
    if damage_pct > 0.3:
        base_pct *= (1.0 - (damage_pct - 0.3))

    # Weather
    base_pct *= weather

    # Cap
    hit_pct = apply_yukikaze_evasion(base_pct, target)
    return min(hit_pct, 25.0)


def roll_hit_location(target=None):
    """Roll d100 and return hit location key."""
    roll = d100()
    for (lo, hi, key, _) in data.HIT_LOCATIONS:
        if lo <= roll <= hi:
            if key == "magazine" and apply_magazine_protection(target): return "belt"
            return key
    return "miss"


def compute_gunnery_effect(hit_loc_key, gun_key, distance_km, target):
    """
    Given a hit location and gun/shell data, determine if shell penetrates and
    what damage category it causes.
    Returns (effect_key, weight, description)
    """
    effect_roll = d100()

    table = data.DAMAGE_TABLES.get(hit_loc_key, [("no_effect", 1.0, "无伤")])
    cum = 0.0
    chosen = table[-1]
    for effect_key, weight, desc in table:
        cum += weight * 100.0
        if effect_roll <= cum:
            chosen = (effect_key, weight, desc)
            break

    return chosen


# ============================================================
# TORPEDO SYSTEM
# 西门庆娶李瓶儿的时候要是遇到九三式，就没后面的事了
# ============================================================

class Torpedo:
    """Represents a single torpedo in the water."""
    def __init__(self, launcher_id, launch_pos, target_id, heading, speed_kt, range_m, warhead_kg, wake_vis):
        self.id = f"torp_{random.randint(10000, 99999)}"
        self.launcher_id = launcher_id
        self.x = launch_pos[0]
        self.y = launch_pos[1]
        self.target_id = target_id
        self.heading = heading
        self.speed_kt = speed_kt
        self.speed_kms = speed_kt * 0.000514  # kt to km/s
        self.range_m = range_m
        self.range_km = range_m / 1000.0
        self.traveled_km = 0.0
        self.warhead_kg = warhead_kg
        self.wake_vis = wake_vis
        self.active = True
        self.armed = False
        self.turns_in_water = 0

    def update(self, turn_duration_min=3):
        if not self.active:
            return None
        dist = self.speed_kms * turn_duration_min * 60.0  # km per turn
        self.traveled_km += dist
        self.turns_in_water += 1

        if self.traveled_km >= self.range_km:
            self.active = False
            return f"鱼雷[{self.id[:6]}]到达极限航程自沉"

        if not self.armed and self.traveled_km >= 0.5:  # 500m arming distance
            self.armed = True

        # Update position (simple linear)
        heading_rad = math.radians(self.heading)
        self.x += dist * math.sin(heading_rad)
        self.y += dist * math.cos(heading_rad)
        return None

    def hit_check(self, target_pos, target_length_m, target_speed_kt, target_heading, accuracy_mod=1.0, target_ship=None):
        """Check if torpedo hits target this turn. accuracy_mod: persona mod (1.0=baseline)."""
        if not self.active or not self.armed:
            return False

        # Distance between torpedo and target
        dx = self.x - target_pos[0]
        dy = self.y - target_pos[1]
        dist_km = math.hypot(dx, dy)

        # If torpedo has passed or is very close
        if dist_km < 0.2:  # within 200m
            # Hit chance based on target aspect, speed, torpedo spread
            hit_chance = 60.0  # base
            # Target speed => harder to hit
            hit_chance -= target_speed_kt * 0.5
            # Target length => easier for bigger
            hit_chance += target_length_m * 0.02
            if self.traveled_km < 3:
                hit_chance += 10
            # Apply torpedo_evasion buff if target has it (Yukikaze)
            if target_ship and target_ship.get("_torpedo_evade", 0) > 0:
                if apply_torpedo_evasion(target_ship):
                    return False
            return roll_chance(max(5, hit_chance))

        return False

    def check_detection(self, observer_ship, distance_km, night=True):
        """Can observer detect this torpedo? Returns True if spotted."""
        if not self.active:
            return False

        # Base wake visibility (Type 93 is nearly invisible)
        wake_base = self.wake_vis

        # Distance modifier
        dist_mod = max(0.1, 1.0 - distance_km / 2.0)

        # Night makes it harder
        night_mod = 0.5 if night else 1.0

        # Running time: longer = more visible (CO2 bubbles start showing)
        time_mod = min(2.0, 1.0 + self.turns_in_water * 0.05)

        detection_chance = wake_base * 100 * dist_mod * night_mod * time_mod
        if detection_chance > 5:
            return roll_chance(detection_chance)
        return False


# ============================================================
# DAMAGE APPLICATION
# ============================================================

def apply_damage(ship, effect_key, gun_key=None, distance_km=20, damage_mod=1.0):
    """Apply a damage effect to a ship. Returns description string."""
    event = f"[{ship['id']}] "

    if effect_key == "no_effect":
        return None

    elif effect_key == "fire_start" or effect_key == "fire":
        ship["fires"].append(random.randint(1, 3))  # severity 1-3
        event += "起火！"

    elif effect_key == "minor_fire":
        ship["fires"].append(1)
        event += "小火灾"

    elif effect_key == "flood_minor":
        ship["flood_level"] += 2
        ship["hp"] -= 10
        event += "小规模进水（+2%）"

    elif effect_key == "flood_moderate":
        ship["flood_level"] += 5
        ship["hp"] -= 30
        event += "中等进水（+5%）"

    elif effect_key == "flood_severe":
        ship["flood_level"] += 10
        ship["hp"] -= 80
        event += "严重进水（+10%）"

    elif effect_key == "rapid_flooding":
        ship["flood_level"] += 20
        ship["hp"] -= 150
        event += "猛烈进水（+20%）"

    elif effect_key == "fire_control_damage":
        ship["fire_control"] = "damaged"
        event += "火控系统受损"

    elif effect_key == "radar_damage":
        ship["radar_online"] = False
        ship["radar_drop_turns"] = random.randint(3, 6)
        event += f"雷达损坏（预计{ship['radar_drop_turns']}回合修复）"

    elif effect_key == "crew_casualty":
        event += "人员伤亡"

    elif effect_key == "comm_damage":
        event += "通讯设备损坏"

    elif effect_key == "command_kill":
        ship["fire_control"] = "out"
        event += "舰桥人员伤亡！指挥链中断"

    elif effect_key == "navigation_damage":
        event += "导航设备损坏"

    elif effect_key == "steering_control_cut":
        ship["rudder_state"] = "jammed"
        event += "操舵线路中断"

    elif effect_key == "penetrate_vitals" or effect_key == "deck_penetrate":
        burst = data.WEAPONS[gun_key]["burst_charge_kg"] if gun_key else 18
        damage = 120 + burst * 4 + random.uniform(0, 50)
        ship["hp"] -= damage
        if roll_chance(15):
            ship["fires"].append(5)
            event += f"核心区穿透！弹药库临近起火！[-{damage:.0f}HP]"
        else:
            event += f"核心区穿透！内部严重损坏[-{damage:.0f}HP]"

    elif effect_key == "semi_penetrate":
        damage = 50 + random.uniform(0, 40)
        ship["hp"] -= damage
        event += f"半穿甲弹→内部中度损伤[-{damage:.0f}HP]"

    elif effect_key == "bounce":
        event += "跳弹！无穿透"

    elif effect_key == "belt_damage":
        event += "主装甲带损伤（防护下降）"

    elif effect_key == "turret_jam":
        ops = max(0, ship["main_guns_operational"] - 3)
        ship["main_guns_operational"] = ops
        event += f"炮塔卡死！可用火炮减少3门"

    elif effect_key == "magazine_flashover" or effect_key == "magazine_explosion":
        resist = apply_critical_resist(ship)
        dmg = 800 * resist
        ship["hp"] -= dmg
        ship["fires"].append(10)
        event += f"弹药库爆燃！大规模殉爆！[-{dmg:.0f}HP]"

    elif effect_key == "gun_damage":
        ship["main_guns_operational"] = max(0, ship["main_guns_operational"] - 1)
        event += "一门主炮损坏"

    elif effect_key == "rudder_jammed":
        ship["rudder_state"] = "jammed"
        event += "舵叶卡死"

    elif effect_key == "rudder_lost":
        ship["rudder_state"] = "lost"
        event += "舵叶丢失！无法操控"

    elif effect_key == "propeller_lost":
        ship["max_speed_kt"] = max(ship["max_speed_kt"] * 0.6, 5)
        ship["speed_kt"] = min(ship["speed_kt"], ship["max_speed_kt"])
        event += "螺旋桨丢失！航速大幅下降"

    elif effect_key == "boiler_damage":
        ship["max_speed_kt"] = max(ship["max_speed_kt"] * 0.7, 8)
        if ship["speed_kt"] > ship["max_speed_kt"]:
            ship["speed_kt"] = ship["max_speed_kt"]
        event += "锅炉损坏！航速下降"

    elif effect_key == "engine_room_flood":
        ship["flood_level"] += 8
        ship["max_speed_kt"] = max(ship["max_speed_kt"] * 0.5, 5)
        ship["hp"] -= 50
        event += "机舱进水！动力大幅下降"

    elif effect_key == "steam_pipe_burst":
        ship["max_speed_kt"] = max(ship["max_speed_kt"] * 0.5, 5)
        event += "蒸汽管道爆裂！航速急剧下降"

    elif effect_key == "catastrophic_machinery":
        ship["speed_kt"] = 0
        ship["max_speed_kt"] = 2
        ship["hp"] -= 200
        event += "主机报废！动力丧失[-200HP]"

    elif effect_key == "catastrophic":
        resist = apply_critical_resist(ship)
        dmg = 1000 * resist
        ship["hp"] -= dmg
        event += f"致命命中！舰体毁灭性损伤[-{dmg:.0f}HP]"

    elif effect_key == "keel_broken":
        ship["hp"] = 0
        event += "龙骨断裂！舰体折毁"

    elif effect_key == "minor_damage":
        ship["hp"] -= 5
        event += "轻微损伤[-5HP]"

    elif effect_key == "aa_damage":
        event += "防空武器损坏"

    elif effect_key == "secondary_destroyed":
        event += "副炮毁伤"

    elif effect_key == "list":
        ship["list_deg"] += random.uniform(1, 5)
        event += f"舰体倾斜{ship['list_deg']:.0f}度"

    elif effect_key == "minor_leak":
        ship["flood_level"] += 0.5
        event += "轻微渗漏"

    elif effect_key == "shaft_damage":
        ship["max_speed_kt"] = max(ship["max_speed_kt"] * 0.75, 6)
        event += "传动轴损坏"

    elif effect_key == "stern_flood":
        ship["flood_level"] += 4
        ship["hp"] -= 20
        event += "尾部进水[-20HP]"

    elif effect_key == "searchlight_damage":
        event += "探照灯损毁"

    elif effect_key == "ventilation_damage":
        event += "通风系统损坏"

    elif effect_key == "fire_suppressed":
        # Magazine flooded (positive effect for ship, loss of ammo)
        event += "弹药库主动注水（弹药失效但避免殉爆）"

    elif effect_key == "secondary_explosion":
        ship["hp"] -= 200
        ship["fires"].append(4)
        event += "次发殉爆！[-200HP]"

    else:
        event += f"{effect_key}"

    ship["damage_log"].append(event)
    return event


# ============================================================
# FIRE / FLOOD PROGRESSION
# ============================================================

def resolve_fires(ship):
    """Process fire progression each turn. Returns list of events."""
    events = []
    new_fires = []
    for severity in ship["fires"]:
        severity += random.randint(0, 1)  # fire can grow
        # Damage
        dmg = severity * random.uniform(1, 3)
        ship["hp"] -= dmg
        if severity <= 2:
            # Small fire might go out
            if roll_chance(30):
                continue  # fire out
            new_fires.append(severity)
        elif severity <= 5:
            # Medium fire
            if roll_chance(15):
                continue
            new_fires.append(severity)
            events.append(f"大火持续，{dmg:.0f}HP损伤")
        else:
            # Severe fire
            new_fires.append(severity)
            events.append(f"猛烈火灾！{dmg:.0f}HP损伤")
            # Catastrophic spread chance
            if roll_chance(10):
                events.append("火灾蔓延至弹药库！")
                ship["hp"] -= 300

    ship["fires"] = new_fires
    return events


def resolve_flooding(ship):
    """Process flooding. Returns events list."""
    events = []
    if ship["flood_level"] <= 0:
        return events

    # Flooding naturally worsens
    ship["flood_level"] += ship["flood_level"] * 0.05  # 5% increase per turn
    dmg = ship["flood_level"] * random.uniform(0.5, 1.5)
    ship["hp"] -= dmg

    # List worsens
    ship["list_deg"] += ship["flood_level"] * 0.01

    if ship["flood_level"] > 50:
        events.append(f"大量进水！舰体严重下沉 {ship['flood_level']:.1f}%")
    elif ship["flood_level"] > 30:
        events.append(mk_event("flood","influx",ship=ship["name"],severity="moderate",level=ship["flood_level"]))
    elif ship["flood_level"] > 15:
        events.append(f"进水持续 {ship['flood_level']:.1f}%")

    # Sink check
    if ship["flood_level"] > 80 or ship["hp"] <= 0:
        ship["sunk"] = True
        events.append("舰体沉没！")

    return events


# ============================================================
# SINK CHECK
# ============================================================

def check_sunk(ship):
    if ship["sunk"]:
        return True
    if ship["hp"] <= 0:
        ship["sunk"] = True
        return True
    if ship["flood_level"] > 80:
        ship["sunk"] = True
        return True
    return False


# ============================================================
# CATASTROPHIC FAILURE
# 武松打虎的拳头落下来，就是这种毁灭性的效果
# ============================================================

def roll_catastrophe(ship):
    """Check for catastrophic failure (ammo cook-off, keel break, etc)."""
    if ship["sunk"]:
        return False
    hp_pct = ship["hp"] / ship["max_hp"]
    fire_severity = sum(ship["fires"])
    factor = (1.0 - hp_pct) * 0.5 + (fire_severity * 0.03)

    if factor > 0.2 and roll_chance(factor * 8):
        events = ["灾难性故障！"]
        # 40% magazine, 30% firestorm, 30% structural failure
        r = d100()
        if r <= 40:
            events.append("弹药库殉爆！")
            ship["hp"] -= 500
        elif r <= 70:
            events.append("火势失控全舰燃烧！")
            ship["fires"].append(10)
        else:
            events.append("舰体结构崩溃！")
            ship["hp"] -= 400
        if ship["hp"] <= 0:
            ship["sunk"] = True
            events.append("舰艇沉没...")
        return events
    return []


# ============================================================
# MAIN GUN SALVO
# ============================================================

"""New fire_salvo, secondary_fire_salvo, and secondary_aim_phase functions.
Written as standalone to avoid quote-nesting issues in the upgrade script."""

def fire_salvo(shooter, gun_key, target, distance_km, weather=1.0,
                accuracy_mod=1.0, damage_mod=1.0, critical_mod=1.0, reload_mod=1.0,
                ammo_type=None):
    events = []
    if shooter["main_guns_operational"] <= 0:
        return ["no main guns available"]
    if ammo_type is None:
        ammo_type = shooter.get("ammo_type", "AP")
    ascii_cls = unicodedata.normalize("NFKD", target.get("class","").lower()).encode("ascii","ignore").decode()
    is_destroyer = ascii_cls in ("kagero", "yugumo", "fubuki", "shimakaze")
    is_battleship = "bb" in target.get("class", "").lower() or "battleship" in target.get("class", "").lower()
    guns = max(1, int(shooter["main_guns_operational"] * reload_mod))
    hit_pct = compute_hit_pct(gun_key, distance_km, shooter, target, weather, accuracy_mod)
    hits = 0
    for _ in range(guns):
        if roll_chance(hit_pct):
            hits += 1
    # Near-miss on DDs
    if hits == 0 and is_destroyer and distance_km < 8:
        nm_chance = min(40, (8 - distance_km) * 5)
        if roll_chance(nm_chance):
            dmg = random.randint(20, 80)
            target["hp"] -= dmg
            events.append(mk_event("gunnery","near_miss",ship=shooter["name"],target=target["name"],hit_pct=hit_pct))
            events.append(mk_event("gunnery","effect",ship=shooter["name"],target=target["name"],effect="near_miss_shockwave"))
            if roll_chance(20):
                target["flood_level"] += 2
            return events
    if hits == 0:
        events.append(mk_event("gunnery","miss",ship=shooter["name"],target=target["name"],hit_pct=hit_pct))
        return events
    events.append(mk_event("gunnery","hit",ship=shooter["name"],target=target["name"],hits=hits,hit_pct=hit_pct))
    ammo_info = data.WEAPONS.get(gun_key, {})
    for _ in range(hits):
        loc_key = roll_hit_location(target)
        if ammo_type in ("HE", "HC"):
            if loc_key in ("belt", "waterline") and not is_destroyer:
                if random.random() < 0.7:
                    loc_key = "upper_works" if random.random() < 0.5 else "deck"
            if is_destroyer and loc_key in ("upper_works", "deck", "bridge", "secondary"):
                dmg = 80 + random.randint(0, 60)
                target["hp"] -= dmg
                events.append(mk_event("gunnery","effect",ship=shooter["name"],target=target["name"],effect="he_destroyer_hit"))
                if random.random() < 0.5:
                    target["fires"].append(random.randint(2, 5))
                if target["sunk"]: break
                continue
        else:
            if is_destroyer and loc_key in ("belt", "waterline"):
                dmg = 15 + random.randint(0, 25)
                target["hp"] -= dmg
                events.append(mk_event("gunnery","effect",ship=shooter["name"],target=target["name"],effect="ap_overpen_dd"))
                if target["sunk"]: break
                continue
        effect = compute_gunnery_effect(loc_key, gun_key, distance_km, target)
        loc_map = {k: n for (_, _, k, n) in data.HIT_LOCATIONS}
        loc_name = loc_map.get(loc_key, loc_key)
        events.append(mk_event("gunnery","location",ship=shooter["name"],target=target["name"],location=loc_name))
        result = apply_damage(target, effect[0], gun_key, distance_km)
        if result:
            events.append(mk_event("gunnery","effect",ship=shooter["name"],target=target["name"],effect=result))
        if ammo_type == "AP" and effect[0] in ("penetrate_vitals","deck_penetrate","semi_penetrate"):
            if random.random() < 0.2:
                extra = ammo_info.get("burst_charge_kg", 15) * random.uniform(2, 5)
                target["hp"] -= extra
        if ammo_type in ("HE","HC"):
            if effect[0] in ("no_effect","minor_damage","bounce"):
                if random.random() < 0.25:
                    target["fires"].append(random.randint(1, 3))
        cat = roll_catastrophe(target)
        if cat:
            events.extend(cat)
        if target["sunk"]:
            break
    return events

def secondary_fire_salvo(shooter, sec_gun_key, target, distance_km, weather=1.0):
    events = []
    if shooter.get("secondary_guns_operational", 0) <= 0:
        return events
    sec_guns = shooter["secondary_guns_operational"]
    gun_data = data.WEAPONS.get(sec_gun_key, {})
    burst_kg = gun_data.get("burst_charge_kg", 3)
    if distance_km < 5:
        hit_pct = 12.0
    elif distance_km < 8:
        hit_pct = 8.0
    elif distance_km < 12:
        hit_pct = 5.0
    elif distance_km < 16:
        hit_pct = 2.5
    else:
        hit_pct = 1.0
    ascii_cls = unicodedata.normalize("NFKD", target.get("class","").lower()).encode("ascii","ignore").decode()
    is_destroyer = ascii_cls in ("kagero", "yugumo", "fubuki", "shimakaze")
    if is_destroyer:
        hit_pct *= 1.3
    speed_penalty = 1.0 - (shooter["speed_kt"] / 40.0) * 0.2
    hit_pct *= speed_penalty * weather
    effective_guns = max(1, min(sec_guns, 8 + int(sec_guns * 0.3)))
    hits = 0
    for _ in range(effective_guns):
        if roll_chance(min(hit_pct, 20.0)):
            hits += 1
    if hits == 0:
        return events
    total_dmg = 0
    for _ in range(hits):
        if is_destroyer:
            dmg = 10 + random.randint(0, 20) + burst_kg * random.uniform(1, 3)
            target["hp"] -= dmg
            total_dmg += dmg
            if random.random() < 0.3:
                target["fires"].append(random.randint(1, 3))
            if random.random() < 0.15:
                target["flood_level"] += 1
        else:
            dmg = 5 + random.randint(0, 10) + burst_kg * random.uniform(0.5, 1.5)
            target["hp"] -= dmg
            total_dmg += dmg
            if random.random() < 0.1:
                target["fires"].append(1)
    events.append(mk_event("secondary","hit",ship=shooter["name"],target=target["name"],hits=hits))
    events.append(mk_event("secondary","effect",ship=shooter["name"],target=target["name"],effect=f"sec_damage_{total_dmg:.0f}"))
    if is_destroyer and total_dmg > 30:
        target["main_guns_operational"] = max(1, target.get("main_guns_operational", 0) - 1)
    if target["sunk"]:
        events.append(mk_event("secondary","sink",ship=shooter["name"],target=target["name"]))
    return events

def secondary_aim_phase(shooter, enemies, weather=1.0):
    """AI selects best target for secondary guns. Priorities: nearest DD, then nearest ship."""
    sec_key = shooter.get("secondary_gun_key")
    if not sec_key:
        return [], None
    sec_gun = data.WEAPONS.get(sec_key)
    if not sec_gun or sec_gun.get("category") != "secondary":
        return [], None
    # Prefer DDs within range
    dds = [e for e in enemies if not e.get("sunk",False) and unicodedata.normalize("NFKD",e.get("class","").lower()).encode("ascii","ignore").decode() in ("kagero","yugumo","fubuki","shimakaze")]
    if dds:
        target = min(dds, key=lambda e: math.hypot(e["position"][0]-shooter["position"][0], e["position"][1]-shooter["position"][1]))
    else:
        target = min(enemies, key=lambda e: math.hypot(e["position"][0]-shooter["position"][0], e["position"][1]-shooter["position"][1]))
    dist = math.hypot(target["position"][0]-shooter["position"][0], target["position"][1]-shooter["position"][1])
    if dist > 18:
        return [], None
    return secondary_fire_salvo(shooter, sec_key, target, dist, weather), target


# ============================================================
# TORPEDO LAUNCH
# ============================================================

def launch_torpedoes(launcher, target_pos, target_id, heading, num_tubes=8):
    """Launch torpedoes from a ship. Returns list of Torpedo objects."""
    torpedoes = []
    # Use Type 93 for IJN ships, Mk15 for USN
    torp_type = data.WEAPONS["type93"] if launcher.get("torpedo_tubes", 0) > 0 and \
                  "kagero" in launcher.get("id", "").lower() or \
                  launcher.get("id") in ["yukikaze", "kagero", "isokaze", "shiranui", "kuroshio"] \
                  else data.WEAPONS["us_mk15"]

    # Actually determine by side: IJN DD use Type 93, USN ships don't have torpedoes
    is_ijn = launcher.get("id") in ["yukikaze", "kagero", "isokaze", "shiranui", "kuroshio"]
    if not is_ijn:
        return []  # US BB don't carry torpedoes

    torp_type = data.WEAPONS["type93"]
    available = launcher["torpedoes_remaining"]
    if available <= 0:
        return []

    to_launch = min(num_tubes, available)
    launcher["torpedoes_remaining"] -= to_launch

    # Spread pattern: -5 to +5 degrees
    spread = random.uniform(-5, 5)
    for i in range(to_launch):
        spread_offset = spread + (i - to_launch/2) * 0.5
        t = Torpedo(
            launcher_id=launcher["id"],
            launch_pos=launcher["position"],
            target_id=target_id,
            heading=heading + spread_offset,
            speed_kt=torp_type["speed_high_kt"],
            range_m=torp_type["range_high_m"],
            warhead_kg=torp_type["warhead_kg"],
            wake_vis=torp_type["wake_visibility"],
        )
        torpedoes.append(t)

    return torpedoes


# ============================================================
# DEBUG / TEST
# ============================================================

def test_salvo():
    iowa = create_ship_state("iowa")
    nagato = create_ship_state("nagato")
    nagato["position"] = [20, 0]  # 20km away

    events = fire_salvo(iowa, "us_16in50_mk7", nagato, 20)
    print("=== TEST SALVO ===")
    for e in events:
        print(f"  {e}")
    print(f"Nagato HP: {nagato['hp']}/{nagato['max_hp']}")
    print(f"Nagato damage_log: {nagato['damage_log']}")
    return nagato

if __name__ == "__main__":
    set_seed(42)
    test_salvo()
