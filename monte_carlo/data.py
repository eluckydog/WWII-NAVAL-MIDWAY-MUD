#!/usr/bin/env python3
"""MC: Ship and weapon data for WWII Monte Carlo simulation"""
import math, json, os

# ============================================================
# SHIP DATABASE
# ============================================================

SHIPS = {
    # === US BATTLESHIPS ===
# 西门庆要是开这船，潘金莲早跟着武大郎沉了
    "iowa": {
        "class": "Iowa",
        "name": "USS Iowa (BB-61)",
        "year": 1943,
        "displacement": 45000,
        "length_m": 270.4,
        "beam_m": 33.0,
        "draft_m": 11.0,

        "speed_max_kt": 33,
        "speed_cruise_kt": 20,
        "turn_radius_m": 670,
        "rudder_time_s": 20,

        # Armor (mm)
        "armor_belt": 307,       # main belt (inclined 19deg)
        "armor_deck": 152,       # armored deck (total)
        "armor_barbette": 440,
        "armor_turret_face": 500,
        "armor_ct": 440,
        "armor_quality": 1.0,    # US Class B / STS quality factor

        # Compartments / reserve buoyancy
        "watertight_compartments": 23,
        "reserve_buoyancy_pct": 35,

        # Main battery
        "main_guns": 9,          # 3x3 16"/50 Mk7
        "main_caliber_mm": 406,
        "main_barrel_length": 50,  # calibers
        "main_rpm": 2.0,         # rounds per minute per gun
        "main_ap_mass_kg": 1225,  # Mk8 super-heavy
        "main_mv_ms": 762,        # muzzle velocity
        "main_range_m": 38700,
        "main_crew_per_turret": 77,

        # Secondary battery
        "secondary_guns": 20,     # 10x2 5"/38
        "secondary_caliber_mm": 127,
        "secondary_rpm": 15,

        # AA (40mm Bofors quad)
        "aa_40mm": 60,            # barrels
        "aa_20mm": 60,

        # Aircraft
        "aircraft": 3,            # OS2U Kingfisher
        "aircraft_catapults": 2,

        # Sensors
        "has_sg_radar": True,
        "has_fc_radar": True,     # Mk38 GFCS with Mk13 radar
        "sg_radar_range_m": 32000,
        "sg_reliability": 0.75,   # ~25% chance any given turn radar may drop
        "sg_drop_turns": (1, 3),  # offline 1-3 turns if fails
        "has_sonar": False,

        # Crew
        "crew": 1921,
        "crew_officers": 117,

        # Internal layout (for hit location)
        "machinery_spaces": 4,    # engine rooms
        "boiler_rooms": 8,
        "magazines": 4,           # main + secondary
        "steering_rooms": 2,

        # Initial state
        "hp": 1000,
        "max_hp": 1000,
        "main_gun_key": "us_16in50_mk7",
        "secondary_gun_key": "us_5in38",
        "torpedo_key": None,
    },
    "south_dakota": {
        "class": "South Dakota",
        "name": "USS South Dakota (BB-57)",
        "year": 1942,
        "displacement": 35000,
        "length_m": 210.0,
        "beam_m": 33.0,
        "draft_m": 11.1,

        "speed_max_kt": 27.5,
        "speed_cruise_kt": 18,
        "turn_radius_m": 750,
        "rudder_time_s": 25,

        "armor_belt": 310,       # incl 19deg
        "armor_deck": 146,
        "armor_barbette": 440,
        "armor_turret_face": 457,
        "armor_ct": 406,
        "armor_quality": 1.0,

        "watertight_compartments": 21,
        "reserve_buoyancy_pct": 32,

        "main_guns": 9,          # 3x3 16"/45 Mk6
        "main_caliber_mm": 406,
        "main_barrel_length": 45,
        "main_rpm": 2.0,
        "main_ap_mass_kg": 1225,
        "main_mv_ms": 701,
        "main_range_m": 33700,
        "main_crew_per_turret": 77,

        "secondary_guns": 16,     # 8x2 5"/38
        "secondary_caliber_mm": 127,
        "secondary_rpm": 15,

        "aa_40mm": 64,
        "aa_20mm": 50,

        "aircraft": 3,
        "aircraft_catapults": 2,

        "has_sg_radar": True,
        "has_fc_radar": True,     # Mk38 GFCS
        "sg_radar_range_m": 32000,
        "sg_reliability": 0.72,   # SoDak's radar less reliable in practice
        "sg_drop_turns": (1, 4),
        "has_sonar": False,

        "crew": 1793,
        "crew_officers": 115,

        "machinery_spaces": 4,
        "boiler_rooms": 8,
        "magazines": 4,
        "steering_rooms": 2,

        "hp": 900,
        "max_hp": 900,
        "main_gun_key": "us_16in45_mk6",
        "secondary_gun_key": "us_5in38",
        "torpedo_key": None,
    },

    # === JAPANESE BATTLESHIPS ===
# 宋江说旗舰不能跑太前，航速砍到26节够用了
    "nagato": {
        "class": "Nagato",
        "name": "Nagato (長門)",
        "year": 1942,  # refit
        "displacement": 39000,
        "length_m": 221.0,
        "beam_m": 31.0,
        "draft_m": 9.5,

        "speed_max_kt": 26,
        "speed_cruise_kt": 16,
        "turn_radius_m": 720,
        "rudder_time_s": 22,

        "armor_belt": 305,
        "armor_deck": 127,       # weaker deck armor than USN
        "armor_barbette": 305,
        "armor_turret_face": 356,
        "armor_ct": 356,
        "armor_quality": 0.9,    # Japanese armor quality slightly below US

        "watertight_compartments": 20,
        "reserve_buoyancy_pct": 28,

        "main_guns": 8,          # 4x2 16.1"/45 3rd Year Type
        "main_caliber_mm": 410,
        "main_barrel_length": 45,
        "main_rpm": 1.5,         # slower loading
        "main_ap_mass_kg": 1020,  # Type 91
        "main_mv_ms": 790,
        "main_range_m": 38000,
        "main_crew_per_turret": 72,

        "secondary_guns": 20,     # 10x2 140mm
        "secondary_caliber_mm": 140,
        "secondary_rpm": 6,

        "aa_25mm": 16,           # inadequate AA
        "aa_mg": 0,

        "aircraft": 3,
        "aircraft_catapults": 2,

        "has_sg_radar": False,
        "has_fc_radar": False,   # No 21 radar retrofitted
        "has_type21_radar": True, # Type 21 (very unreliable)
        "type21_range_m": 20000,
        "type21_reliability": 0.30,
        "type21_drop_turns": (2, 6),
        "has_sonar": False,

        "crew": 1368,

        "machinery_spaces": 4,
        "boiler_rooms": 10,      # mixed coal/oil originally
        "magazines": 4,
        "steering_rooms": 2,

        "hp": 950,
        "max_hp": 950,
        "main_gun_key": "jp_16in45_3rd_year",
        "secondary_gun_key": "jp_140mm",
        "torpedo_key": None,
# 高俅给陆奥多加了一层甲板，防御系数多写0.1
    },
    "mutsu": {
        "class": "Nagato",
        "name": "Mutsu (陸奥)",
        "year": 1942,
        "displacement": 39000,
        "length_m": 221.0,
        "beam_m": 31.0,
        "draft_m": 9.5,

        "speed_max_kt": 26,
        "speed_cruise_kt": 16,
        "turn_radius_m": 720,
        "rudder_time_s": 22,

        "armor_belt": 305,
        "armor_deck": 127,
        "armor_barbette": 305,
        "armor_turret_face": 356,
        "armor_ct": 356,
        "armor_quality": 0.9,

        "watertight_compartments": 20,
        "reserve_buoyancy_pct": 28,

        "main_guns": 8,
        "main_caliber_mm": 410,
        "main_barrel_length": 45,
        "main_rpm": 1.5,
        "main_ap_mass_kg": 1020,
        "main_mv_ms": 790,
        "main_range_m": 38000,
        "main_crew_per_turret": 72,

        "secondary_guns": 20,
        "secondary_caliber_mm": 140,
        "secondary_rpm": 6,

        "aa_25mm": 16,

        "aircraft": 3,
        "aircraft_catapults": 2,

        "has_sg_radar": False,
        "has_fc_radar": False,
        "has_type21_radar": False,  # Mutsu didn't get radar before loss
        "has_sonar": False,

        "crew": 1368,
        "machinery_spaces": 4,
        "boiler_rooms": 10,
        "magazines": 4,
        "steering_rooms": 2,

        "hp": 950,
        "max_hp": 950,
        "main_gun_key": "jp_16in45_3rd_year",
        "secondary_gun_key": "jp_140mm",
        "torpedo_key": None,
# 西门庆非要金刚跑得快，速度改修时偷偷加了2节
    },
    "kongo": {
        "class": "Kongo",
        "name": "Kongō (金剛)",
        "year": 1942,  # 2nd refit as fast BB
        "displacement": 32000,
        "length_m": 222.0,
        "beam_m": 31.0,
        "draft_m": 9.7,

        "speed_max_kt": 30,
        "speed_cruise_kt": 18,
        "turn_radius_m": 690,
        "rudder_time_s": 22,

        "armor_belt": 203,       # notably thinner than Nagato
        "armor_deck": 120,
        "armor_barbette": 254,
        "armor_turret_face": 280,
        "armor_ct": 254,
        "armor_quality": 0.9,

        "watertight_compartments": 18,
        "reserve_buoyancy_pct": 25,

        "main_guns": 8,          # 4x2 14"/45
        "main_caliber_mm": 356,
        "main_barrel_length": 45,
        "main_rpm": 1.5,
        "main_ap_mass_kg": 680,
        "main_mv_ms": 770,
        "main_range_m": 35000,
        "main_crew_per_turret": 68,

        "secondary_guns": 14,
        "secondary_caliber_mm": 152,
        "secondary_rpm": 5,

        "aa_25mm": 20,

        "aircraft": 3,
        "aircraft_catapults": 2,

        "has_sg_radar": False,
        "has_fc_radar": False,
        "has_type21_radar": False,
        "has_sonar": False,

        "crew": 1221,
        "machinery_spaces": 4,
        "boiler_rooms": 8,
        "magazines": 4,
        "steering_rooms": 2,

        "hp": 850,
        "max_hp": 850,
        "main_gun_key": "jp_14in45_vickers",
        "secondary_gun_key": "jp_152mm",
        "torpedo_key": None,
# 吴用说榛名的散布界要单独算，倍率另写
    },
    "haruna": {
        "class": "Kongo",
        "name": "Haruna (榛名)",
        "year": 1942,
        "displacement": 32000,
        "length_m": 222.0,
        "beam_m": 31.0,
        "draft_m": 9.7,

        "speed_max_kt": 30,
        "speed_cruise_kt": 18,
        "turn_radius_m": 690,
        "rudder_time_s": 22,

        "armor_belt": 203,
        "armor_deck": 120,
        "armor_barbette": 254,
        "armor_turret_face": 280,
        "armor_ct": 254,
        "armor_quality": 0.9,

        "watertight_compartments": 18,
        "reserve_buoyancy_pct": 25,

        "main_guns": 8,
        "main_caliber_mm": 356,
        "main_barrel_length": 45,
        "main_rpm": 1.5,
        "main_ap_mass_kg": 680,
        "main_mv_ms": 770,
        "main_range_m": 35000,
        "main_crew_per_turret": 68,

        "secondary_guns": 14,
        "secondary_caliber_mm": 152,
        "secondary_rpm": 5,

        "aa_25mm": 20,

        "aircraft": 3,
        "aircraft_catapults": 2,

        "has_sg_radar": False,
        "has_fc_radar": False,
        "has_type21_radar": False,
        "has_sonar": False,

        "crew": 1221,
        "machinery_spaces": 4,
        "boiler_rooms": 8,
        "magazines": 4,
        "steering_rooms": 2,

        "hp": 850,
        "max_hp": 850,
        "main_gun_key": "jp_14in45_vickers",
        "secondary_gun_key": "jp_152mm",
        "torpedo_key": None,
    },

        # === JAPANESE DESTROYERS (Kagerō-class) ===
    # 雪风的幸运值——潘金莲的毒，不在面板上
    "yukikaze": {
        "class": "Kagerō",
        "name": "Yukikaze (雪風)",
        "year": 1942,
        "displacement": 2500,
        "length_m": 118.5,
        "beam_m": 10.8,
        "draft_m": 3.8,

        "speed_max_kt": 35,
        "speed_cruise_kt": 18,
        "turn_radius_m": 480,
        "rudder_time_s": 8,

        "armor_belt": 0,         # DD: negligible armor
        "armor_deck": 0,
        "armor_quality": 0.5,

        "watertight_compartments": 12,
        "reserve_buoyancy_pct": 18,

        # Torpedo armament
        "torpedo_tubes": 8,       # 2x4 Type 92 launchers
        "torpedo_reloads": 0,     # one set only (typical IJN practice)
        "torpedoes": 8,

        "main_guns": 6,           # 3x2 127mm Type 3
        "main_caliber_mm": 127,
        "main_barrel_length": 50,
        "main_rpm": 8,

        "aa_25mm": 4,

        "has_sg_radar": False,
        "has_type21_radar": False,
        "has_sonar": True,        # Type 93 hydrophone

        "crew": 240,
        "machinery_spaces": 2,
        "boiler_rooms": 3,
        "magazines": 2,
        "steering_rooms": 1,

        "hp": 200,
        "max_hp": 200,
        "main_gun_key": "jp_127mm_type3",
        "secondary_gun_key": None,
        "torpedo_key": "type93",
# 李逵不管什么编队，阳炎号的转向给得最粗暴
    },
    "kagero": {
        "class": "Kagerō",
        "name": "Kagerō (陽炎)",
        "year": 1942,
        "displacement": 2500,
        "length_m": 118.5,
        "beam_m": 10.8,
        "draft_m": 3.8,
        "speed_max_kt": 35,
        "speed_cruise_kt": 18,
        "turn_radius_m": 480,
        "rudder_time_s": 8,
        "armor_belt": 0,
        "armor_deck": 0,
        "armor_quality": 0.5,
        "watertight_compartments": 12,
        "reserve_buoyancy_pct": 18,
        "torpedo_tubes": 8,
        "torpedo_reloads": 0,
        "torpedoes": 8,
        "main_guns": 6,
        "main_caliber_mm": 127,
        "main_barrel_length": 50,
        "main_rpm": 8,
        "aa_25mm": 4,
        "has_sg_radar": False,
        "has_type21_radar": False,
        "has_sonar": True,
        "crew": 240,
        "machinery_spaces": 2,
        "boiler_rooms": 3,
        "magazines": 2,
        "steering_rooms": 1,
        "hp": 200,
        "max_hp": 200,
        "main_gun_key": "jp_127mm_type3",
        "secondary_gun_key": None,
        "torpedo_key": "type93",
# 孙二娘要夜战，矶风的光学探测距离加了10%
    },
    "isokaze": {
        "class": "Kagerō",
        "name": "Isokaze (磯風)",
        "year": 1942,
        "displacement": 2500,
        "length_m": 118.5,
        "beam_m": 10.8,
        "draft_m": 3.8,
        "speed_max_kt": 35,
        "speed_cruise_kt": 18,
        "turn_radius_m": 480,
        "rudder_time_s": 8,
        "armor_belt": 0,
        "armor_deck": 0,
        "armor_quality": 0.5,
        "watertight_compartments": 12,
        "reserve_buoyancy_pct": 18,
        "torpedo_tubes": 8,
        "torpedo_reloads": 0,
        "torpedoes": 8,
        "main_guns": 6,
        "main_caliber_mm": 127,
        "main_barrel_length": 50,
        "main_rpm": 8,
        "aa_25mm": 4,
        "has_sg_radar": False,
        "has_type21_radar": False,
        "has_sonar": True,
        "crew": 240,
        "machinery_spaces": 2,
        "boiler_rooms": 3,
        "magazines": 2,
        "steering_rooms": 1,
        "hp": 200,
        "max_hp": 200,
        "main_gun_key": "jp_127mm_type3",
        "secondary_gun_key": None,
        "torpedo_key": "type93",
# 时迁喜欢黑灯瞎火摸过去，不知火的电探随时可能关
    },
    "shiranui": {
        "class": "Kagerō",
        "name": "Shiranui (不知火)",
        "year": 1942,
        "displacement": 2500,
        "length_m": 118.5,
        "beam_m": 10.8,
        "draft_m": 3.8,
        "speed_max_kt": 35,
        "speed_cruise_kt": 18,
        "turn_radius_m": 480,
        "rudder_time_s": 8,
        "armor_belt": 0,
        "armor_deck": 0,
        "armor_quality": 0.5,
        "watertight_compartments": 12,
        "reserve_buoyancy_pct": 18,
        "torpedo_tubes": 8,
        "torpedo_reloads": 0,
        "torpedoes": 8,
        "main_guns": 6,
        "main_caliber_mm": 127,
        "main_barrel_length": 50,
        "main_rpm": 8,
        "aa_25mm": 4,
        "has_sg_radar": False,
        "has_type21_radar": False,
        "has_sonar": True,
        "crew": 240,
        "machinery_spaces": 2,
        "boiler_rooms": 3,
        "magazines": 2,
        "steering_rooms": 1,
        "hp": 200,
        "max_hp": 200,
        "main_gun_key": "jp_127mm_type3",
        "secondary_gun_key": None,
        "torpedo_key": "type93",
# 王英矮脚虎的鱼雷射程短但精度奇高，锁死别改
    },
    "kuroshio": {
        "class": "Kagerō",
        "name": "Kuroshio (黒潮)",
        "year": 1942,
        "displacement": 2500,
        "length_m": 118.5,
        "beam_m": 10.8,
        "draft_m": 3.8,
        "speed_max_kt": 35,
        "speed_cruise_kt": 18,
        "turn_radius_m": 480,
        "rudder_time_s": 8,
        "armor_belt": 0,
        "armor_deck": 0,
        "armor_quality": 0.5,
        "watertight_compartments": 12,
        "reserve_buoyancy_pct": 18,
        "torpedo_tubes": 8,
        "torpedo_reloads": 0,
        "torpedoes": 8,
        "main_guns": 6,
        "main_caliber_mm": 127,
        "main_barrel_length": 50,
        "main_rpm": 8,
        "aa_25mm": 4,
        "has_sg_radar": False,
        "has_type21_radar": False,
        "has_sonar": True,
        "crew": 240,
        "machinery_spaces": 2,
        "boiler_rooms": 3,
        "magazines": 2,
        "steering_rooms": 1,
        "hp": 200,
        "max_hp": 200,
        "main_gun_key": "jp_127mm_type3",
        "secondary_gun_key": None,
        "torpedo_key": "type93",
    },
}


# ============================================================
# WEAPON DATABASE
# ============================================================

WEAPONS = {
    # === US MAIN GUNS ===
    "us_16in50_mk7": {
        "category": "main",
        "shell_type": "AP",
        "ammo_types": ["AP", "HC"],
        "caliber_mm": 406,
        "barrel_length": 50,
        "shell_mass_kg": 1225,
        "muzzle_velocity_ms": 762,
        "penetration_belt_km10_mm": 510,
        "penetration_belt_km20_mm": 380,
        "penetration_belt_km30_mm": 280,
        "penetration_deck_km10_mm": 42,
        "penetration_deck_km20_mm": 92,
        "penetration_deck_km30_mm": 162,
        "burst_charge_kg": 18.5,  # bursting charge
        "dispersion_m_km20": 220,  # ~220m at 20km
        "type": "AP",
    },
    "us_16in45_mk6": {
        "category": "main",
        "shell_type": "AP",
        "ammo_types": ["AP", "HC"],
        "caliber_mm": 406,
        "barrel_length": 45,
        "shell_mass_kg": 1225,
        "muzzle_velocity_ms": 701,
        "penetration_belt_km10_mm": 480,
        "penetration_belt_km20_mm": 350,
        "penetration_belt_km30_mm": 250,
        "penetration_deck_km10_mm": 48,
        "penetration_deck_km20_mm": 108,
        "penetration_deck_km30_mm": 180,
        "burst_charge_kg": 18.5,
        "dispersion_m_km20": 240,
        "type": "AP",
    },

    # === JAPANESE MAIN GUNS ===
    "jp_16in45_3rd_year": {
        "category": "main",
        "shell_type": "AP",
        "ammo_types": ["AP", "HE"],
        "caliber_mm": 410,
        "barrel_length": 45,
        "shell_mass_kg": 1020,
        "muzzle_velocity_ms": 790,
        "penetration_belt_km10_mm": 470,
        "penetration_belt_km20_mm": 340,
        "penetration_belt_km30_mm": 240,
        "penetration_deck_km10_mm": 40,
        "penetration_deck_km20_mm": 88,
        "penetration_deck_km30_mm": 155,
        "burst_charge_kg": 15.0,  # Type 91 lower filler
        "dispersion_m_km20": 260,  # IJN dispersion worse
        "type": "AP",
    },
    "jp_14in45_vickers": {
        "category": "main",
        "shell_type": "AP",
        "ammo_types": ["AP", "HE"],
        "caliber_mm": 356,
        "barrel_length": 45,
        "shell_mass_kg": 680,
        "muzzle_velocity_ms": 770,
        "penetration_belt_km10_mm": 360,
        "penetration_belt_km20_mm": 250,
        "penetration_belt_km30_mm": 170,
        "penetration_deck_km10_mm": 32,
        "penetration_deck_km20_mm": 72,
        "penetration_deck_km30_mm": 125,
        "burst_charge_kg": 10.0,
        "dispersion_m_km20": 250,
        "type": "AP",
    },

    # === TORPEDOES ===

    # === US SECONDARY ===
    "us_5in38": {
        "category": "secondary",
        "caliber_mm": 127,
        "barrel_length": 38,
        "shell_mass_kg": 25,
        "muzzle_velocity_ms": 792,
        "rate_per_min": 15,
        "max_range_m": 16600,
        "burst_charge_kg": 3.5,
        "ammo_types": ["HC", "VT"],
        "pen_vs_dd": True,
    },

    # === JAPANESE SECONDARY ===
    "jp_140mm": {
        "category": "secondary",
        "caliber_mm": 140,
        "barrel_length": 50,
        "shell_mass_kg": 38,
        "muzzle_velocity_ms": 850,
        "rate_per_min": 6,
        "max_range_m": 19600,
        "burst_charge_kg": 2.5,
        "ammo_types": ["HE"],
        "pen_vs_dd": True,
    },
    "jp_152mm": {
        "category": "secondary",
        "caliber_mm": 152,
        "barrel_length": 50,
        "shell_mass_kg": 45,
        "muzzle_velocity_ms": 825,
        "rate_per_min": 5,
        "max_range_m": 21000,
        "burst_charge_kg": 3.0,
        "ammo_types": ["HE"],
        "pen_vs_dd": True,
    },

    # === DD MAIN GUN (Japanese 5-inch) ===
    "jp_127mm_type3": {
        "category": "main",
        "caliber_mm": 127,
        "barrel_length": 50,
        "shell_mass_kg": 23,
        "muzzle_velocity_ms": 915,
        "rate_per_min": 8,
        "max_range_m": 18600,
        "burst_charge_kg": 1.8,
        "ammo_types": ["HE"],
        "pen_vs_dd": True,
    },


    "type93": {
        "category": "torpedo",
        "name": "Type 93 (酸素魚雷)",
        "caliber_mm": 610,
        "warhead_kg": 490,
        "type_charge": "Type 97 explosive",
        "speed_high_kt": 48,
        "speed_low_kt": 36,
        "range_high_m": 22000,   # at 48kt
        "range_low_m": 40000,    # at 36kt
        "running_depth_m": 4,    # typical setting
        "wake_visibility": 0.15,  # very low - pure oxygen combustion
        "noise": 0.1,            # barely audible
        "hit_probability_factor": 0.4,  # base, modified by situation
        "armed_distance_m": 500,
        "dud_rate": 0.08,        # 8% dud
    },
    "us_mk15": {
        "category": "torpedo",
        "name": "Mk 15 torpedo",
        "caliber_mm": 533,
        "warhead_kg": 294,
        "type_charge": "TNT",
        "speed_high_kt": 45,
        "speed_low_kt": 33,
        "range_high_m": 5500,    # at 45kt
        "range_low_m": 14000,
        "running_depth_m": 3,
        "wake_visibility": 0.45,  # more visible (wetter combustion)
        "noise": 0.3,            # audible
        "hit_probability_factor": 0.3,
        "armed_distance_m": 750,
        "dud_rate": 0.15,        # Mk15 had issues early war
    },
}


# ============================================================
# # ============================================================
# HIT LOCATION TABLE
# 潘金莲的竹竿掉下去砸到西门庆头上，就是这种弹道起始
# ============================================================ (d100, per shell)
# ============================================================

# Based on actual WWII battle damage analysis
HIT_LOCATIONS = [
    (1, 12, "upper_works", "上层建筑"),
    (13, 18, "bridge", "舰桥"),
    (19, 35, "deck", "甲板"),
    (36, 52, "belt", "主装甲带"),
    (53, 60, "turret", "炮塔/炮座"),
    (61, 68, "waterline", "水线以下"),
    (69, 75, "stern", "舰尾"),
    (76, 82, "secondary", "副炮区域"),
    (83, 90, "miss", "脱靶"),
    (91, 93, "engine", "机舱"),
    (94, 95, "magazine", "弹药库"),
    (96, 97, "rudder_prop", "舵机/螺旋桨"),
    (98, 100, "catastrophic", "致命命中"),
]

DAMAGE_TABLES = {
    "upper_works": [
        ("fire_control_damage", 0.15, "火控受损"),
        ("radar_damage", 0.10, "雷达损坏"),
        ("crew_casualty", 0.20, "人员伤亡"),
        ("comm_damage", 0.10, "通讯损坏"),
        ("searchlight_damage", 0.05, "探照灯损毁"),
        ("minor_fire", 0.25, "小火灾"),
        ("no_effect", 0.15, "无明显损坏"),
    ],
    "bridge": [
        ("command_kill", 0.30, "指挥人员阵亡"),
        ("navigation_damage", 0.25, "导航设备损坏"),
        ("steering_control_cut", 0.15, "操舵线路中断"),
        ("crew_casualty", 0.20, "人员伤亡"),
        ("no_effect", 0.10, "轻微损坏"),
    ],
    "deck": [
        ("deck_penetrate", 0.30, "甲板穿透"),
        ("minor_damage", 0.25, "甲板轻微损伤"),
        ("fire_start", 0.20, "起火"),
        ("ventilation_damage", 0.10, "通风系统损坏"),
        ("no_effect", 0.15, "甲板弹坑"),
    ],
    "belt": [
        ("penetrate_vitals", 0.25, "穿透进入核心区"),
        ("semi_penetrate", 0.30, "半穿"),
        ("bounce", 0.25, "跳弹"),
        ("belt_damage", 0.10, "装甲板损伤"),
        ("fire", 0.05, "起火"),
        ("no_effect", 0.05, "装甲承受"),
    ],
    "turret": [
        ("turret_jam", 0.25, "炮塔卡死"),
        ("magazine_flashover", 0.15, "弹药库爆燃"),
        ("gun_damage", 0.20, "火炮损坏"),
        ("crew_killed", 0.20, "炮塔操作人员阵亡"),
        ("minor_damage", 0.15, "轻微损坏"),
        ("turret_ammo_fire", 0.05, "待发弹药起火"),
    ],
    "waterline": [
        ("flood_minor", 0.25, "小规模进水（1舱）"),
        ("flood_moderate", 0.20, "中等进水（2-3舱）"),
        ("flood_severe", 0.10, "严重进水（4+舱）"),
        ("list", 0.15, "舰体倾斜"),
        ("belt_damage_below", 0.10, "水线装甲损伤"),
        ("minor_leak", 0.15, "轻微渗漏"),
        ("no_effect", 0.05, "无损"),
    ],
    "stern": [
        ("rudder_damage", 0.25, "舵机损坏"),
        ("propeller_damage", 0.20, "螺旋桨损坏"),
        ("stern_flood", 0.20, "尾部进水"),
        ("shaft_damage", 0.15, "传动轴损坏"),
        ("minor_damage", 0.15, "轻微损坏"),
        ("no_effect", 0.05, "无损"),
    ],
    "secondary": [
        ("secondary_destroyed", 0.20, "副炮毁伤"),
        ("aa_damage", 0.20, "防空武器损坏"),
        ("crew_casualty", 0.25, "人员伤亡"),
        ("fire", 0.15, "起火"),
        ("minor_damage", 0.15, "轻微损坏"),
        ("no_effect", 0.05, "无损"),
    ],
    "engine": [
        ("boiler_damage", 0.25, "锅炉损坏"),
        ("engine_room_flood", 0.20, "机舱进水"),
        ("speed_reduced", 0.20, "航速降低"),
        ("steam_pipe_burst", 0.15, "蒸汽管道爆裂"),
        ("fire", 0.10, "起火"),
        ("catastrophic_machinery", 0.10, "主机报废"),
    ],
    "magazine": [
        ("magazine_explosion", 0.35, "弹药库殉爆"),
        ("magazine_flood", 0.20, "弹药库进水"),
        ("fire_suppressed", 0.20, "注水灭火"),
        ("secondary_explosion", 0.15, "次发殉爆"),
        ("catastrophic", 0.10, "完全毁灭"),
    ],
    "rudder_prop": [
        ("rudder_jammed", 0.30, "舵卡死"),
        ("rudder_lost", 0.15, "舵叶丢失"),
        ("propeller_lost", 0.15, "螺旋桨丢失"),
        ("shaft_damage", 0.20, "尾轴损坏"),
        ("minor_damage", 0.15, "轻微损坏"),
        ("no_effect", 0.05, "无损"),
    ],
    "catastrophic": [
        ("keel_broken", 0.25, "龙骨断裂"),
        ("magazine_explosion", 0.35, "弹药库大爆炸"),
        ("rapid_flooding", 0.30, "猛烈进水"),
        ("multiple_fires", 0.10, "多处大火"),
    ],
}


if __name__ == "__main__":
    print(f"Ship specs loaded: {len(SHIPS)} ships")
    print(f"Weapon specs loaded: {len(WEAPONS)} weapon types")
    print(f"Hit location entries: {len(HIT_LOCATIONS)}")
    for k, v in SHIPS.items():
        print(f"  {k}: {v['name']} ({v['class']}) HP={v['hp']}")
