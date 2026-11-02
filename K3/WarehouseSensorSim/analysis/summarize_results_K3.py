#!/usr/bin/env python3
"""Summarize K3_Final OMNeT++ .sca outputs (standard INET statistic naming).
Run: py analysis/summarize_results.py from the project root.
"""
from pathlib import Path
import csv
import re
import statistics
import sys

ROOT = Path.cwd()
FILES = sorted(ROOT.rglob('K3_Final-*.sca'))
# Avoid duplicate paths if user copied files to the analysis directory.
FILES = [p for p in FILES if 'analysis' not in p.parts]
OUT = ROOT / 'analysis'
OUT.mkdir(exist_ok=True)
SENSOR_APP = re.compile(r'(?:^|\.)sensor\[(\d+)\]\.app\[\d+\]$')
SENSOR_ENERGY = re.compile(r'(?:^|\.)sensor\[(\d+)\]\.energyStorage$')
GATEWAY_APP = re.compile(r'(?:^|\.)gateway\.app\[\d+\]$')

def parse(path):
    scalars, stats = [], {}
    current = None
    for raw in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if parts[0] == 'scalar' and len(parts) >= 4:
            try: scalars.append((parts[1], parts[2], float(parts[3])))
            except ValueError: pass
            current = None
        elif parts[0] == 'statistic' and len(parts) >= 3:
            current = (parts[1], parts[2])
            stats[current] = {}
        elif parts[0] == 'field' and current and len(parts) >= 3:
            try: stats[current][parts[1]] = float(parts[2])
            except ValueError: pass
        elif parts[0] not in ('attr','bin','param','run','itervar','config','version','runattr'):
            current = None
    return scalars, stats

def select_scalars(items, module_regex, names):
    return [(module, name, value) for module,name,value in items if module_regex.search(module) and name.lower() in names]

def write_csv(name, rows, columns):
    dest = OUT / name
    with dest.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print('Saved:', dest)

if not FILES:
    sys.exit('ERROR: Cannot find K3_Final-*.sca under '+str(ROOT))

run_rows = []
energy_rows = []
for file in FILES:
    matched = re.search(r'K3_Final-(\d+)\.sca$', file.name)
    seed = int(matched.group(1)) if matched else file.stem
    scalars, stats = parse(file)
    sent = select_scalars(scalars, SENSOR_APP, {'packetsent:count', 'packetsent:count'})
    received = select_scalars(scalars, GATEWAY_APP, {'packetreceived:count'})
    energies = select_scalars(scalars, SENSOR_ENERGY, {'residualenergycapacity:last'})
    delay_stats = [fields for (module,name),fields in stats.items()
                   if GATEWAY_APP.search(module) and name.lower().startswith('endtoenddelay')]
    # A few setups record the mean as a scalar rather than a statistic object.
    delay_scalars = select_scalars(scalars, GATEWAY_APP, {'endtoenddelay:mean','endtoenddelay:max'})
    delay_mean = delay_max = None
    if delay_stats:
        delay_mean = delay_stats[0].get('mean')
        delay_max = delay_stats[0].get('max')
    if delay_mean is None:
        delay_mean = next((v for _, n, v in delay_scalars if n.lower().endswith(':mean')), None)
    if delay_max is None:
        delay_max = next((v for _, n, v in delay_scalars if n.lower().endswith(':max')), None)
    total_sent = sum(v for _, _,v in sent) if sent else None
    total_recv = sum(v for _, _,v in received) if received else None
    energy_mean = statistics.mean(v for _,_,v in energies) if energies else None
    row = {'seed':seed, 'sensor_sent_count':len(sent), 'energy_sensor_count':len(energies),
           'sent_packets':total_sent, 'received_packets':total_recv,
           'PDR_percent':100*total_recv/total_sent if total_sent and total_recv is not None else None,
           'delay_mean_ms':1000*delay_mean if delay_mean is not None else None,
           'delay_max_ms':1000*delay_max if delay_max is not None else None,
           'energy_remaining_J_per_sensor':energy_mean,
           'energy_consumed_J_per_sensor':100-energy_mean if energy_mean is not None else None}
    run_rows.append(row)
    for module, _, value in energies:
        match=SENSOR_ENERGY.search(module)
        if match: energy_rows.append({'seed':seed,'sensor':int(match.group(1)),'energy_remaining_J':value,'energy_consumed_J':100-value})
    print('seed={}: sent={}, received={}, PDR={}, delay={} ms, energy={} J/sensor ({} sensor app counters; {} energy values)'.format(seed,total_sent,total_recv,row['PDR_percent'],row['delay_mean_ms'],energy_mean,len(sent),len(energies)))
    if len(sent)!=30 or len(energies)!=30 or total_recv is None or delay_mean is None:
        print('  WARNING: some K2-style statistics are absent. Inspect result names in this .sca file; do not treat missing KPI as zero.')

columns=list(run_rows[0])
write_csv('K3_Final_KPI_PerRun.csv', run_rows, columns)
write_csv('K3_Final_Energy_PerSensor.csv', energy_rows, ['seed','sensor','energy_remaining_J','energy_consumed_J'])
fields=['PDR_percent','delay_mean_ms','energy_remaining_J_per_sensor','energy_consumed_J_per_sensor']
summary=[]
for name in fields:
    values=[r[name] for r in run_rows if r[name] is not None]
    summary.append({'metric':name, 'runs_with_data':len(values),'mean':statistics.mean(values) if values else '',
                   'sample_stddev':statistics.stdev(values) if len(values)>1 else ''})
write_csv('K3_Final_KPI_Summary.csv', summary, ['metric','runs_with_data','mean','sample_stddev'])
print('Done. If the exported values are blank, inspect your .sca file for the actual statistic names.')
