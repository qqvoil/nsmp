#!/bin/bash
/Users/voil/data/nsmp/scripts/remote_exec.sh "cat << 'INNER' > /etc/systemd/system/nsmp-net-tuning.service
[Unit]
Description=NeverSMP Network Card Offload and Checksum Fix
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'ethtool -K enp5s0 tx off rx off sg off tso off gso off gro off lro off'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
INNER
systemctl daemon-reload && systemctl restart nsmp-net-tuning"
