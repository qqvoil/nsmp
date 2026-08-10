#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Safe Monthly Wipe Script (SMP & Anarchy)
# Strictly preserves Player Tokens, Auth Accounts, and LuckPerms Ranks in MariaDB.
# ==============================================================================

set -e

TARGET="${1}"
SERVER_ROOT="${HOME}/data/server"
BACKUP_SCRIPT="$(dirname "$0")/backup_worlds.sh"

if [ -z "$TARGET" ]; then
    echo "Использование: ./wipe_server.sh <smp1|smp2|anarchy1|anarchy2|hardcore1|all_wipeable>"
    exit 1
fi

echo "=================================================="
echo "⚠️  ВНИМАНИЕ: Запущен процесс ВАЙПА для: ${TARGET}"
echo "   Токены и Премиум в MariaDB БУДУТ СОХРАНЕНЫ!"
echo "=================================================="

# 1. First make an emergency backup of current worlds before wiping
echo "[1/4] Создание архивного бэкапа перед вайпом..."
bash "${BACKUP_SCRIPT}" || true

wipe_single_server() {
    local srv="$1"
    local srv_dir="${SERVER_ROOT}/${srv}"
    
    if [ ! -d "$srv_dir" ]; then
        echo "[-] Сервер ${srv} не найден в ${SERVER_ROOT}."
        return
    fi

    echo "[2/4] Остановка сервера ${srv}..."
    if [[ "$srv" == "hardcore1" ]]; then
        echo "Снятие банов смертей (очистка hardcore.dead) через MariaDB..."
        # Удаляем право hardcore.dead у всех игроков в базе LuckPerms
        mysql -u nsmp_user -p"NeverSMP_SecureDB_2026!" neversmp -e "DELETE FROM lp_user_permissions WHERE permission = 'hardcore.dead';" 2>/dev/null || true
        # Синхронизируем изменения на обоих серверах хардкора перед их рестартом
        tmux send-keys -t "nsmp_hardcore1" "lp sync" Enter 2>/dev/null || true
        tmux send-keys -t "nsmp_hardcore2" "lp sync" Enter 2>/dev/null || true
        sleep 2
    fi
    if tmux has-session -t "nsmp_${srv}" 2>/dev/null; then
        tmux send-keys -t "nsmp_${srv}" "stop" Enter
        sleep 5
    fi

    echo "[3/4] Очистка миров, инвентарей, точек домов и аукционов на ${srv}..."
    # Remove world folders
    rm -rf "${srv_dir}/world" "${srv_dir}/world_nether" "${srv_dir}/world_the_end"
    
    # Remove playerdata, stats, advancements
    rm -rf "${srv_dir}/plugins/Essentials/userdata" 2>/dev/null || true
    rm -rf "${srv_dir}/plugins/WorldGuard/worlds" 2>/dev/null || true
    rm -rf "${srv_dir}/plugins/GriefPreventionData" 2>/dev/null || true
    rm -rf "${srv_dir}/plugins/AuctionHouse" 2>/dev/null || true
    rm -rf "${srv_dir}/plugins/zAuctionHouse" 2>/dev/null || true
    rm -rf "${srv_dir}/plugins/Chunky" 2>/dev/null || true

    echo "[4/4] Запуск свежего сервера ${srv} с новой генерацией мира..."
    bash "$(dirname "$0")/server-manager.sh" start "${srv}"
    echo "[5/5] Ожидание запуска для старта прогрузки чанков (Chunky)..."
    sleep 40
    bash "$(dirname "$0")/pregenerate_worlds.sh" "${srv}"
    echo "✅ Вайп сервера ${srv} успешно завершен!"
}

if [ "$TARGET" == "all_wipeable" ]; then
    for srv in smp1 anarchy1; do
        wipe_single_server "$srv"
    done
else
    wipe_single_server "$TARGET"
fi

echo "=================================================="
echo "✨ Все плановые миры пересозданы. Сеть готова к новому сезону!"
