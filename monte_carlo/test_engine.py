#!/usr/bin/env python3
"""Test the Monte Carlo engine at various ranges."""
import sys
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship')
from monte_carlo import engine

for seed in [42, 99, 123, 456, 789]:
    engine.set_seed(seed)
    iowa = engine.create_ship_state('iowa')
    nagato = engine.create_ship_state('nagato')
    nagato['position'] = [8, 0]
    print(f'--- Seed {seed} (8km) ---')
    events = engine.fire_salvo(iowa, 'us_16in50_mk7', nagato, 8)
    for e in events:
        print(f'  {e}')
    print(f'  Nagato HP: {nagato["hp"]:.0f}/{nagato["max_hp"]:.0f}')
    if engine.check_sunk(nagato):
        print('  SUNK!')
    print()

# Radar failure test
print("=== Radar Reliability Test (100 turns) ===")
engine.set_seed(42)
iowa = engine.create_ship_state('iowa')
fail_count = 0
total_offline = 0
for t in range(100):
    was, msg = engine.update_radar(iowa)
    if not iowa["radar_online"]:
        fail_count += 1
        total_offline += iowa["radar_drop_turns"]
print(f"Radar failures: {fail_count}/100 turns")
print(f"Total offline turns: {total_offline}")
