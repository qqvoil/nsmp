#!/bin/bash
/Users/voil/data/nsmp/scripts/remote_exec.sh "cat << 'INNER' > /etc/systemd/system/nsmp-net-tuning.service
[Unit]
Description=NeverSMP Network Card Offload and VPN Safe MTU Fix
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'ip link set dev enp5s0 mtu 1280 && ethtool -K enp5s0 tx off rx off sg off tso off gso off gro off lro off'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
INNER
systemctl daemon-reload && systemctl restart nsmp-net-tuning"
