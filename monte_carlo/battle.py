#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle runner: turn-by-turn Monte Carlo battle simulation.
"""
import random, math, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as mc
from engine import mk_event, format_event
import data
import persona_registry
import buffs


# ============================================================
# BATTLE STATE
# 宋江带兵出征，晁盖的鬼魂大概就在这种时候出现
# ============================================================

class Battle:
    def setup_battle(self):
        # PINCER: JP splits 2 groups behind US, both flanks
        # Group A (east): heading 225 SW from starboard
        # Group B (west): heading 135 SE from port
        self.add_ship("US", "iowa", (0, -6), 180, 22, "human")
        self.add_ship("US", "south_dakota", (0.8, -8.5), 180, 22, "macarthur")
        # GROUP A: east flank
        self.add_ship("JP", "nagato", (10, 2), 225, 21, "xiucai")
        self.add_ship("JP", "mutsu", (11, 0.5), 225, 21, "gaoqiu")
        self.add_ship("JP", "haruna", (9, -2.5), 225, 21, "siming")
        self.add_ship("JP", "isokaze", (12, 3.5), 225, 24, "isokaze_sim")
        self.add_ship("JP", "shiranui", (10, -4), 225, 24, "shiranui_sim")
        # GROUP B: west flank
        self.add_ship("JP", "kongo", (-10, 2.5), 135, 22, "duanyu")
        self.add_ship("JP", "yukikaze", (-9, 4), 135, 25, "yukikaze_sim")
        self.add_ship("JP", "kagero", (-11, 1.5), 135, 25, "kagero_sim")
        self.add_ship("JP", "kuroshio", (-8, 0.5), 135, 25, "kuroshio_sim")
    def __init__(self, name="Midway North Night Battle", seed=None, has_carriers=False):
        self.name = name
        self.turn = 0
        self.time_minutes = 0
        self.seed = seed or random.randint(0, 99999)
        mc.set_seed(self.seed)
        self.has_carriers = has_carriers
        self.fleets = {"US": [], "JP": []}
        self.all_ships = []
        self.torpedoes = []
        self.log = []
        self.human_visible = []
        self.weather = 1.0
        self.visibility_km = 15.0
        self.night = True
        self.wind_dir = 90
        self.current_dir = 45
        self.current_speed_kt = 0.5

    def add_ship(self, side, ship_key, position, heading, speed_kt=None, persona_id=None):
        s = mc.create_ship_state(ship_key)
        s["position"] = list(position)
        s["heading"] = heading
        s["speed_kt"] = speed_kt or s.get("speed_cruise_kt", 18)
        s["_key"] = ship_key
        s["persona_id"] = persona_id
        s["side"] = side
        self.fleets[side].append(s)
        self.all_ships.append(s)
        return s

    def get_ship(self, ship_id):
        for s in self.all_ships:
            if s["id"] == ship_id:
                return s
        return None

    def active_ships(self, side=None):
        if side:
            return [s for s in self.fleets[side] if not s["sunk"]]
        return [s for s in self.all_ships if not s["sunk"]]

    def log_event(self, msg, human_visible=True):
        entry = {"turn": self.turn, "time": f"{self.time_minutes:02d}:00", "msg": msg}
        self.log.append(entry)
        if human_visible:
            self.human_visible.append(entry)
        return entry

    def distance_between(self, a, b):
        dx = a["position"][0] - b["position"][0]
        dy = a["position"][1] - b["position"][1]
        return math.hypot(dx, dy)

    def bearing_between(self, a, b):
        dx = b["position"][0] - a["position"][0]
        dy = b["position"][1] - a["position"][1]
        return (math.degrees(math.atan2(dx, dy)) + 360) % 360

    def get_personality(self, ship):
        """Get per-ship personality from registry."""
        if ship["side"] != "JP":
            return None
        pid = ship.get("persona_id")
        if not pid:
            return None
        return persona_registry.get_persona(pid)

    def move_ship(self, ship):
        if ship["sunk"]:
            return
        spd = min(ship["speed_kt"], ship["max_speed_kt"])
    
        pcfg = self.get_personality(ship)
        enemies = [e for e in self.active_ships() if e["side"] != ship["side"]]
        nearest = min(enemies, key=lambda e: self.distance_between(ship, e)) if enemies else None
    
        if nearest and ship["rudder_state"] not in ["jammed", "lost"]:
            dist = self.distance_between(ship, nearest)
            bearing = self.bearing_between(ship, nearest)
    
            if ship["side"] == "JP" and pcfg:
                # Per-captain personality-driven movement
                agg = pcfg["aggression"]
                dec = pcfg["decisiveness"]
                ada = pcfg["adaptability"]
                obe = pcfg["obedience"]
                range_pref = pcfg["range_preference"]
                retreat_threshold = pcfg["retreat_threshold"]
                turn_mod = pcfg["turn_rate_mod"]
                formation_bond = pcfg["formation_bond"]
                special = pcfg.get("special", "")
    
                # Variable range for shiranui
                if range_pref == "variable":
                    range_pref = random.choice(["close", "medium", "long"])
    
                # Retreat check
                if ship["hp"] / ship["max_hp"] < retreat_threshold:
                    desired = (bearing + 0) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-8, min(8, diff * 0.5))
                else:
                    # Personality-based range bands
                    # close_target = how close they'll go before evading
                    # open_range = what distance triggers approach
                    if range_pref == "close":
                        open_range = 14.0
                        close_target = 4
                    elif range_pref == "long":
                        open_range = 22.0
                        close_target = 10
                    else:  # medium
                        open_range = 18.0 - agg * 5.0
                        close_target = 8 if agg < 0.5 else (5 if agg > 0.8 else 6)
    
                    # Special: overrides for certain personalities
                    if special == "frenzy":
                        # 李逵: never retreats, always charges
                        close_target = 2
                        open_range = 20.0
                    elif special == "coward":
                        # 西门庆: keeps distance
                        close_target = 7
                        open_range = 16.0
                    elif special == "harasser":
                        # 时迁: long-range harassment, never closes under 6
                        close_target = 6
                        open_range = 22.0
                    elif special == "repressed_burst":
                        # 王英: wants very close torpedo range
                        close_target = 3
                        open_range = 12.0
    
                    # Adaptability
                    if ada > 0.7 and random.random() < 0.2:
                        enemies2 = [e for e in self.active_ships() if e["side"] != ship["side"]]
                        if enemies2:
                            nearest = min(enemies2, key=lambda e: self.distance_between(ship, e))
                            dist = self.distance_between(ship, nearest)
                            bearing = self.bearing_between(ship, nearest)
    
                    # Formation cohesion
                    if formation_bond > 0.6:
                        friends = [f for f in self.active_ships("JP") if f["id"] != ship["id"]]
                        if friends:
                            close_count = sum(1 for f in friends if self.distance_between(ship, f) < 3)
                            if close_count < 1:
                                closest = min(friends, key=lambda f: self.distance_between(ship, f))
                                fb = self.bearing_between(ship, closest)
                                bearing = int(bearing * 0.6 + ((fb + 180) % 360) * 0.4)
    
                    # ============= TACTICAL MOVEMENT =============
                    if dist > open_range:
                        # FAR RANGE: Approach to engage
                        factor = 0.4 + agg * 0.3
                        desired = (bearing + 180) % 360  # toward enemy
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        ship["heading"] += max(-6 * turn_mod, min(6 * turn_mod, diff * factor))
    
                    elif dist > max(close_target, 4):
                        # MID RANGE: Carrier escort or decisive engagement
                        carrier_boost = 0.15 if self.has_carriers else 0.0
                        effective_agg = min(1.0, agg + carrier_boost)
                        if effective_agg > 0.6:
                            # Aggressive: CLOSE HARD
                            offset = 170 + (1 - effective_agg) * 20
                        elif effective_agg > 0.3:
                            # Balanced: converging intercept
                            offset = 130 + (0.5 - effective_agg) * 60
                        else:
                            # Cautious but still closing
                            offset = 100 + (0.5 - effective_agg) * 30
                        
                        desired = (bearing + offset) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        # Turn-rate proportional to how far from optimal heading
                        turn_rate = (3 + agg * 3) * turn_mod
                        ship["heading"] += max(-turn_rate, min(turn_rate, diff * 0.3))
    
                    else:
                        # CLOSE RANGE: NO RETREAT — decisive engagement
                        carrier_boost = 0.15 if self.has_carriers else 0.0
                        effective_agg = min(1.0, agg + carrier_boost)
                        if ship.get("torpedoes_remaining", 0) > 0 and (range_pref == "close" or effective_agg > 0.6):
                            # Torpedo run
                            desired = (bearing + 150) % 360
                        elif range_pref == "close" or effective_agg > 0.5:
                            # Fight through: slow for accuracy
                            spd = max(8, spd * 0.6)
                            ship["speed_kt"] = spd
                            desired = (bearing + 180) % 360
                        else:
                            # Cross the T
                            desired = (bearing + 260) % 360 if random.random() < 0.5 else (bearing + 100) % 360
                        diff = (desired - ship["heading"] + 540) % 360 - 180
                        turn_rate = (4 + effective_agg * 4) * pcfg.get("turn_rate_mod", 1.0)
                        ship["heading"] += max(-turn_rate, min(turn_rate, diff * 0.35))
    
            else:
                # US movement: SPEED + GUNS — control the range
                # US can do 27-33kt vs JP 26kt BB. Keep distance at 10-14km.
                if dist > 16:
                    # Long range: cross the T at high speed
                    desired = (bearing + 200) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-5, min(5, diff * 0.3))
                    ship["speed_kt"] = min(ship["max_speed_kt"], ship["speed_kt"] + 2)
                elif dist > 9:
                    # Mid-range: HOLD range for gunnery advantage
                    # US 16in/50 outrange JP. Keep ~14km for radar fire control.
                    if dist < 14:
                        # Slightly open range
                        desired = (bearing + 80) % 360
                    elif dist < 17:
                        # Ideal: slight crossing for broadside
                        desired = (bearing + 120) % 360
                    else:
                        # Closing slowly
                        desired = (bearing + 160) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-2, min(2, diff * 0.2))
                elif dist > 6:
                    # Too close: open range but keep guns bearing
                    desired = (bearing + 60) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-4, min(4, diff * 0.25))
                    ship["speed_kt"] = ship["max_speed_kt"]
                else:
                    # Torpedo danger zone: emergency evasion
                    desired = (bearing + 20) % 360
                    diff = (desired - ship["heading"] + 540) % 360 - 180
                    ship["heading"] += max(-7, min(7, diff * 0.4))
                    ship["speed_kt"] = ship["max_speed_kt"]
        ship["heading"] = (ship["heading"] + 360) % 360
        dist_moved = spd * 1.852 * (3.0 / 60.0)
        hdg_rad = math.radians(ship["heading"])
        ship["position"][0] += dist_moved * math.sin(hdg_rad)
        ship["position"][1] += dist_moved * math.cos(hdg_rad)
    


    def detection_phase(self):
        events = []
        for ship in self.active_ships():
            enemies = [e for e in self.active_ships() if e["side"] != ship["side"]]
            for enemy in enemies:
                dist = self.distance_between(ship, enemy)
                if mc.check_detection(ship, enemy, dist, self.night, self.weather):
                    if ship["side"] == "US":
                        bearing = self.bearing_between(ship, enemy)
                        if ship["radar_online"]:
                            events.append(mk_event("radar","detect",ship=ship["name"],dist=dist,bearing=bearing,size=ship["name"]))
                        else:
                            events.append(mk_event("radar","visual",ship=ship["name"],bearing=bearing,dist=dist))
        return events

    def radar_phase(self):
        events = []
        for ship in self.active_ships():
            w, msg = mc.update_radar(ship)
            if msg:
                events.append(mk_event("radar","status",ship=ship["name"],msg=msg))
        return events

    def torpedo_launch_phase(self):
        events = []
        for ship in self.active_ships("JP"):
            if ship.get("torpedoes_remaining", 0) <= 0:
                continue
            targets = [t for t in self.active_ships("US") if t.get("main_guns", 0) >= 6]
            if not targets:
                continue
            target = min(targets, key=lambda t: self.distance_between(ship, t))
            dist = self.distance_between(ship, target)
            detected = mc.check_detection(ship, target, dist, self.night, self.weather)
            pcfg = self.get_personality(ship)
            torp_trigger_km = 20.0
            if pcfg:
                torp_trigger_km = pcfg["torpedo_trigger_km"]
                dec = pcfg["decisiveness"]
            
            # 时迁: long-range harassment even without detection
            special = pcfg.get("special", "") if pcfg else ""
            if special == "harasser" and not detected and dist > 8:
                # 时迁 fires blind at long range with lower accuracy anyway
                torp_trigger_km = max(torp_trigger_km, 15.0)
            elif not detected and dist > 8:
                continue
            
            if dist > torp_trigger_km:
                continue
            
            bearing = self.bearing_between(ship, target)
            num_tubes = min(ship["torpedoes_remaining"], 8)
            
            # Persona torpedo accuracy modifier
            torp_acc = pcfg["torpedo_accuracy_mod"] if pcfg else 1.0
            # Special abilities
            if special == "backstab":
                # 潘金莲: closer = deadlier
                if dist < 8:
                    torp_acc *= 1.3
            elif special == "repressed_burst":
                # 王英: close range burst
                if dist < 5:
                    torp_acc *= 1.5
            elif special == "ambusher":
                # 孙二娘: surprise from behind
                ship_angle = (ship["heading"] - bearing + 360) % 360
                if abs(ship_angle - 180) < 60:  # approaching from behind
                    torp_acc *= 1.3
            
            # Store accuracy modifier on torpedo state
            ship["_torp_accuracy_mod"] = torp_acc
            
            new_torps = mc.launch_torpedoes(ship, target["position"], target["id"], bearing, num_tubes)
            for t in new_torps:
                t._accuracy_mod = torp_acc
                self.torpedoes.append(t)
            ship["torpedoes_remaining"] -= num_tubes
            events.append(mk_event("torpedo","launch",ship=ship["name"],target=target["name"],dist=dist,num=num_tubes))
        return events

    def torpedo_phase(self):
        events = []
        for t in self.torpedoes[:]:
            result = t.update()
            if result:
                events.append(mk_event("torpedo","expired",desc=result))
                self.torpedoes.remove(t)
                continue
            for ship in self.active_ships("US"):
                dist = math.hypot(t.x - ship["position"][0], t.y - ship["position"][1])
                if t.check_detection(ship, dist, self.night):
                    bearing = (math.degrees(math.atan2(t.x - ship["position"][0], t.y - ship["position"][1])) + 360) % 360
                    events.append(mk_event("torpedo","detected",ship=ship["name"],dist=dist,bearing=bearing))
                    break
            targ = self.get_ship(t.target_id)
            if targ and not targ["sunk"] and not isinstance(targ, type(None)):
                # Use persona torpedo accuracy modifier
                torp_acc = getattr(t, '_accuracy_mod', 1.0)
                if t.hit_check(targ["position"], targ["length_m"], targ["speed_kt"], targ["heading"], accuracy_mod=torp_acc, target_ship=targ):
                    wf = t.warhead_kg / 300.0
                    base_damage = 250 * wf
                    targ["hp"] -= base_damage
                    targ["flood_level"] += 25 * wf
                    targ["list_deg"] += random.uniform(0, 5)
                    events.append(mk_event("torpedo_hit","hit",target=targ["name"],dmg=base_damage))
                    self.torpedoes.remove(t)
        return events

    def get_gun_key(self, ship):
        if ship["main_caliber_mm"] == 410:
            return "jp_16in45_3rd_year"
        elif ship["main_caliber_mm"] == 356:
            return "jp_14in45_vickers"
        elif ship["main_caliber_mm"] == 406 and ship.get("main_barrel_length") == 50:
            return "us_16in50_mk7"
        elif ship["main_caliber_mm"] == 406:
            return "us_16in45_mk6"
        return None

    def gunnery_phase(self):
        events = []
        for ship in self.active_ships():
            enemies = [e for e in self.active_ships() if e["side"] != ship["side"]]
            if not enemies:
                continue
            
            pcfg = self.get_personality(ship)
            
            # Target selection by persona
            high_value = [e for e in enemies if e.get("main_guns", 0) >= 6]
            if ship["side"] == "JP" and pcfg:
                if pcfg.get("aggression", 0.5) > 0.7:
                    # Aggressive: pick weakened
                    target = min(high_value, key=lambda e: e.get("hp", 999)) if high_value else min(enemies, key=lambda e: self.distance_between(ship, e))
                elif pcfg.get("special") == "opportunist":
                    # 高俅: pick already damaged
                    damaged = [e for e in enemies if e["hp"] < e["max_hp"] * 0.5]
                    if damaged:
                        target = min(damaged, key=lambda e: self.distance_between(ship, e))
                    else:
                        target = max(high_value, key=lambda e: e.get("hp", 0)) if high_value else min(enemies, key=lambda e: e.get("hp"))
                elif pcfg.get("special") == "trickster":
                    # 吴用: switch targets each turn
                    target = max(enemies, key=lambda e: e.get("main_guns", 0))
                elif pcfg.get("special") == "coward":
                    # 西门庆: target farthest
                    target = max(enemies, key=lambda e: self.distance_between(ship, e))
                else:
                    target = max(high_value, key=lambda e: e.get("hp", 0)) if high_value else min(enemies, key=lambda e: self.distance_between(ship, e))
            else:
                # US: nearest most dangerous threat
                # Check player-set targets for Iowa
                if ship.get("name") == "USS Iowa (BB-61)" and ship.get("primary_target"):
                    target_id = ship["primary_target"]
                    targeted = [e for e in enemies if e["id"] == target_id]
                    if targeted:
                        target = targeted[0]
                    else:
                        target = min(enemies, key=lambda e: self.distance_between(ship, e))
                elif ship.get("name") == "USS South Dakota (BB-57)" and ship.get("primary_target"):
                    # MacArthur might not listen
                    if random.random() > 0.7:  # 30% disobey
                        target = min(enemies, key=lambda e: self.distance_between(ship, e))
                    else:
                        target_id = ship["primary_target"]
                        targeted = [e for e in enemies if e["id"] == target_id]
                        if targeted:
                            target = targeted[0]
                        else:
                            target = min(enemies, key=lambda e: self.distance_between(ship, e))
                else:
                    target = min(enemies, key=lambda e: self.distance_between(ship, e))
            
            dist = self.distance_between(ship, target)
            if dist > 35:
                continue
            gun_key = self.get_gun_key(ship)
            
            if not gun_key:
                continue
            
            # Persona combat modifiers
            acc_mod = pcfg.get("accuracy_mod", 1.0) if pcfg else 1.0
            dmg_mod = pcfg.get("damage_mod", 1.0) if pcfg else 1.0
            crit_mod = pcfg.get("critical_mod", 1.0) if pcfg else 1.0
            reload_mod = pcfg.get("reload_mod", 1.0) if pcfg else 1.0
            
            # Fire salvo with persona modifiers and ammo type
            ammo_t = ship.get("ammo_type", "AP")
            salvo_events = mc.fire_salvo(ship, gun_key, target, dist, self.weather,
                                          accuracy_mod=acc_mod, damage_mod=dmg_mod,
                                          critical_mod=crit_mod, reload_mod=reload_mod,
                                          ammo_type=ammo_t)
            for e in salvo_events:
                events.append(mk_event("gunnery","shot",shooter=ship["name"],target=target["name"],desc=e))
        return events

    def secondary_gunnery_phase(self):
        """Secondary battery fire phase."""
        events = []
        for ship in self.active_ships():
            sec_key = ship.get("secondary_gun_key")
            if not sec_key:
                continue
            enemies = [e for e in self.active_ships() if e["side"] != ship["side"] and not e.get("sunk", False)]
            if not enemies:
                continue
            sec_evts, target = mc.secondary_aim_phase(ship, enemies, self.weather)
            for e in sec_evts:
                events.append(e)
        return events

    def damage_progression(self):
        events = []
        for ship in self.active_ships():
            for e in mc.resolve_fires(ship):
                events.append(mk_event("fire","event",ship=ship["name"],desc=e))
            for e in mc.resolve_flooding(ship):
                events.append(mk_event("flood","event",ship=ship["name"],desc=e))
        return events

    def sink_check(self):
        events = []
        for ship in self.active_ships():
            if mc.check_sunk(ship):
                events.append(mk_event("sink","sunk",ship=ship["name"]))
        return events

    def run_turn(self):
        self.turn += 1
        self.time_minutes += 3
        events = []
        events.append(mk_event("turn","header",turn=self.turn,time=f"{self.time_minutes:02d}:00"))
        events.extend(self.radar_phase())
        events.extend(self.detection_phase())
        for ship in self.active_ships():
            self.move_ship(ship)
        events.extend(self.torpedo_launch_phase())
        events.extend(self.torpedo_phase())
        events.extend(self.gunnery_phase())
        events.extend(self.damage_progression())
        events.extend(self.sink_check())
        us = len(self.active_ships("US"))
        jp = len(self.active_ships("JP"))
        events.append(mk_event("status","fleet",us=us,jp=jp))
        return events

    def run_battle(self, max_turns=60):
        self.setup_battle()
        yield "battle start"
        for t in range(max_turns):
            ev = self.run_turn()
            for e in ev:
                yield e
            if not self.active_ships("US") or not self.active_ships("JP"):
                break

    def summary(self):
        lines = [f"=== {self.name} Summary ==="]
        lines.append(f"Turns: {self.turn} | Time: {self.time_minutes}min | Seed: {self.seed}")
        for side in ["US", "JP"]:
            alive = [s for s in self.fleets[side] if not s["sunk"]]
            sunk = [s for s in self.fleets[side] if s["sunk"]]
            lines.append(f"\n{side}:")
            lines.append(f"  Alive: {len(alive)}")
            for s in alive:
                lines.append(f"    {s['name']} HP={s['hp']:.0f}/{s['max_hp']:.0f}")
            lines.append(f"  Sunk: {len(sunk)}")
            for s in sunk:
                lines.append(f"    {s['name']} sunk")
        return "\n".join(lines)


# ============================================================
# MONTE CARLO RUN (module-level)
# ============================================================

def run_monte_carlo(battle_class, n=100, max_turns=60, seed=None, **kwargs):
    """
    Run n battles and return summary stats.
    """
    import random as rng
    results = {"us_wins": 0, "jp_wins": 0, "draws": 0, "avg_turns": 0}
    total_turns = 0
    for i in range(n):
        seed_i = seed + i if seed else rng.randint(0, 99999)
        b = battle_class(seed=seed_i, **kwargs)
        for e in b.run_battle(max_turns=max_turns):
            pass
        us_alive = len([s for s in b.fleets["US"] if not s["sunk"]])
        jp_alive = len([s for s in b.fleets["JP"] if not s["sunk"]])
        if us_alive > 0 and jp_alive == 0:
            results["us_wins"] += 1
        elif jp_alive > 0 and us_alive == 0:
            results["jp_wins"] += 1
        else:
            results["draws"] += 1
        total_turns += b.turn
    results["avg_turns"] = total_turns / n if n > 0 else 0
    return results
