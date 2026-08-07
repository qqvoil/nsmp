#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Crash Watchdog (Auto-Recovery)
# ==============================================================================

MANAGER_SCRIPT="$(dirname "$0")/server-manager.sh"

SERVERS=("velocity" "limbo" "lobby" "smp1" "smp2" "hardcore1" "hardcore2" "anarchy1" "anarchy2" "building1" "building2")

for srv in "${SERVERS[@]}"; do
    session="nsmp_${srv}"
    if ! tmux has-session -t "$session" 2>/dev/null; then
        echo "[$(date)] ⚠️ Server '${srv}' is DOWN! Automatically restarting..."
        bash "${MANAGER_SCRIPT}" start "$srv"
    fi
done
