"""Read real OMNeT++ scalar files; Python 3.10+, optional matplotlib for plots."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import re
import shlex
import statistics

SENSOR_APP = re.compile(r"WarehouseWSN\.sensor\[(\d+)\]\.app\[0\]$")
SENSOR_ENERGY = re.compile(r"WarehouseWSN\.sensor\[(\d+)\]\.energyStorage$")
GATEWAY_APP = "WarehouseWSN.gateway.app[0]"


def read_sca(path):
    attrs, scalars, stats, pars = {}, {}, {}, {}
    current_stat = None
    with Path(path).open(encoding="utf-8") as stream:
        for raw in stream:
            parts = raw.strip().split(maxsplit=3)
            if not parts:
                continue
            kind = parts[0]
            if kind == "run":
                current_stat = None
            elif kind == "attr" and parts[1] in ("configname", "seedset", "repetition", "network"):
                attrs[parts[1]] = shlex.split(raw)[2]
            elif kind in ("scalar", "par", "statistic"):
                if parts[1].startswith('"') or parts[2].startswith('"'):
                    parts = shlex.split(raw)
                key = (parts[1], parts[2])
                current_stat = None
                if kind == "scalar":
                    if key in scalars:
                        raise ValueError(f"{path}: duplicate scalar {key}")
                    scalars[key] = float(parts[3])
                elif kind == "par":
                    pars[key] = parts[3]
                else:
                    current_stat = stats.setdefault(key, {})
            elif kind == "field" and current_stat is not None:
                current_stat[parts[1]] = float(parts[2])
    return attrs, scalars, stats, pars


def extract_run(path, scenario):
    attrs, scalars, stats, pars = read_sca(path)
    expected = 10 if scenario == "K1" else 30
    if attrs.get("configname") != f"{scenario}_Final":
        raise ValueError(f"{path}: expected {scenario}_Final, got {attrs.get('configname')}")
    if attrs.get("network") != "warehousewsn.simulations.WarehouseWSN":
        raise ValueError(f"{path}: unexpected network")
    if int(pars[("WarehouseWSN", "numSensors")]) != expected:
        raise ValueError(f"{path}: unexpected sensor count")
    seed, repetition = int(attrs["seedset"]), int(attrs["repetition"])
    if seed != repetition or seed not in range(5):
        raise ValueError(f"{path}: expected seed = repetition in 0..4")
    sent = {int(m[1]): value for (module, name), value in scalars.items()
            if name == "packetSent:count" and (m := SENSOR_APP.fullmatch(module))}
    energy = {int(m[1]): value for (module, name), value in scalars.items()
              if name == "residualEnergyCapacity:last" and (m := SENSOR_ENERGY.fullmatch(module))}
    if set(sent) != set(range(expected)) or set(energy) != set(range(expected)):
        raise ValueError(f"{path}: missing sensor application or energy results")
    # A full baseline run sends 88 packets/node between uniform(11,12) and 99 s.
    if any(value != 88 for value in sent.values()):
        raise ValueError(f"{path}: unexpected packet count; check traffic or incomplete run")
    if any(not math.isfinite(v) or not 0 <= v <= 100 for v in energy.values()):
        raise ValueError(f"{path}: invalid remaining energy")
    received = scalars[(GATEWAY_APP, "packetReceived:count")]
    if not math.isfinite(received) or received <= 0 or received != int(received):
        raise ValueError(f"{path}: no valid received-packet count")
    # CsmaCaMac has no duplicate suppression. Never silently clip a ratio > 100%.
    if received > sum(sent.values()):
        raise ValueError(f"{path}: received > sent; inspect duplicates before computing PDR")
    delay = stats[(GATEWAY_APP, "endToEndDelay:stats")]
    if delay["count"] != received or not all(math.isfinite(delay[k]) for k in ("mean", "min", "max")):
        raise ValueError(f"{path}: delay samples do not match received packets")
    if not 0 <= delay["min"] <= delay["mean"] <= delay["max"]:
        raise ValueError(f"{path}: invalid delay statistics")
    macs = [f"WarehouseWSN.sensor[{i}].wlan[0].mac" for i in range(expected)] + ["WarehouseWSN.gateway.wlan[0].mac"]
    row = dict(scenario=scenario, seed=seed, sensors=expected,
               sent_packets=int(sum(sent.values())), received_packets=int(received),
               lost_packets=int(sum(sent.values()) - received), pdr_pct=100 * received / sum(sent.values()),
               delay_mean_ms=delay["mean"] * 1000, delay_min_ms=delay["min"] * 1000,
               delay_max_ms=delay["max"] * 1000, energy_mean_j=statistics.mean(energy.values()),
               energy_min_j=min(energy.values()), energy_max_j=max(energy.values()),
               energy_common10_mean_j=statistics.mean(energy[i] for i in range(10)),
               energy_consumed_mean_j=100 - statistics.mean(energy.values()),
               energy_consumed_total_j=sum(100 - value for value in energy.values()),
               payload_goodput_bps=received * 64 * 8 / 90,
               mac_retries=sum(scalars[(module, "numRetry")] for module in macs),
               mac_given_up=sum(scalars[(module, "numGivenUp")] for module in macs),
               overheard_data_frames_mean_per_sensor=statistics.mean(
                   scalars[(module, "packetDropNotAddressedToUs:count")] for module in macs[:-1]))
    nodes = [dict(scenario=scenario, seed=seed, sensor=i, energy_remaining_j=energy[i],
                  energy_consumed_j=100 - energy[i]) for i in sorted(energy)]
    return row, nodes, pars


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify_vectors(folder, output):
    """Check all K2 energy samples and delay samples against their scalars."""
    checked, curves = [], {}
    for seed in range(5):
        _, scalars, stats, _ = read_sca(folder / f"K2_Final-{seed}.sca")
        vectors = {}
        with (folder / f"K2_Final-{seed}.vec").open(encoding="utf-8") as stream:
            for line in stream:
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == "vector" and (parts[3] == "residualEnergyCapacity:vector" or
                        parts[2] == GATEWAY_APP and parts[3] == "endToEndDelay:vector"):
                    if parts[4] != "ETV":
                        raise ValueError("Expected ETV vector columns")
                    vectors[parts[1]] = dict(module=parts[2], name=parts[3], count=0, time=-math.inf,
                                              value=math.inf, total=0.0)
                elif parts[0] in vectors:
                    v = vectors[parts[0]]
                    t, value = float(parts[2]), float(parts[3])
                    if not math.isfinite(value) or t < v["time"] or not 10 <= t <= 100:
                        raise ValueError("Invalid vector time or value")
                    energy = v["name"] == "residualEnergyCapacity:vector"
                    if energy and (not 0 <= value <= 100 or value > v["value"] + 1e-9):
                        raise ValueError("Energy increased without a generator")
                    if not energy and value < 0:
                        raise ValueError("Negative end-to-end delay")
                    v.update(count=v["count"] + 1, time=t, value=value, total=v["total"] + value)
                    if seed == 0 and energy and v["count"] % 100 == 1:
                        curves.setdefault(v["module"], []).append((t, value))
        if len(vectors) != 31:
            raise ValueError(f"Seed {seed}: expected 30 energy vectors and one delay vector")
        for v in vectors.values():
            if v["count"] == 0 or v["time"] < 98:
                raise ValueError(f"Seed {seed}: empty or truncated vector")
            if v["name"] == "residualEnergyCapacity:vector":
                target = scalars[(v["module"], "residualEnergyCapacity:last")]
                if not math.isclose(v["value"], target, abs_tol=1e-9):
                    raise ValueError("Energy scalar does not match last vector sample")
                if seed == 0:
                    curves[v["module"]].append((v["time"], v["value"]))
            else:
                target = stats[(GATEWAY_APP, "endToEndDelay:stats")]
                if v["count"] != target["count"] or not math.isclose(v["total"] / v["count"], target["mean"], abs_tol=1e-12):
                    raise ValueError("Delay vector does not match scalar statistics")
            checked.append(dict(seed=seed, module=v["module"], vector=v["name"], samples=v["count"],
                                last_time_s=v["time"], last_value=v["value"], status="PASS"))
    write_csv(output / "K2_vector_checks.csv", checked)
    return curves


def check_controls(k1, k2):
    """Compare resolved parameters, including INET defaults, for existing nodes."""
    differences = []
    for key, value in k1.items():
        module, name = key
        # Display and automatically generated network addresses are not controls.
        if "display" in name.lower() or name.lower() in ("address", "macaddress", "routerid", "interfaceid", "ipv4address", "ipv6address"):
            continue
        if key not in k2 or k2[key] != value:
            if key != ("WarehouseWSN", "numSensors"):
                differences.append(f"{module}.{name}: {value!r} -> {k2.get(key)!r}")
    if differences:
        raise ValueError("K1/K2 control mismatch:\n" + "\n".join(differences[:30]))


def make_plots(output, rows, topology, curves=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    colors = ("#2563a6", "#df8421")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), layout="constrained")
    for ax, key, label in zip(axes, ("pdr_pct", "delay_mean_ms", "energy_mean_j"),
                              ("PDR (%)", "End-to-end delay (ms)", "Energy remaining (J/sensor)")):
        for scenario, color in zip(("K1", "K2"), colors):
            data = [r[key] for r in rows if r["scenario"] == scenario]
            ax.errorbar([scenario], [statistics.mean(data)], yerr=statistics.stdev(data),
                        fmt="o", color=color, capsize=5, markersize=8)
        ax.set_title(label)
        ax.grid(axis="y", alpha=.2)
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(formatter)
        if key == "pdr_pct":
            ax.set_ylim(0, 105)
        if key == "delay_mean_ms":
            ax.set_ylim(bottom=0)
    fig.suptitle("K1 vs K2 | mean and sample SD across five seeds")
    fig.savefig(output / "K1_K2_KPI.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 6.6), layout="constrained")
    for group, color, label in ((topology[:10], colors[0], "10 sensors retained from K1"),
                                (topology[10:], colors[1], "20 sensors added in K2")):
        ax.scatter([r["x_m"] for r in group], [r["y_m"] for r in group],
                   color=color, s=65, label=label)
        for r in group:
            ax.annotate(str(r["sensor"]), (r["x_m"], r["y_m"]), xytext=(5, 5), textcoords="offset points")
    ax.scatter([5], [5], marker="*", color="#192d42", s=200, label="Gateway (5, 5)")
    ax.set(xlim=(0, 100), ylim=(0, 60), xlabel="x (m)", ylabel="y (m)",
           title="K2 | configured topology | warehouse 100 x 60 m", aspect="equal")
    ax.legend(loc="upper left", bbox_to_anchor=(0, -.11), ncols=2, frameon=False)
    ax.grid(alpha=.2)
    fig.savefig(output / "K2_Topology.png", dpi=180)
    plt.close(fig)
    if curves:
        fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
        for module, data in curves.items():
            ax.plot([p[0] for p in data], [p[1] for p in data], linewidth=.7, alpha=.5)
        ax.set(xlabel="Simulation time (s)", ylabel="Energy remaining (J)",
               title="K2 seed 0 | 30 sensor energy traces (overlapping)", xlim=(10, 100))
        ax.ticklabel_format(axis="y", useOffset=False)
        ax.grid(alpha=.2)
        fig.savefig(output / "K2_Energy_Remaining.png", dpi=180)
        plt.close(fig)


def main():
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k1", type=Path, default=project.parents[1] / "K1/WarehouseWSN/simulations/results")
    parser.add_argument("--k2", type=Path, default=project / "simulations/results")
    parser.add_argument("--output", type=Path, default=project / "analysis/exports")
    parser.add_argument("--plots", action="store_true", help="Requires matplotlib")
    parser.add_argument("--verify-vectors", action="store_true", help="Read all five K2 .vec files (about 270 MB)")
    args = parser.parse_args()
    rows, nodes, resolved = [], [], {}
    for scenario, folder in (("K1", args.k1), ("K2", args.k2)):
        for seed in range(5):
            path = folder / f"{scenario}_Final-{seed}.sca"
            row, energies, pars = extract_run(path, scenario)
            if row["seed"] != seed:
                raise ValueError(f"{path}: seed does not match file name")
            rows.append(row)
            nodes.extend(energies)
            resolved[scenario, seed] = pars
    for seed in range(5):
        check_controls(resolved["K1", seed], resolved["K2", seed])
    topology = []
    p = resolved["K2", 0]
    for i in range(30):
        def coordinate(axis):
            return float(p[(f"WarehouseWSN.sensor[{i}].mobility", f"initial{axis}")].removesuffix("m"))
        topology.append(dict(sensor=i, x_m=coordinate("X"), y_m=coordinate("Y"), z_m=coordinate("Z")))
    if len({(r["x_m"], r["y_m"]) for r in topology}) != 30:
        raise ValueError("Overlapping K2 sensor positions")
    if any(not (0 <= r["x_m"] <= 100 and 0 <= r["y_m"] <= 60) for r in topology):
        raise ValueError("Sensor outside warehouse")
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "K1_K2_per_seed.csv", rows)
    write_csv(args.output / "K1_K2_energy_per_sensor.csv", nodes)
    write_csv(args.output / "K2_coordinates.csv", topology)
    summary = []
    metrics = [key for key in rows[0] if key not in ("scenario", "seed", "sensors")]
    for scenario in ("K1", "K2"):
        for key in metrics:
            data = [r[key] for r in rows if r["scenario"] == scenario]
            summary.append(dict(scenario=scenario, metric=key, n=len(data), mean=statistics.mean(data),
                                sample_sd=statistics.stdev(data), minimum=min(data), maximum=max(data)))
    write_csv(args.output / "K1_K2_summary.csv", summary)
    lines = ["# Kết quả K1 và K2 từ scalar thực tế", "",
             "K1 lấy từ 5 file upstream; K2 lấy từ 5 lần chạy K2_Final. Đơn vị thống kê là một seed, n = 5.",
             "Sai số ± dưới đây là độ lệch chuẩn mẫu giữa các seed, không phải khoảng tin cậy.", "",
             "| Kịch bản | Seed | Gửi | Nhận | PDR (%) | Delay trung bình (ms) | Energy trung bình (J/sensor) | Retry |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['scenario']} | {r['seed']} | {r['sent_packets']} | {r['received_packets']} | "
                     f"{r['pdr_pct']:.6f} | {r['delay_mean_ms']:.6f} | {r['energy_mean_j']:.9f} | {r['mac_retries']:.0f} |")
    lines += ["", "| Chỉ số | K1 mean ± SD | K2 mean ± SD |", "|---|---:|---:|"]
    for key in metrics:
        values = [next(r for r in summary if r["scenario"] == s and r["metric"] == key) for s in ("K1", "K2")]
        lines.append(f"| {key} | " + " | ".join(f"{r['mean']:.9g} ± {r['sample_sd']:.6g}" for r in values) + " |")
    lines += ["", "Energy là residualEnergyCapacity:last như K1, tức mẫu năng lượng được ghi cuối cùng; "
              "không tự sửa hoặc ngoại suy về đúng t = 100 s. Tiêu thụ được suy ra từ 100 J ban đầu.",
              "Goodput payload = Received × 64 × 8 / 90 s, trên cửa sổ đo [10, 100] s. "
              "Không gọi đây là throughput tầng PHY. Packet loss không được quy đổi thành collision.",
              "So sánh năng lượng chính dùng J/sensor; tổng tiêu thụ mạng chỉ là dữ liệu bổ sung. "
              "energy_common10_mean_j cho phép kiểm tra riêng 10 sensor được giữ nguyên.",
              "Các tham số đã resolve của sensor cũ và gateway đã được đối chiếu tự động giữa K1 và K2 "
              "cho từng seed, bỏ qua địa chỉ tự sinh và tham số hiển thị.", ""]
    (args.output / "K1_K2_results.md").write_text("\n".join(lines), encoding="utf-8")
    curves = verify_vectors(args.k2, args.output) if args.verify_vectors else None
    if args.plots:
        make_plots(args.output, rows, topology, curves)
    print(f"Validated 10 runs; wrote results to {args.output}")
    for r in summary:
        if r["metric"] in ("pdr_pct", "delay_mean_ms", "energy_mean_j"):
            print(f"{r['scenario']} {r['metric']}: {r['mean']:.9f} +/- {r['sample_sd']:.9f}")


if __name__ == "__main__":
    main()
