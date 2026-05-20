"""Run full Monte Carlo simulation for the Midway North battle."""
import sys, os
sys.path.insert(0, r'C:\Users\13918\.qclaw\workspace-code-gen\mud_wwii_ship\monte_carlo')
import battle as bt

def run_demo(seed=42):
    b = bt.Battle("Midway North Night Battle (Demo)", seed)
    for msg in b.run_battle(50):
        if isinstance(msg, dict):
            msg = msg.get("msg", str(msg))
        print(msg)
    print()
    print(b.summary())


def run_monte_carlo(n=100):
    """Run multiple battles and aggregate stats."""
    results = {"us_win": 0, "jp_win": 0, "draw": 0, "total_loss": 0}
    results["turns"] = []
    results["iowa_survived"] = 0
    results["so_dak_survived"] = 0
    results["us_sunk"] = 0
    results["jp_sunk"] = 0

    for i in range(n):
        b = bt.Battle(f"MC#{i}", seed=None)
        list(b.run_battle(60))
        us_alive = len(b.active_ships("US"))
        jp_alive = len(b.active_ships("JP"))
        us_sunk = len([s for s in b.fleets["US"] if s["sunk"]])
        jp_sunk = len([s for s in b.fleets["JP"] if s["sunk"]])

        if us_alive > 0 and jp_alive == 0:
            results["us_win"] += 1
        elif jp_alive > 0 and us_alive == 0:
            results["jp_win"] += 1
        elif us_alive > 0 and jp_alive > 0:
            results["draw"] += 1
        else:
            results["total_loss"] += 1

        results["turns"].append(b.turn)
        results["iowa_survived"] += 1 if b.get_ship("iowa") and not b.get_ship("iowa")["sunk"] else 0
        results["so_dak_survived"] += 1 if b.get_ship("south_dakota") and not b.get_ship("south_dakota")["sunk"] else 0
        results["us_sunk"] += us_sunk
        results["jp_sunk"] += jp_sunk

    avg_turns = sum(results["turns"]) / n if results["turns"] else 0
    print(f"=== Monte Carlo [{n} runs] ===")
    print(f"US win:  {results['us_win']:3d} ({results['us_win']/n*100:.1f}%)")
    print(f"JP win:  {results['jp_win']:3d} ({results['jp_win']/n*100:.1f}%)")
    print(f"Draw:    {results['draw']:3d} ({results['draw']/n*100:.1f}%)")
    print(f"TotalL:  {results['total_loss']:3d} ({results['total_loss']/n*100:.1f}%)")
    print(f"Avg turns: {avg_turns:.1f}")
    print(f"Iowa sur:  {results['iowa_survived']/n*100:.1f}%")
    print(f"SoDak sur: {results['so_dak_survived']/n*100:.1f}%")
    print(f"Avg US ships sunk: {results['us_sunk']/n:.2f}")
    print(f"Avg JP ships sunk: {results['jp_sunk']/n:.2f}")
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mc":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        run_monte_carlo(n)
    else:
        run_demo()
