#!/usr/bin/env bash
# ==============================================================================
# NeverSMP Network — Master Server Manager (tmux based)
# ==============================================================================

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/server"
TMUX_PREFIX="nsmp"

# Server definitions: [name]="DIR|PORT|RAM_MIN|RAM_MAX|JAR_NAME"
declare -A SERVERS=(
    ["velocity"]="velocity|25565|512M|1G|velocity.jar"
    ["limbo"]="Limbo|25567|128M|256M|limbo.jar"
    ["lobby"]="Lobby|25566|1G|2G|server.jar"
    ["smp1"]="SMP1|25590|3G|5G|server.jar"
    ["smp2"]="SMP2|25587|3G|5G|server.jar"
    ["hardcore1"]="hardcore1|25589|2G|4G|server.jar"
    ["hardcore2"]="hardcore2|25586|2G|4G|server.jar"
    ["anarchy1"]="anarchy1|25588|3G|5G|server.jar"
    ["anarchy2"]="anarchy2|25585|3G|5G|server.jar"
    ["building1"]="building1|25583|2G|3G|server.jar"
    ["building2"]="building2|25584|2G|3G|server.jar"
)

# Startup order (Auth/Proxy first, then Lobby, then Game servers)
START_ORDER=("limbo" "velocity" "lobby" "smp1" "smp2" "hardcore1" "hardcore2" "anarchy1" "anarchy2" "building1" "building2")

AIKAR_FLAGS="-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:G1InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true"

is_running() {
    local srv="$1"
    tmux has-session -t "${TMUX_PREFIX}_${srv}" 2>/dev/null
}

start_server() {
    local srv="$1"
    if [[ -z "${SERVERS[$srv]}" ]]; then
        echo "❌ Неизвестный сервер: $srv"
        return 1
    fi

    if is_running "$srv"; then
        echo "⚠️ Сервер $srv уже запущен в tmux-сессии '${TMUX_PREFIX}_${srv}'."
        return 0
    fi

    IFS='|' read -r dir port ram_min ram_max jar <<< "${SERVERS[$srv]}"
    local target_dir="$BASE_DIR/$dir"

    if [[ ! -d "$target_dir" ]]; then
        echo "❌ Каталог $target_dir не найден!"
        return 1
    fi

    if [[ ! -f "$target_dir/$jar" ]]; then
        local found_jar
        found_jar=$(find "$target_dir" -maxdepth 1 -name "*.jar" | head -n 1)
        if [[ -n "$found_jar" ]]; then
            jar=$(basename "$found_jar")
        fi
    fi

    echo "🚀 Запуск $srv ($dir) [RAM: $ram_max, Port: $port]..."
    if [[ "$srv" == "velocity" || "$srv" == "limbo" ]]; then
        tmux new-session -d -s "${TMUX_PREFIX}_${srv}" -c "$target_dir" \
            "java -Xms${ram_min} -Xmx${ram_max} -jar ${jar}"
    else
        tmux new-session -d -s "${TMUX_PREFIX}_${srv}" -c "$target_dir" \
            "java -Xms${ram_min} -Xmx${ram_max} ${AIKAR_FLAGS} -jar ${jar} nogui"
    fi
    
    sleep 1
}

stop_server() {
    local srv="$1"
    if ! is_running "$srv"; then
        echo "⏹ Сервер $srv не запущен."
        return 0
    fi

    echo "🛑 Остановка $srv..."
    if [[ "$srv" == "velocity" ]]; then
        tmux send-keys -t "${TMUX_PREFIX}_${srv}" "end" Enter
    else
        tmux send-keys -t "${TMUX_PREFIX}_${srv}" "stop" Enter
    fi

    # Wait up to 15 seconds for clean shutdown
    for i in {1..15}; do
        if ! is_running "$srv"; then
            echo "✓ Сервер $srv успешно остановлен."
            return 0
        fi
        sleep 1
    done

    echo "⚠️ Принудительное завершение сессии $srv..."
    tmux kill-session -t "${TMUX_PREFIX}_${srv}" 2>/dev/null
}

console_server() {
    local srv="$1"
    if ! is_running "$srv"; then
        echo "❌ Сервер $srv не запущен."
        return 1
    fi
    echo "🎮 Подключение к консоли $srv (Для выхода нажмите Ctrl+B затем D)..."
    tmux attach-session -t "${TMUX_PREFIX}_${srv}"
}

status_all() {
    echo "================================================================="
    echo "                 NeverSMP Network Status                         "
    echo "================================================================="
    printf "%-12s | %-8s | %-8s | %-10s | %-12s\n" "Сервер" "Статус" "Порт" "RAM Макс" "Tmux Сессия"
    echo "-----------------------------------------------------------------"
    for srv in "${START_ORDER[@]}"; do
        IFS='|' read -r dir port ram_min ram_max jar <<< "${SERVERS[$srv]}"
        if is_running "$srv"; then
            printf "\e[32m%-12s\e[0m | \e[32mONLINE \e[0m | %-8s | %-10s | %-12s\n" "$srv" "$port" "$ram_max" "${TMUX_PREFIX}_${srv}"
        else
            printf "\e[31m%-12s\e[0m | \e[31mOFFLINE\e[0m | %-8s | %-10s | -\n" "$srv" "$port" "$ram_max"
        fi
    done
    echo "================================================================="
}

case "$1" in
    start)
        if [[ "$2" == "all" || -z "$2" ]]; then
            echo "🌟 Запуск всей сети NeverSMP Network..."
            for srv in "${START_ORDER[@]}"; do
                start_server "$srv"
                sleep 2
            done
            status_all
        else
            start_server "$2"
        fi
        ;;
    stop)
        if [[ "$2" == "all" || -z "$2" ]]; then
            echo "🛑 Остановка всей сети NeverSMP Network..."
            # Stop game servers first, then Lobby, then Proxy
            for (( idx=${#START_ORDER[@]}-1 ; idx>=0 ; idx-- )) ; do
                stop_server "${START_ORDER[idx]}"
            done
            status_all
        else
            stop_server "$2"
        fi
        ;;
    restart)
        if [[ "$2" == "all" || -z "$2" ]]; then
            $0 stop all
            sleep 3
            $0 start all
        else
            stop_server "$2"
            sleep 2
            start_server "$2"
        fi
        ;;
    console)
        if [[ -z "$2" ]]; then
            echo "Использование: $0 console <имя_сервера>"
            echo "Доступные сервера: ${START_ORDER[*]}"
            exit 1
        fi
        console_server "$2"
        ;;
    status)
        status_all
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|console|status} [имя_сервера|all]"
        echo "Примеры:"
        echo "  $0 start all        # Запустить всю сеть"
        echo "  $0 stop all         # Остановить всю сеть"
        echo "  $0 restart lobby    # Перезапустить лобби"
        echo "  $0 console smp1     # Войти в консоль SMP1"
        echo "  $0 status           # Посмотреть статус всех серверов"
        exit 1
        ;;
esac
