#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Crontab Installer (03:00 MSK Nightly Maintenance & Watchdog)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESTART_SCRIPT="${SCRIPT_DIR}/nightly_restart.sh"
WATCHDOG_SCRIPT="${SCRIPT_DIR}/watchdog.sh"

echo "=================================================="
echo "⚔ NeverSMP — Установка расписания Cron"
echo "=================================================="

# Make scripts executable
chmod +x "${SCRIPT_DIR}"/*.sh

# Current crontab without existing nsmp entries
CRON_TMP=$(mktemp)
crontab -l 2>/dev/null | grep -v "NeverSMP" | grep -v "${SCRIPT_DIR}" > "${CRON_TMP}" || true

# Add new entries:
# 1. Nightly restart at 03:00 MSK (Starts warning sequence at 02:49 MSK)
echo "49 2 * * * /bin/bash ${RESTART_SCRIPT} >> ${HOME}/data/nightly_restart.log 2>&1 # NeverSMP Nightly Restart" >> "${CRON_TMP}"

# 2. Watchdog every 2 minutes
echo "*/2 * * * * /bin/bash ${WATCHDOG_SCRIPT} >> ${HOME}/data/watchdog.log 2>&1 # NeverSMP Crash Watchdog" >> "${CRON_TMP}"

crontab "${CRON_TMP}"
rm -f "${CRON_TMP}"

echo "✅ Crontab успешно установлен:"
crontab -l
echo "=================================================="
