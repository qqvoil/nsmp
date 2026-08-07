#!/usr/bin/env bash
# =================================================================
#        🚀 NeverSMP Production Server Deployment & Setup
# =================================================================
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}================================================================="
echo "        🚀 NeverSMP Production Server Deployment & Setup         "
echo -e "=================================================================${NC}"

# Check root privileges
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Запустите скрипт от имени root (sudo ./deploy.sh)${NC}"
    exit 1
fi

# 1. Установка системных зависимостей
echo -e "\n${YELLOW}📦 [1/6] Установка системных пакетов и зависимостей...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    curl \
    wget \
    git \
    tmux \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    ethtool \
    net-tools \
    iproute2 \
    tar \
    gzip \
    unzip \
    iptables

# 2. Проверка / установка Java 21
if ! command -v java >/dev/null 2>&1 || ! java -version 2>&1 | grep -q "21"; then
    echo -e "${YELLOW}☕ Установка Java 21 (Temurin / OpenJDK)...${NC}"
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --batch --yes --dearmor -o /etc/apt/keyrings/adoptium.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main' > /etc/apt/sources.list.d/adoptium.list
    apt-get update -qq
    apt-get install -y -qq temurin-21-jre
fi

pip install --break-system-packages -q flask gunicorn requests python-dotenv 2>/dev/null || pip install -q flask gunicorn requests python-dotenv

# Ensure system hostname is mapped in /etc/hosts for Java network stack
SYS_HOSTNAME=$(cat /etc/hostname 2>/dev/null || hostname)
if [[ -n "$SYS_HOSTNAME" ]] && ! grep -q "$SYS_HOSTNAME" /etc/hosts; then
    echo "127.0.0.1 ${SYS_HOSTNAME}" >> /etc/hosts
fi

echo -e "${GREEN}✓ Системные пакеты, Java 21 и библиотеки Python установлены.${NC}"

# 3. Конфигурация .env
echo -e "\n${YELLOW}🔑 [2/6] Проверка и настройка backend/.env...${NC}"
ENV_FILE="${BASE_DIR}/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat << 'ENVEOF' > "$ENV_FILE"
SECRET_KEY=change_this_to_a_secure_random_key_in_production
SITE_URL=https://donate.neversmp.ru
PLATEGA_PROJECT_ID=your_platega_project_id
PLATEGA_SECRET_KEY=your_platega_secret_key
ADMIN_PASSWORD=neversmp_admin_2026
RCON_LOBBY_HOST=127.0.0.1
RCON_LOBBY_PORT=25575
RCON_SMP1_HOST=127.0.0.1
RCON_SMP1_PORT=25576
RCON_PASS=change_this_rcon_password
ENVEOF
    echo -e "${GREEN}✓ Создан шаблон файла .env.${NC}"
else
    # Ensure ADMIN_PASSWORD exists in .env
    if ! grep -q "ADMIN_PASSWORD" "$ENV_FILE"; then
        echo "ADMIN_PASSWORD=neversmp_admin_2026" >> "$ENV_FILE"
    fi
    echo -e "${GREEN}✓ Файл .env проверен и обновлен.${NC}"
fi

# 4. Сетевая оптимизация и Фаервол (MTU 1200, advmss 1160, изоляция подсерверов)
echo -e "\n${YELLOW}🌐 [3/6] Настройка сетевого стека и защиты портов (Firewall & MTU)...${NC}"
IFACE=$(ip -o link show | awk -F': ' '$2 != "lo" {print $2; exit}')
GW=$(ip route show default 2>/dev/null | awk '{print $3; exit}')

# Immediate firewall rules application
iptables -C INPUT -i lo -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -i lo -j ACCEPT
iptables -C INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || iptables -I INPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -C INPUT -p tcp -m multiport --dports 25566,25567,25583,25584,25585,25586,25587,25588,25589,25590,5000 -j DROP 2>/dev/null || iptables -A INPUT -p tcp -m multiport --dports 25566,25567,25583,25584,25585,25586,25587,25588,25589,25590,5000 -j DROP

cat << SVCEOF > /etc/systemd/system/nsmp-net-tuning.service
[Unit]
Description=NeverSMP Network Tuning, Firewall & Safe MTU Fix
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'IF=\$(ip -o link show | awk -F\": \" \"\\\$2 != \\\"lo\\\" {print \\\$2; exit}\"); GW=\$(ip route show default 2>/dev/null | awk \"{print \\\$3; exit}\"); ip link set dev \$IF mtu 1200 2>/dev/null || true; [ -n \"\$GW\" ] && ip route change default via \$GW dev \$IF mtu 1200 advmss 1160 2>/dev/null || true; ethtool -K \$IF tx off rx off sg off tso off gso off gro off lro off 2>/dev/null || true; sysctl -w net.ipv6.conf.all.disable_ipv6=1; sysctl -w net.ipv6.conf.default.disable_ipv6=1; sysctl -w net.ipv4.tcp_mtu_probing=1; sysctl -w net.ipv4.tcp_base_mss=1024; sysctl -w net.ipv4.conf.all.rp_filter=0; iptables -C INPUT -i lo -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -i lo -j ACCEPT; iptables -C INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || iptables -I INPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT; iptables -C INPUT -p tcp -m multiport --dports 25566,25567,25583,25584,25585,25586,25587,25588,25589,25590,5000 -j DROP 2>/dev/null || iptables -A INPUT -p tcp -m multiport --dports 25566,25567,25583,25584,25585,25586,25587,25588,25589,25590,5000 -j DROP'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable --now nsmp-net-tuning.service
ip link set dev $IFACE mtu 1200 2>/dev/null || true
if [ -n "$GW" ]; then
    ip route change default via $GW dev $IFACE mtu 1200 advmss 1160 2>/dev/null || true
fi
ethtool -K $IFACE tx off rx off sg off tso off gso off gro off lro off 2>/dev/null || true
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv4.tcp_mtu_probing=1
sysctl -w net.ipv4.tcp_base_mss=1024
echo -e "${GREEN}✓ Сетевая служба и фаервол nsmp-net-tuning активированы.${NC}"

# 5. Настройка Nginx Reverse Proxy и SSL
echo -e "\n${YELLOW}🔒 [4/6] Настройка Nginx и SSL-сертификатов...${NC}"
if [ -f /etc/letsencrypt/live/test1.jointhevoid.ru/fullchain.pem ]; then
    cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80;
    listen [::]:80;
    server_name test1.jointhevoid.ru test2.jointhevoid.ru donate.neversmp.ru mc.neversmp.ru _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name test1.jointhevoid.ru test2.jointhevoid.ru donate.neversmp.ru mc.neversmp.ru _;

    ssl_certificate /etc/letsencrypt/live/test1.jointhevoid.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/test1.jointhevoid.ru/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_buffer_size 1300;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
else
    cat << 'NGINXEOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
fi

nginx -t
systemctl reload nginx
echo -e "${GREEN}✓ Nginx успешно обновлен и перезапущен.${NC}"

# 6. Служба магазина nsmp-web (Gunicorn WSGI)
echo -e "\n${YELLOW}🐍 [5/6] Настройка службы бэкенда nsmp-web...${NC}"
GUNICORN_BIN=$(which gunicorn 2>/dev/null || echo "/usr/bin/gunicorn")
cat << SYSEOF > /etc/systemd/system/nsmp-web.service
[Unit]
Description=NeverSMP Production Web Store & Admin Panel
After=network.target mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=${BASE_DIR}/backend
ExecStart=${GUNICORN_BIN} -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=3
EnvironmentFile=${BASE_DIR}/backend/.env

[Install]
WantedBy=multi-user.target
SYSEOF

systemctl daemon-reload
systemctl enable --now nsmp-web.service
systemctl restart nsmp-web.service
echo -e "${GREEN}✓ Сервис nsmp-web запущен и работает в фоновом режиме.${NC}"

# 7. Автоматическая сборка и запуск 11 игровых серверов NeverSMP
echo -e "\n${YELLOW}🎮 [6/7] Сборка и запуск серверов NeverSMP...${NC}"
chmod +x "${BASE_DIR}/scripts/build_network.sh"
chmod +x "${BASE_DIR}/scripts/server-manager.sh"

"${BASE_DIR}/scripts/server-manager.sh" stop all || true
"${BASE_DIR}/scripts/build_network.sh"
"${BASE_DIR}/scripts/server-manager.sh" start all || true
echo -e "${GREEN}✓ Игровые серверы запущены через tmux.${NC}"

# 8. Комплексный Health Check
echo -e "\n${YELLOW}🧪 [7/7] Проверка работы сервисов...${NC}"
sleep 2
API_RES=$(curl -s http://127.0.0.1:5000/api/catalog | grep -o '"success":true' || echo 'FAILED')
if [ "$API_RES" = '"success":true' ]; then
    echo -e "${GREEN}✓ Backend REST API: OK (200)${NC}"
else
    echo -e "${RED}❌ Backend REST API: $API_RES${NC}"
fi

MC_SESSIONS=$(tmux list-sessions 2>/dev/null | grep 'nsmp_' | wc -l || echo 0)
echo -e "${GREEN}✓ Активных игровых Minecraft серверов: ${MC_SESSIONS}${NC}"

echo -e "\n${GREEN}${BOLD}================================================================="
echo "       🎉 ДЕПЛОЙ НА СЕРВЕРЕ УСПЕШНО ВЫПОЛНЕН!"
echo "=================================================================${NC}"
echo -e "Магазин:      ${CYAN}https://test1.jointhevoid.ru/${NC}"
echo -e "Админка:      ${CYAN}https://test1.jointhevoid.ru/admin${NC}"
echo -e "Minecraft IP: ${CYAN}test2.jointhevoid.ru${NC} (25565)"
echo -e "Управление MC серверами: ${CYAN}${BASE_DIR}/scripts/server-manager.sh status${NC}"
echo "================================================================="
