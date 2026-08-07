#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Nightly Maintenance Restart (03:00 MSK)
# ==============================================================================

MANAGER_SCRIPT="$(dirname "$0")/server-manager.sh"
BACKUP_SCRIPT="$(dirname "$0")/backup_worlds.sh"

send_broadcast() {
    local msg="$1"
    # Send broadcast to all tmux sessions
    for session in nsmp_velocity nsmp_lobby nsmp_smp1 nsmp_smp2 nsmp_hardcore1 nsmp_hardcore2 nsmp_anarchy1 nsmp_anarchy2 nsmp_building1 nsmp_building2; do
        if tmux has-session -t "$session" 2>/dev/null; then
            tmux send-keys -t "$session" "broadcast $msg" Enter 2>/dev/null || true
            tmux send-keys -t "$session" "say $msg" Enter 2>/dev/null || true
        fi
    done
}

save_all_worlds() {
    for session in nsmp_lobby nsmp_smp1 nsmp_smp2 nsmp_hardcore1 nsmp_hardcore2 nsmp_anarchy1 nsmp_anarchy2 nsmp_building1 nsmp_building2; do
        if tmux has-session -t "$session" 2>/dev/null; then
            tmux send-keys -t "$session" "save-all" Enter 2>/dev/null || true
        fi
    done
}

echo "[$(date)] Starting 03:00 MSK maintenance cycle..."

# 1. 10 Minute Warning
send_broadcast "§6§l[ВНИМАНИЕ] §fПлановый ночной рестарт серверов через §e10 минут§f!"
sleep 300

# 2. 5 Minute Warning
send_broadcast "§6§l[ВНИМАНИЕ] §fПлановый ночной рестарт через §e5 минут§f. Завершайте важные дела!"
sleep 240

# 3. 1 Minute Warning & World Save
send_broadcast "§c§l[ВНИМАНИЕ] §fРестарт через §c1 минуту§f! Сохранение игрового мира..."
save_all_worlds
sleep 50

# 4. 10 Second Final Countdown
send_broadcast "§c§l[ВНИМАНИЕ] §fРестарт через §c10 секунд§f! До встречи через 1 минуту!"
sleep 10

# 5. Run backup and restart all servers
bash "${BACKUP_SCRIPT}" || true
bash "${MANAGER_SCRIPT}" restart all

echo "[$(date)] Nightly maintenance restart successfully completed!"
