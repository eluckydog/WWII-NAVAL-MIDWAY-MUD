# quick test
import sys
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo')
import battle
attrs = [m for m in dir(battle.Battle) if not m.startswith('__')]
print('Battle methods:', attrs[:30])
b = battle.Battle()
print('Ships:', len(b.ships))
print('Ship keys:', list(b.ships.keys())[:3])
for k, v in b.ships.items():
    print(f'  {k}: name={v.get("name","?")} side={v.get("side","?")} persona={v.get("persona_id","?")}')
