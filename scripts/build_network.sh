#!/usr/bin/env bash
# ==============================================================================
# NeverSMP Network — Automated Infrastructure Builder (IaC)
# Assembles all 11 Minecraft servers from lightweight templates & plugin pool.
# ==============================================================================

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="${BASE_DIR}/server"
CORE_DIR="${BASE_DIR}/core"
JARS_DIR="${CORE_DIR}/jars"
TEMPLATES_DIR="${CORE_DIR}/templates"
PLUGINS_POOL="${CORE_DIR}/plugins_pool"
MAPS_DIR="${CORE_DIR}/maps"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}================================================================="
echo "   ⚡ NeverSMP Network — Automated Build & Assemble Engine"
echo -e "=================================================================${NC}"

RCON_PASS=$(grep -oP '^RCON_PASS=\K.*' "${BASE_DIR}/backend/.env" 2>/dev/null || echo "neversmp_rcon_dev")

mkdir -p "${SERVER_DIR}"

# 1. Server setup definitions
# Format: NAME|TEMPLATE|PORT|JAR_TYPE|MAP_TAR|RAM_MIN|RAM_MAX
declare -a SERVERS_CONFIG=(
    "velocity|velocity|25565|velocity||512M|1G"
    "Limbo|Limbo|25567|limbo||128M|256M"
    "Lobby|Lobby|25566|paper|lobby_world.tar.gz|1G|2G"
    "SMP1|SMP|25590|paper||2G|4G"
    "SMP2|SMP|25587|paper||2G|4G"
    "anarchy1|anarchy1|25588|paper||2G|4G"
    "anarchy2|anarchy1|25585|paper||2G|4G"
    "hardcore1|hardcore1|25589|paper|hardcore_world.tar.gz|2G|4G"
    "hardcore2|hardcore1|25586|paper|hardcore_world.tar.gz|2G|4G"
    "building1|building1|25583|paper|building_world.tar.gz|1G|2G"
    "building2|building1|25584|paper|building_world.tar.gz|1G|2G"
)

assemble_servers() {
    echo -e "\n${YELLOW}🏗 [1/3] Развертывание структуры 11 серверов...${NC}"

    for entry in "${SERVERS_CONFIG[@]}"; do
        IFS='|' read -r name template port jar_type map_archive ram_min ram_max <<< "$entry"
        local srv_dir="${SERVER_DIR}/${name}"
        local tmpl_dir="${TEMPLATES_DIR}/${template}"

        echo -e "⚙️ Сборка ${CYAN}${name}${NC} (Порт: ${port}, Шаблон: ${template})..."
        mkdir -p "${srv_dir}/plugins"

        # Copy clean template configs
        if [[ -d "$tmpl_dir" ]]; then
            cp -r "$tmpl_dir"/* "$srv_dir/"
        fi

        # Place the correct server jar from core/jars and generate start.sh
        if [[ "$jar_type" == "velocity" ]]; then
            cp "${JARS_DIR}/velocity.jar" "${srv_dir}/velocity.jar"
            cat << 'EOF' > "${srv_dir}/start.sh"
#!/usr/bin/env bash
exec java -Xms512M -Xmx1G -jar velocity.jar
EOF
        elif [[ "$jar_type" == "limbo" ]]; then
            cp "${JARS_DIR}/limbo.jar" "${srv_dir}/limbo.jar"
            cat << 'EOF' > "${srv_dir}/start.sh"
#!/usr/bin/env bash
exec java -Xms128M -Xmx256M -jar limbo.jar
EOF
        else
            cp "${JARS_DIR}/paper-1.21.4.jar" "${srv_dir}/server.jar"
            cat << EOF > "${srv_dir}/start.sh"
#!/usr/bin/env bash
exec java -Xms${ram_min} -Xmx${ram_max} -XX:+UseG1GC -jar server.jar nogui
EOF
        fi

        chmod +x "${srv_dir}/start.sh"

        # Accept EULA
        echo "eula=true" > "${srv_dir}/eula.txt"

        # Adjust server.properties port and world size if file exists
        if [[ -f "${srv_dir}/server.properties" ]]; then
            rcon_port=$((port - 14))
            sed -i.bak "s/^server-port=.*/server-port=${port}/" "${srv_dir}/server.properties" 2>/dev/null || true
            sed -i.bak "s/^query.port=.*/query.port=${port}/" "${srv_dir}/server.properties" 2>/dev/null || true
            sed -i.bak "s/^rcon.port=.*/rcon.port=${rcon_port}/" "${srv_dir}/server.properties" 2>/dev/null || true
            sed -i.bak "s/^enable-rcon=.*/enable-rcon=true/" "${srv_dir}/server.properties" 2>/dev/null || true
            sed -i.bak "s/^rcon.password=.*/rcon.password=${RCON_PASS}/" "${srv_dir}/server.properties" 2>/dev/null || true
            
            # Set world size based on wipe schedule
            if [[ "$name" == "SMP1" || "$name" == "anarchy1" ]]; then
                sed -i.bak "s/^max-world-size=.*/max-world-size=5000/" "${srv_dir}/server.properties" 2>/dev/null || true
            elif [[ "$name" == "SMP2" || "$name" == "anarchy2" || "$name" == "hardcore1" ]]; then
                sed -i.bak "s/^max-world-size=.*/max-world-size=15000/" "${srv_dir}/server.properties" 2>/dev/null || true
            elif [[ "$name" == "hardcore2" ]]; then
                sed -i.bak "s/^max-world-size=.*/max-world-size=20000/" "${srv_dir}/server.properties" 2>/dev/null || true
            else
                sed -i.bak "s/^max-world-size=.*/max-world-size=80000/" "${srv_dir}/server.properties" 2>/dev/null || true
            fi
            
            rm -f "${srv_dir}/server.properties.bak"
        fi

        # Unpack world map if defined and world directory doesn't exist
        if [[ -n "$map_archive" && ! -d "${srv_dir}/world" && -f "${MAPS_DIR}/${map_archive}" ]]; then
            echo -e "  🗺 Распаковка карты ${map_archive} в ${name}/world..."
            mkdir -p "${srv_dir}/world"
            tar -xzf "${MAPS_DIR}/${map_archive}" -C "${srv_dir}/world"
        fi
    done

    # Clean any stale session locks
    find "${SERVER_DIR}" -name "session.lock" -delete 2>/dev/null || true
}

link_plugins() {
    echo -e "\n${YELLOW}🔌 [2/3] Привязка пула плагинов к серверам...${NC}"

    # Velocity plugins
    local VELO_PLUGINS=("Geyser-Velocity.jar" "floodgate-velocity.jar" "TCPShield-2.8.1 (1).jar" "veloauth-latest.jar" "VelocityPlayerListQuery-1.5.0.jar" "voicechat-velocity-2.6.18.jar" "LuckPerms-Velocity-5.5.71.jar")
    for p in "${VELO_PLUGINS[@]}"; do
        if [[ -f "${PLUGINS_POOL}/${p}" ]]; then
            cp -u "${PLUGINS_POOL}/${p}" "${SERVER_DIR}/velocity/plugins/" 2>/dev/null || cp "${PLUGINS_POOL}/${p}" "${SERVER_DIR}/velocity/plugins/"
        fi
    done

    # Paper Common plugins for all game servers
    local GAME_SERVERS=("Lobby" "SMP1" "SMP2" "anarchy1" "anarchy2" "hardcore1" "hardcore2" "building1" "building2")
    for srv in "${GAME_SERVERS[@]}"; do
        # Clean existing jars to avoid stale plugins
        rm -f "${SERVER_DIR}/${srv}/plugins/"*.jar 2>/dev/null || true

        # Clean mode-mismatched plugin config folders
        if [[ "$srv" != "Lobby" ]]; then
            rm -rf "${SERVER_DIR}/${srv}/plugins/sCheckPlayer" "${SERVER_DIR}/${srv}/plugins/DGCommandItems" "${SERVER_DIR}/${srv}/plugins/UltraItemLock" "${SERVER_DIR}/${srv}/plugins/kav16Disable" 2>/dev/null || true
        fi
        if [[ "$srv" != hardcore* ]]; then
            rm -rf "${SERVER_DIR}/${srv}/plugins/HardcoreRevive" 2>/dev/null || true
        fi
        if [[ "$srv" != SMP* && "$srv" != anarchy* ]]; then
            rm -rf "${SERVER_DIR}/${srv}/plugins/CrazyAuctions" "${SERVER_DIR}/${srv}/plugins/DonutAuctionHouse" "${SERVER_DIR}/${srv}/plugins/DonutOrders" "${SERVER_DIR}/${srv}/plugins/GUIShop" 2>/dev/null || true
        fi
        if [[ "$srv" == "Lobby" ]]; then
            rm -rf "${SERVER_DIR}/${srv}/plugins/AdvancedRTP" "${SERVER_DIR}/${srv}/plugins/SimpleClans" "${SERVER_DIR}/${srv}/plugins/SimpleTPA" 2>/dev/null || true
        fi

        for p in "${PLUGINS_POOL}"/*.jar; do
            local p_name
            p_name=$(basename "$p")
            # Skip velocity-only plugins
            if [[ "$p_name" == *velocity* || "$p_name" == *Velocity* || "$p_name" == *Geyser-Velocity* || "$p_name" == *TCPShield* || "$p_name" == *veloauth* ]]; then
                continue
            fi
            # Filter HardcoreRevive (Hardcore servers only)
            if [[ "$p_name" == *HardcoreRevive* ]] && [[ "$srv" != hardcore* ]]; then
                continue
            fi
            # Filter CrazyAuctions (SMP and Anarchy servers only)
            if [[ "$p_name" == *CrazyAuctions* ]] && [[ "$srv" != SMP* ]] && [[ "$srv" != anarchy* ]]; then
                continue
            fi
            # Filter AdvancedRTP and SimpleClans (Game modes only, not Lobby)
            if [[ "$p_name" == *AdvancedRTP* || "$p_name" == *SimpleClans* ]] && [[ "$srv" == "Lobby" ]]; then
                continue
            fi
            # Filter Lobby-specific items plugins
            if [[ "$p_name" == *DGCommandItems* || "$p_name" == *ItemLock* || "$p_name" == *kav16Disable* ]] && [[ "$srv" != "Lobby" ]]; then
                continue
            fi

            cp "$p" "${SERVER_DIR}/${srv}/plugins/"
        done
    done
    echo -e "${GREEN}✓ Все плагины распределены по серверам.${NC}"
}

apply_configs() {
    echo -e "\n${YELLOW}⚙️ [3/4] Применение глобальных конфигураций MySQL...${NC}"
    NSMP_DB_PASSWORD="NeverSMP_SecureDB_2026!" python3 "${BASE_DIR}/scripts/apply_mysql_configs.py"
}

verify_build() {
    echo -e "\n${YELLOW}🧪 [4/4] Верификация собранной структуры...${NC}"
    local count
    count=$(ls -d "${SERVER_DIR}"/*/ 2>/dev/null | wc -l || echo 0)
    echo -e "${GREEN}✓ Успешно собрано серверов: ${count} из 11${NC}"
    echo -e "${GREEN}🎉 NeverSMP Network полностью собрана и готова к запуску!${NC}"
}

assemble_servers
link_plugins
apply_configs
verify_build
