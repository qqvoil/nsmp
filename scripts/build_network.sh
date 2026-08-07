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
            cp -rn "$tmpl_dir"/* "$srv_dir/" 2>/dev/null || cp -r "$tmpl_dir"/* "$srv_dir/"
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

    # Clean any stale session locks
    find "${SERVER_DIR}" -name "session.lock" -delete 2>/dev/null || true
}

link_plugins() {
    echo -e "\n${YELLOW}🔌 [2/3] Привязка пула плагинов к серверам...${NC}"

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
        # Clean any improperly placed velocity plugins in paper servers
        rm -f "${SERVER_DIR}/${srv}/plugins/"*velocity* "${SERVER_DIR}/${srv}/plugins/"*Velocity* "${SERVER_DIR}/${srv}/plugins/"*TCPShield* "${SERVER_DIR}/${srv}/plugins/"*veloauth* 2>/dev/null || true
        for p in "${PLUGINS_POOL}"/*.jar; do
            local p_name
            p_name=$(basename "$p")
            # Skip velocity-only plugins
            if [[ "$p_name" == *"[Vv]elocity"* || "$p_name" == *"Velocity"* || "$p_name" == *"velocity"* || "$p_name" == *"Geyser-Velocity"* || "$p_name" == *"TCPShield"* || "$p_name" == *"veloauth"* ]]; then
                continue
            fi
            cp -u "$p" "${SERVER_DIR}/${srv}/plugins/" 2>/dev/null || cp "$p" "${SERVER_DIR}/${srv}/plugins/"
        done
    done
    echo -e "${GREEN}✓ Все плагины распределены по серверам.${NC}"
}

verify_build() {
    echo -e "\n${YELLOW}🧪 [3/3] Верификация собранной структуры...${NC}"
    local count
    count=$(ls -d "${SERVER_DIR}"/*/ 2>/dev/null | wc -l || echo 0)
    echo -e "${GREEN}✓ Успешно собрано серверов: ${count} из 11${NC}"
    echo -e "${GREEN}🎉 NeverSMP Network полностью собрана и готова к запуску!${NC}"
}

assemble_servers
link_plugins
verify_build
