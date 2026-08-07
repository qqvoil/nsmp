#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Automated World Backup Script
# ==============================================================================

set -e

BACKUP_DIR="${HOME}/data/backups"
SERVER_ROOT="${HOME}/data/server"
DATE_STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
BACKUP_ARCHIVE="${BACKUP_DIR}/nsmp_backup_${DATE_STAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting NeverSMP world backups..."

# Find all world directories across all backend servers
WORLD_DIRS=()
for srv in lobby smp1 smp2 hardcore1 hardcore2 anarchy1 anarchy2 building1 building2; do
    if [ -d "${SERVER_ROOT}/${srv}" ]; then
        for w in world world_nether world_the_end; do
            if [ -d "${SERVER_ROOT}/${srv}/${w}" ]; then
                WORLD_DIRS+=("-C" "${SERVER_ROOT}/${srv}" "${w}")
            fi
        done
    fi
done

if [ ${#WORLD_DIRS[@]} -gt 0 ]; then
    tar -czf "${BACKUP_ARCHIVE}" "${WORLD_DIRS[@]}" 2>/dev/null || true
    echo "[$(date)] Backup completed: ${BACKUP_ARCHIVE} ($(du -h "${BACKUP_ARCHIVE}" | cut -f1))"
else
    echo "[-] No world directories found to backup."
fi

# Rotate backups: delete backups older than 7 days
find "${BACKUP_DIR}" -type f -name "nsmp_backup_*.tar.gz" -mtime +7 -delete

echo "[$(date)] Backup retention cleanup completed."
