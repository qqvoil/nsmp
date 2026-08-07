#!/usr/bin/env bash
# ==============================================================================
# NeverSMP — Remote Dedicated Server Executor via Persistent SSH ControlMaster
# ==============================================================================

HOST="${NSMP_SERVER_HOST:-127.0.0.1}"
USER="${NSMP_SERVER_USER:-root}"
PASS="${NSMP_SERVER_PASS:-}"
SOCKET="/tmp/ssh-nsmp-${USER}@${HOST}:22"

CMD="$*"

if [ -z "$CMD" ]; then
    CMD="uptime"
fi

connect_master() {
    rm -f "${SOCKET}"
    SSHPASS="${PASS}" sshpass -e ssh -M -f -N \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o LogLevel=ERROR \
        -o PreferredAuthentications=password \
        -o PubkeyAuthentication=no \
        -o ConnectTimeout=10 \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o ControlPath="${SOCKET}" \
        -o ControlPersist=30m \
        "${USER}@${HOST}" 2>/dev/null
    sleep 0.5
}

for attempt in 1 2 3; do
    if ! ssh -O check -o ControlPath="${SOCKET}" "${USER}@${HOST}" 2>/dev/null; then
        connect_master
    fi

    if ssh -o ControlPath="${SOCKET}" -o LogLevel=ERROR "${USER}@${HOST}" "${CMD}"; then
        exit 0
    fi

    # If failed, clear socket and retry
    rm -f "${SOCKET}"
    sleep 1
done

exit 1
