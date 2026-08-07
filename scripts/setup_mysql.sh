#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — MariaDB Initializer & User Setup
# ==============================================================================

set -e

DB_NAME="neversmp"
DB_USER="nsmp_user"
DB_PASS="NeverSMP_SecureDB_2026!"
SCHEMA_FILE="$(dirname "$0")/../configs/database_schema.sql"

echo "=================================================="
echo "⚔ NeverSMP — Настройка централизованной БД MariaDB"
echo "=================================================="

# Check if mariadb/mysql is installed
if ! command -v mysql &> /dev/null; then
    echo "⚠️ MySQL/MariaDB клиент не найден. Установка..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y mariadb-server mariadb-client
        sudo systemctl enable --now mariadb
    else
        echo "❌ Пожалуйста, установите MariaDB сервер вручную."
        exit 1
    fi
fi

echo "📦 Создание базы данных и пользователя..."

sudo mysql -e "
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'127.0.0.1' IDENTIFIED BY '${DB_PASS}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
"

echo "📜 Импорт схемы таблиц..."
mysql -u "${DB_USER}" -p"${DB_PASS}" -h 127.0.0.1 "${DB_NAME}" < "${SCHEMA_FILE}"

echo "✅ База данных успешно инициализирована!"
echo "   Хост: 127.0.0.1:3306"
echo "   База: ${DB_NAME}"
echo "   Пользователь: ${DB_USER}"
echo "=================================================="
