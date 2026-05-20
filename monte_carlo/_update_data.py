"""Add weapon key references to all ships in data.py."""
import sys, os, re

f = r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo\data.py'
with open(f, 'r', encoding='utf-8') as fh:
    txt = fh.read()

# Ship-to-weapon map
ship_weapons = {
    "iowa":      ("us_16in50_mk7",     "us_5in38",      None),
    "south_dakota": ("us_16in45_mk6",  "us_5in38",      None),
    "nagato":    ("jp_16in45_3rd_year", "jp_140mm",     None),
    "mutsu":     ("jp_16in45_3rd_year", "jp_140mm",     None),
    "kongo":     ("jp_14in45_vickers", "jp_152mm",      None),
    "haruna":    ("jp_14in45_vickers", "jp_152mm",      None),
    "yukikaze":  ("jp_127mm_type3",     None,           "type93"),
    "kagero":    ("jp_127mm_type3",     None,           "type93"),
    "isokaze":   ("jp_127mm_type3",     None,           "type93"),
    "shiranui":  ("jp_127mm_type3",     None,           "type93"),
    "kuroshio":  ("jp_127mm_type3",     None,           "type93"),
}

# Insert weapon key lines after "max_hp" line for each ship
for ship_key, (main_key, sec_key, torp_key) in ship_weapons.items():
    # Find the ship definition block
    pattern = rf'"{ship_key}":\s*\{{'
    # Find its "max_hp" line and insert after
    insert_after = f'"max_hp": {7*" "}}}' if ship_key in ["iowa","south_dakota","nagato","mutsu","haruna"] else f'"max_hp": 200,'

    # Search in a more targeted way
    # Find the ship block
    ship_start = txt.find(f'    "{ship_key}": {{')
    if ship_start < 0:
        ship_start = txt.find(f'        "{ship_key}": {{')
    if ship_start < 0:
        print(f"  WARN: {ship_key} not found")
        continue
    
    # Find the end of this ship's definition
    # Look for the max_hp line + closing brace
    ship_end_marker = '    },' if txt[ship_start:ship_start+4] == '    "' else '        },'
    
    # Find the max_hp line after ship_start
    maxhp_pos = txt.find('"max_hp"', ship_start)
    if maxhp_pos < 0:
        print(f"  WARN: {ship_key} max_hp not found")
        continue
    
    # Find end of max_hp line
    eol = txt.find('\n', maxhp_pos)
    
    # Check if weapon keys already exist
    if txt.find('"main_gun_key"', ship_start, ship_start + 500) >= 0:
        print(f"  SKIP {ship_key}: already has weapon keys")
        continue
    
    # Build insertion text
    main_line = f'        "main_gun_key": "{main_key}",'
    sec_line = f'        "secondary_gun_key": "{sec_key}",' if sec_key else f'        "secondary_gun_key": None,'
    torp_line = f'        "torpedo_key": "{torp_key}",' if torp_key else f'        "torpedo_key": None,'
    insertion = f'\n{main_line}\n{sec_line}\n{torp_line}'
    
    txt = txt[:eol] + insertion + txt[eol:]
    print(f"  DONE {ship_key}: {main_key} / {sec_key or 'none'} / {torp_key or 'none'}")

# Also count ships before adding
# Count weapon key entries
import_count = txt.count('"main_gun_key"')
print(f"\nTotal weapon key entries added: {import_count}")

if import_count == 11:
    # Now add new weapon entries to WEAPONS dict
    new_weapons = """

    # === US SECONDARY ===
    "us_5in38": {
        "type": "secondary",
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
        "type": "secondary",
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
        "type": "secondary",
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
        "type": "main",
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

"""
    # Insert before the torpedo section
    torp_start = txt.find('\n    "type93": {')
    txt = txt[:torp_start] + new_weapons + txt[torp_start:]
    print("New weapon entries added to WEAPONS")

    # Update us_16in50_mk7 and us_16in45_mk6 to have ammo_types
    txt = txt.replace(
        '"us_16in50_mk7": {',
        '"us_16in50_mk7": {\n        "type": "main",\n        "ammo_types": ["AP", "HC"],'
    )
    txt = txt.replace(
        '"us_16in45_mk6": {',
        '"us_16in45_mk6": {\n        "type": "main",\n        "ammo_types": ["AP", "HC"],'
    )
    txt = txt.replace(
        '"jp_16in45_3rd_year": {',
        '"jp_16in45_3rd_year": {\n        "type": "main",\n        "ammo_types": ["AP", "HE"],'
    )
    txt = txt.replace(
        '"jp_14in45_vickers": {',
        '"jp_14in45_vickers": {\n        "type": "main",\n        "ammo_types": ["AP", "HE"],'
    )
    txt = txt.replace(
        '"type93": {',
        '"type93": {\n        "type": "torpedo",'
    )
    txt = txt.replace(
        '"us_mk15": {',
        '"us_mk15": {\n        "type": "torpedo",'
    )

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(txt)
    print("Ammo types added to main gun entries")
    print("Type field added to all weapon entries")
else:
    print(f"EXPECTED 11 ships, got {import_count} - check results")
