#!/usr/bin/env python3
"""Run one battle tick with given commands and report results."""
import sys, os, math, random
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo')
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship')
import play

# Create game instance - force Chinese
game = play.Game()
game.cn = True

# --- Briefing ---
game.show_briefing()

p = game.player_ship

# Set initial: heading 150, speed 20 (default)
print("\n" + "=" * 66)
print("  [01:47] 衣阿华号 — 舰桥")
print("  灯光静默已执行。全舰所有外部灯光关闭。无线电静默。")
print(">> 命令：全舰灯光静默，给麦克阿瑟发消息，让他小心，调整队形，占领有利阵位")
print()

# Parse commands
print(">>  舵角设定，航向150度。")
print(">>  车钟：20节。")
print(">>  通讯官：「南达科他号回复：『收到。保持警惕。跟在你后面。』」")
print()

sodak = game.get_ship("south_dakota")
if sodak and not sodak.get("sunk", False):
    sodak["heading"] = p["heading"]
    sodak["speed_kt"] = p["speed_kt"] - 2

# Run first tick
print("=" * 66)
print("  【第一回合 · 10分钟后 · 01:57】")
print("=" * 66)

events = game.run_tick()

# Generate report
report = play.make_report(game, p, events, 1)
for line in report:
    print(line)

# Additional narrative
print()
print("=" * 66)
print("  雷达操作员报告更新：")
contacts = game.active_ships("JP")
visible_ct = 0
for e in contacts:
    d = game.distance_between(p, e)
    radar_on = p.get("radar_online", True)
    if (radar_on and d < 32) or d < 12:
        visible_ct += 1
print(f"    「长官，已确认{visible_ct}个回波。还在逐步锁定。那个大目标——看起来是战列舰级别的。」")

# Burke's tactical assessment
print()
d_to_closest = game.distance_between(p, contacts[0]) if contacts else 0
bearing_to_enemy = 150  # simplified
print(f"  伯克： 「距离约{d_to_closest:.0f}公里，方位西北偏西。}")
print(f"           他们还没看到我们——我们占了先手。}")
print(f"           建议：保持当前航向，利用雷达优势控制接触距离。}")
print(f"           如果你想要，我们可以向左转拉大距离，}")
print(f"           或者向右转准备切入他们的T字横头。」}")

# Show key ship states
print()
print("=" * 66)
print("  【当前阵位】")
print(f"  衣阿华号：航向{int(p['heading'])}度  航速{int(p['speed_kt'])}节")
for e in contacts[:4]:
    d = game.distance_between(p, e)
    nm = play.cn_name(e.get("_key", ""))
    print(f"  雷达接触：{nm:10s}  {d:.1f}公里")

sodak = game.get_ship("south_dakota")
if sodak and not sodak.get("sunk", False):
    sd = game.distance_between(p, sodak)
    print(f"  南达科他号：{sd:.1f}公里  右后方  等待你的命令")
