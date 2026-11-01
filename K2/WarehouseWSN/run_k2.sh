#!/usr/bin/env bash
# Run inside the OMNeT++ terminal (mingwenv.cmd on Windows).
# Example: INET_ROOT=/c/omnetpp/samples/inet-4.7.0 bash run_k2.sh
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
config="${1:-K2_Final}"
ui="${2:-Cmdenv}"
case "$config" in
  K2_Minimal|K2_Coordinates|K2_OneSensorUdp|K2_OneSensorCsmaAck|K2_AllSensorsCsmaAck|K2_AllSensorsEnergy|K2_Final|K2_VisualCheck) ;;
  *) echo "Unknown configuration: $config" >&2; exit 2 ;;
esac
case "$ui" in Cmdenv|Qtenv) ;; *) echo "UI must be Cmdenv or Qtenv" >&2; exit 2 ;; esac

if [[ -z "${INET_ROOT:-}" ]]; then
  echo 'Set INET_ROOT to your INET 4.7.0 folder first.' >&2
  echo 'Example: export INET_ROOT=/c/omnetpp/samples/inet-4.7.0' >&2
  exit 2
fi
# Accept both C:/... paths and /c/... paths from the Windows OMNeT++ shell.
if command -v cygpath >/dev/null 2>&1; then
  INET_ROOT="$(cygpath -u "$INET_ROOT")"
fi
inet_dir="$(cd -- "$INET_ROOT" && pwd)"
if [[ ! -d "$inet_dir/src/inet" ]]; then
  echo "Not an INET source folder: $inet_dir" >&2
  exit 2
fi

build_mode="${BUILD_MODE:-release}"
case "$build_mode" in
  release) runner=opp_run; library="$inet_dir/src/INET" ;;
  debug) runner=opp_run_dbg; library="$inet_dir/src/INET_dbg" ;;
  *) echo 'BUILD_MODE must be release or debug' >&2; exit 2 ;;
esac
command -v "$runner" >/dev/null 2>&1 || {
  echo "Cannot find $runner. Open the OMNeT++ terminal first." >&2
  exit 2
}

ned_path=".;$inet_dir/src"
image_dir="$inet_dir/images"
if command -v cygpath >/dev/null 2>&1; then
  # opp_run is a native Windows process; its path-list separator is ';'.
  ned_path=".;$(cygpath -m "$inet_dir/src")"
  library="$(cygpath -m "$library")"
  image_dir="$(cygpath -m "$image_dir")"
  export MSYS2_ARG_CONV_EXCL='*'
fi
cd -- "$project_dir/simulations"
mkdir -p results
run_numbers=(0)
if [[ "$config" == K2_Final && "$ui" == Cmdenv ]]; then
  run_numbers=(0 1 2 3 4)
fi
for run_number in "${run_numbers[@]}"; do
  echo "Running $config, repetition $run_number, $ui, $build_mode"
  "$runner" -u "$ui" -n "$ned_path" -l "$library" \
    --image-path="$image_dir" -c "$config" -r "$run_number" omnetpp.ini \
    2>&1 | tee "results/${config}-${run_number}.log"
done
echo 'Finished. Results are in WarehouseWSN/simulations/results.'
