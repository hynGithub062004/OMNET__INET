#!/usr/bin/env python3
"""Summarize real OMNeT++ scalar files. Python 3.9+, standard library only."""
import argparse
import csv
import math
from pathlib import Path
import re
import shlex
import statistics
import sys


def parse_sca(path):
    attrs, configs, scalars, stats = {}, {}, {}, {}
    current = None
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            tokens = shlex.split(line, comments=False)
            if not tokens:
                continue
            kind = tokens[0]
            if kind == "attr" and len(tokens) >= 3:
                # Later attr records belong to results, not the run itself.
                if not scalars and not stats:
                    attrs.setdefault(tokens[1], " ".join(tokens[2:]))
            elif kind == "config" and len(tokens) >= 3:
                # OMNeT++ writes the derived section before its ancestors.
                configs.setdefault(tokens[1], " ".join(tokens[2:]))
            elif kind == "scalar" and len(tokens) == 4:
                scalars[(tokens[1], tokens[2])] = float(tokens[3])
                current = None
            elif kind == "statistic" and len(tokens) == 3:
                current = (tokens[1], tokens[2])
                stats[current] = {}
            elif kind == "field" and current and len(tokens) == 3:
                stats[current][tokens[1]] = float(tokens[2])
    return attrs, configs, scalars, stats


def quantity(value, unit):
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*" + re.escape(unit) + r"\s*", value)
    if not match:
        raise ValueError(f"Expected a value in {unit}, received {value!r}")
    return float(match[1])


def scalar_by_suffix(scalars, module_suffix, name):
    matches = [value for (module, stat), value in scalars.items()
               if module.endswith(module_suffix) and stat == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one {module_suffix} {name}; found {len(matches)}")
    return matches[0]


def summarize(path, config_name, sensors):
    attrs, configs, scalars, stats = parse_sca(path)
    if attrs.get("configname") != config_name:
        raise ValueError(f"{path.name}: configname is not {config_name}")
    sent, energies = {}, {}
    for (module, stat), value in scalars.items():
        node = re.search(r"\.sensor\[(\d+)\]\.", module)
        if node:
            index = int(node.group(1))
            if module.endswith(".app[0]") and stat == "packetSent:count":
                sent[index] = value
            if module.endswith(".energyStorage") and stat == "residualEnergyCapacity:last":
                energies[index] = value
    expected = set(range(sensors))
    if set(sent) != expected or set(energies) != expected:
        raise ValueError(f"{path.name}: expected application counts and energy for all {sensors} sensors; "
                         f"found {len(sent)} counts, {len(energies)} energies")
    if any(not math.isfinite(value) or value < 0 for value in (*sent.values(), *energies.values())):
        raise ValueError(f"{path.name}: invalid packet count or energy")
    received = scalar_by_suffix(scalars, ".gateway.app[0]", "packetReceived:count")
    total_sent = sum(sent.values())
    if not total_sent or not math.isfinite(received) or not 0 <= received <= total_sent:
        raise ValueError(f"{path.name}: invalid sent/received count")
    delay_stats = [fields for (module, name), fields in stats.items()
                   if module.endswith(".gateway.app[0]") and name == "endToEndDelay:stats"]
    if received:
        if len(delay_stats) != 1 or delay_stats[0].get("count") != received:
            raise ValueError(f"{path.name}: delay sample count does not match received count")
        delay = delay_stats[0]["mean"] * 1000
        delay_max = delay_stats[0]["max"] * 1000
        if not math.isfinite(delay) or delay < 0 or not math.isfinite(delay_max) or delay_max < delay:
            raise ValueError(f"{path.name}: invalid delay")
    else:
        delay = delay_max = math.nan
    simulation_time = quantity(configs["sim-time-limit"], "s")
    warmup_time = quantity(configs.get("warmup-period", "0s"), "s")
    duration = simulation_time - warmup_time
    if duration <= 0:
        raise ValueError("Measurement interval must be positive")
    payload = quantity(configs["*.sensor[*].app[0].messageLength"], "B")
    byte_key = next(((m, n) for m, n in scalars
                     if m.endswith(".gateway.app[0]") and n == "packetReceived:sum(packetBytes)"), None)
    received_bytes = scalars[byte_key] if byte_key else received * payload
    # This fallback is valid only for the fixed-length traffic in K1/K2.
    initial_energy = quantity(configs["*.sensor[*].energyStorage.initialCapacity"], "J")
    if any(value > initial_energy + 1e-8 for value in energies.values()):
        raise ValueError(f"{path.name}: remaining energy exceeds initial energy")
    seed = int(attrs["seedset"])
    row = {
        "config": config_name, "seed": seed, "sensors": sensors,
        "packet_sent": int(total_sent), "packet_received": int(received),
        "packet_loss": int(total_sent - received), "pdr_percent": 100 * received / total_sent,
        "delay_mean_ms": delay, "delay_max_ms": delay_max,
        "energy_remaining_mean_J": statistics.mean(energies.values()),
        "energy_remaining_min_J": min(energies.values()),
        "energy_consumed_mean_J": initial_energy - statistics.mean(energies.values()),
        "app_throughput_bps": 8 * received_bytes / duration,
        "measurement_duration_s": duration,
        "throughput_bytes_source": "recorded" if byte_key else "received_count_times_fixed_payload",
    }
    per_sensor = [{"config": config_name, "seed": seed, "sensor": f"sensor[{i}]",
                   "packet_sent": int(sent[i]), "energy_remaining_J": energies[i],
                   "energy_consumed_J": initial_energy - energies[i]} for i in range(sensors)]
    return row, per_sensor


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", nargs="?", type=Path, default=here.parent / "simulations/results")
    parser.add_argument("--config", default="K2_Final")
    parser.add_argument("--sensors", type=int, default=30)
    parser.add_argument("--expect-runs", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=here)
    args = parser.parse_args()
    files = sorted(args.results_dir.glob(f"{args.config}-*.sca"))
    if len(files) != args.expect_runs:
        parser.error(f"Expected {args.expect_runs} {args.config} scalar files, found {len(files)}. "
                     "Run all repetitions to completion first.")
    rows, energy_rows = [], []
    try:
        for path in files:
            row, node_rows = summarize(path, args.config, args.sensors)
            rows.append(row)
            energy_rows.extend(node_rows)
        seeds = [row["seed"] for row in rows]
        if sorted(seeds) != list(range(args.expect_runs)):
            raise ValueError(f"Expected distinct seed sets 0..{args.expect_runs - 1}; found {seeds}")
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    summary = []
    for metric in ("pdr_percent", "delay_mean_ms", "energy_remaining_mean_J",
                   "energy_remaining_min_J", "app_throughput_bps", "packet_sent", "packet_received"):
        values = [row[metric] for row in rows if math.isfinite(row[metric])]
        summary.append({"metric": metric, "valid_runs": len(values),
                        "mean": statistics.mean(values) if values else math.nan,
                        "sample_stddev": statistics.stdev(values) if len(values) > 1 else math.nan,
                        "min": min(values) if values else math.nan,
                        "max": max(values) if values else math.nan})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / f"{args.config}_KPI_PerRun.csv", rows)
    write_csv(args.output_dir / f"{args.config}_KPI_Summary.csv", summary)
    write_csv(args.output_dir / f"{args.config}_Energy_PerSensor.csv", energy_rows)
    for row in rows:
        print(f"seed={row['seed']}: sent={row['packet_sent']}, received={row['packet_received']}, "
              f"PDR={row['pdr_percent']:.4f}%, delay={row['delay_mean_ms']:.6f} ms, "
              f"energy={row['energy_remaining_mean_J']:.8f} J/sensor")
    print(f"Saved three CSV files to {args.output_dir}")
    print("Throughput uses the fixed post-warm-up window, 10..100 s for K2_Final (90 s).")
    print("Summary stddev is across runs; it is not the within-run packet-delay stddev.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
