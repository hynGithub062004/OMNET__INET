"""Export four KPIs and per-sensor energy from native K2_Charts scalar files."""
from pathlib import Path
import argparse
import csv
import re
import statistics


def read_sca(path):
    scalars, stats, current = {}, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        p = line.split(maxsplit=3)
        if not p:
            continue
        if p[0] == "scalar":
            current = None
            try:
                scalars[p[1], p[2]] = float(p[3])
            except ValueError:
                pass  # Unrelated descriptive names may contain spaces.
        elif p[0] == "statistic":
            current = stats.setdefault((p[1], p[2]), {})
        elif p[0] == "field" and current is not None:
            current[p[1]] = float(p[2])
    return scalars, stats


def save(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=project / "simulations/results/light")
    parser.add_argument("--output", type=Path, default=project / "analysis/exports/compact")
    args = parser.parse_args()
    rows, energies = [], []
    for seed in range(5):
        sc, st = read_sca(args.results / f"K2_Charts-{seed}.sca")
        sent = sum(sc[f"WarehouseWSN.sensor[{i}].app[0]", "packetSent:count"] for i in range(30))
        received = sc["WarehouseWSN.gateway.app[0]", "packetReceived:count"]
        delay = st["WarehouseWSN.gateway.app[0]", "endToEndDelay:stats"]
        energy = [sc[f"WarehouseWSN.sensor[{i}].energyStorage", "residualEnergyCapacity:last"] for i in range(30)]
        assert sent == 2640 and 0 <= received <= sent and delay["count"] == received
        assert delay["min"] >= 0 and all(0 <= value <= 100 for value in energy)
        rows.append(dict(seed=seed, sent=sent, received=received, pdr_pct=100*received/sent,
                         delay_mean_ms=1000*delay["mean"], energy_mean_j=statistics.mean(energy),
                         payload_goodput_bps=8*sc["WarehouseWSN.gateway.app[0]", "packetReceived:sum(packetBytes)"]/90))
        energies.extend(dict(seed=seed, sensor=i, remaining_j=value, consumed_j=100-value) for i, value in enumerate(energy))
    args.output.mkdir(parents=True, exist_ok=True)
    save(args.output / "K2_Charts_per_seed.csv", rows)
    save(args.output / "K2_Charts_energy_per_sensor.csv", energies)
    save(args.output / "K2_Charts_summary.csv", [dict(metric=key, mean=statistics.mean(r[key] for r in rows),
         sample_sd=statistics.stdev(r[key] for r in rows)) for key in ("pdr_pct", "delay_mean_ms", "energy_mean_j", "payload_goodput_bps")])
    print(f"Validated all five runs; wrote compact KPI tables to {args.output}")


if __name__ == "__main__":
    main()
