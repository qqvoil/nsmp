#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Автоматическая генерация чанков (Chunky)
# ==============================================================================

TARGET="${1:-all}"

trigger_chunky() {
    local srv="$1"
    
    # Skip proxies and lobby
    if [[ "$srv" == "velocity" || "$srv" == "limbo" || "$srv" == "lobby" ]]; then
        return
    fi
    
    # Define max-world-size (radius) dynamically based on wipe schedule
    local radius=80000
    if [[ "$srv" == "smp1" || "$srv" == "anarchy1" ]]; then
        radius=5000
    elif [[ "$srv" == "smp2" || "$srv" == "anarchy2" || "$srv" == "hardcore1" ]]; then
        radius=15000
    elif [[ "$srv" == "hardcore2" || "$srv" == "building1" || "$srv" == "building2" ]]; then
        radius=20000
    fi

    if tmux has-session -t "nsmp_${srv}" 2>/dev/null; then
        echo "➡️ Запуск генерации чанков (Chunky) на сервере ${srv} (радиус: ${radius})..."
        tmux send-keys -t "nsmp_${srv}" "chunky radius ${radius}" Enter
        sleep 1
        tmux send-keys -t "nsmp_${srv}" "chunky start" Enter
        sleep 1
        tmux send-keys -t "nsmp_${srv}" "chunky confirm" Enter
        sleep 1
        tmux send-keys -t "nsmp_${srv}" "chunky quiet" Enter
    else
        echo "⚠️ Сервер ${srv} (nsmp_${srv}) не запущен в tmux. Пропуск генерации."
    fi
}

if [ "$TARGET" == "all" ]; then
    echo "Запуск массовой прогрузки чанков для всех игровых серверов..."
    for srv in smp1 smp2 anarchy1 anarchy2 hardcore1 hardcore2 building1 building2; do
        trigger_chunky "$srv"
    done
    echo "✅ Команды генерации успешно отправлены на сервера!"
else
    trigger_chunky "$TARGET"
fi
