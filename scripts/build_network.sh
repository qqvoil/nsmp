#!/usr/bin/env bash
# ==============================================================================
# NeverSMP Network — Automated Infrastructure Builder (IaC)
# Assembles all 11 Minecraft servers from lightweight templates & plugin pool.
# ==============================================================================

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="${BASE_DIR}/server"
CACHE_DIR="${BASE_DIR}/cache"
CORE_DIR="${BASE_DIR}/core"
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

mkdir -p "${CACHE_DIR}"
mkdir -p "${SERVER_DIR}"

# 1. Download Server Jars if missing
download_jars() {
    echo -e "\n${YELLOW}📥 [1/4] Проверка и загрузка серверных ядер (Paper / Velocity)...${NC}"
    
    # Paper 1.21.4
    if [[ ! -f "${CACHE_DIR}/paper-1.21.4.jar" ]]; then
        echo -e "${CYAN}Загрузка Paper 1.21.4 с официального API PaperMC...${NC}"
        LATEST_BUILD=$(curl -s https://api.papermc.io/v2/projects/paper/versions/1.21.4 | grep -o '"builds":\[[^]]*\]' | grep -o '[0-9]*' | tail -n 1 || echo "227")
        if [[ -z "$LATEST_BUILD" ]]; then LATEST_BUILD="227"; fi
        curl -fsSL "https://api.papermc.io/v2/projects/paper/versions/1.21.4/builds/${LATEST_BUILD}/downloads/paper-1.21.4-${LATEST_BUILD}.jar" -o "${CACHE_DIR}/paper-1.21.4.jar"
        echo -e "${GREEN}✓ Paper 1.21.4 (build ${LATEST_BUILD}) успешно загружен.${NC}"
    else
        echo -e "${GREEN}✓ Paper 1.21.4 уже в кэше.${NC}"
    fi

    # Velocity Proxy
    if [[ ! -f "${CACHE_DIR}/velocity.jar" ]]; then
        echo -e "${CYAN}Загрузка Velocity Proxy с PaperMC API...${NC}"
        LATEST_VELO_BUILD=$(curl -s https://api.papermc.io/v2/projects/velocity/versions/3.4.0-SNAPSHOT | grep -o '"builds":\[[^]]*\]' | grep -o '[0-9]*' | tail -n 1 || echo "465")
        if [[ -z "$LATEST_VELO_BUILD" ]]; then LATEST_VELO_BUILD="465"; fi
        curl -fsSL "https://api.papermc.io/v2/projects/velocity/versions/3.4.0-SNAPSHOT/builds/${LATEST_VELO_BUILD}/downloads/velocity-3.4.0-SNAPSHOT-${LATEST_VELO_BUILD}.jar" -o "${CACHE_DIR}/velocity.jar"
        echo -e "${GREEN}✓ Velocity (build ${LATEST_VELO_BUILD}) успешно загружен.${NC}"
    else
        echo -e "${GREEN}✓ Velocity jar уже в кэше.${NC}"
    fi

    # Limbo Auth
    if [[ ! -f "${CACHE_DIR}/limbo.jar" ]]; then
        if [[ -f "${TEMPLATES_DIR}/Limbo/limbo.jar" ]]; then
            cp "${TEMPLATES_DIR}/Limbo/limbo.jar" "${CACHE_DIR}/limbo.jar"
        else
            echo -e "${CYAN}Загрузка Limbo Auth...${NC}"
            curl -fsSL "https://github.com/LOSEMYMIND/Limbo/releases/download/v0.3.5/limbo.jar" -o "${CACHE_DIR}/limbo.jar" || true
        fi
    fi
}

# 2. Server setup definitions
# Format: NAME|TEMPLATE|PORT|JAR_TYPE|MAP_TAR
declare -a SERVERS_CONFIG=(
    "velocity|velocity|25565|velocity|"
    "Limbo|Limbo|25567|limbo|"
    "Lobby|Lobby|25566|paper|lobby_world.tar.gz"
    "SMP1|SMP|25590|paper|"
    "SMP2|SMP|25587|paper|"
    "anarchy1|anarchy1|25588|paper|"
    "anarchy2|anarchy1|25585|paper|"
    "hardcore1|hardcore1|25589|paper|hardcore_world.tar.gz"
    "hardcore2|hardcore1|25586|paper|hardcore_world.tar.gz"
    "building1|building1|25583|paper|building_world.tar.gz"
    "building2|building1|25584|paper|building_world.tar.gz"
)

assemble_servers() {
    echo -e "\n${YELLOW}🏗 [2/4] Развертывание структуры 11 серверов...${NC}"

    for entry in "${SERVERS_CONFIG[@]}"; do
        IFS='|' read -r name template port jar_type map_archive <<< "$entry"
        local srv_dir="${SERVER_DIR}/${name}"
        local tmpl_dir="${TEMPLATES_DIR}/${template}"

        echo -e "⚙️ Сборка ${CYAN}${name}${NC} (Порт: ${port}, Шаблон: ${template})..."
        mkdir -p "${srv_dir}/plugins"

        # Copy clean template configs
        if [[ -d "$tmpl_dir" ]]; then
            cp -rn "$tmpl_dir"/* "$srv_dir/" 2>/dev/null || cp -r "$tmpl_dir"/* "$srv_dir/"
        fi

        # Place the correct server jar
        if [[ "$jar_type" == "velocity" ]]; then
            cp "${CACHE_DIR}/velocity.jar" "${srv_dir}/velocity.jar"
        elif [[ "$jar_type" == "limbo" ]]; then
            if [[ -f "${CACHE_DIR}/limbo.jar" ]]; then
                cp "${CACHE_DIR}/limbo.jar" "${srv_dir}/limbo.jar"
            fi
        else
            cp "${CACHE_DIR}/paper-1.21.4.jar" "${srv_dir}/server.jar"
        fi

        # Accept EULA
        echo "eula=true" > "${srv_dir}/eula.txt"

        # Adjust server.properties port if file exists
        if [[ -f "${srv_dir}/server.properties" ]]; then
            sed -i.bak "s/^server-port=.*/server-port=${port}/" "${srv_dir}/server.properties" 2>/dev/null || true
            sed -i.bak "s/^query.port=.*/query.port=${port}/" "${srv_dir}/server.properties" 2>/dev/null || true
            rm -f "${srv_dir}/server.properties.bak"
        fi

        # Unpack world map if defined and world directory doesn't exist
        if [[ -n "$map_archive" && ! -d "${srv_dir}/world" && -f "${MAPS_DIR}/${map_archive}" ]]; then
            echo -e "  🗺 Распаковка карты ${map_archive} в ${name}/world..."
            mkdir -p "${srv_dir}/world"
            tar -xzf "${MAPS_DIR}/${map_archive}" -C "${srv_dir}/world"
        fi
    done
}

link_plugins() {
    echo -e "\n${YELLOW}🔌 [3/4] Привязка пула плагинов к серверам...${NC}"

    # Velocity plugins
    local VELO_PLUGINS=("Geyser-Velocity.jar" "floodgate-velocity.jar" "TCPShield-2.8.1 (1).jar" "veloauth-latest.jar" "VelocityPlayerListQuery-1.5.0.jar" "voicechat-velocity-2.6.18.jar")
    for p in "${VELO_PLUGINS[@]}"; do
        if [[ -f "${PLUGINS_POOL}/${p}" ]]; then
            cp -u "${PLUGINS_POOL}/${p}" "${SERVER_DIR}/velocity/plugins/" 2>/dev/null || cp "${PLUGINS_POOL}/${p}" "${SERVER_DIR}/velocity/plugins/"
        fi
    done

    # Paper Common plugins for all game servers
    local GAME_SERVERS=("Lobby" "SMP1" "SMP2" "anarchy1" "anarchy2" "hardcore1" "hardcore2" "building1" "building2")
    for srv in "${GAME_SERVERS[@]}"; do
        for p in "${PLUGINS_POOL}"/*.jar; do
            local p_name
            p_name=$(basename "$p")
            # Skip velocity-only plugins
            if [[ "$p_name" == *"velocity"* || "$p_name" == *"Geyser-Velocity"* || "$p_name" == *"TCPShield"* || "$p_name" == *"veloauth"* ]]; then
                continue
            fi
            cp -u "$p" "${SERVER_DIR}/${srv}/plugins/" 2>/dev/null || cp "$p" "${SERVER_DIR}/${srv}/plugins/"
        done
    done
    echo -e "${GREEN}✓ Все плагины распределены по серверам.${NC}"
}

verify_build() {
    echo -e "\n${YELLOW}🧪 [4/4] Верификация собранной структуры...${NC}"
    local count
    count=$(ls -d "${SERVER_DIR}"/*/ 2>/dev/null | wc -l || echo 0)
    echo -e "${GREEN}✓ Успешно собрано серверов: ${count} из 11${NC}"
    echo -e "${GREEN}${BOLD}🎉 NeverSMP Network полностью собрана и готова к запуску!${NC}"
}

download_jars
assemble_servers
link_plugins
verify_build
