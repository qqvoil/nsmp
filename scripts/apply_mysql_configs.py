#!/usr/bin/env python3
"""
NeverSMP — Automated MySQL Configurator for LuckPerms & Plugins
Switches all backend servers to unified MariaDB storage with real-time SQL messaging.
"""

import os
import re

SERVER_ROOT = os.path.expanduser("~/data/server")

SERVERS = [
    "lobby", "smp1", "smp2", "hardcore1", "hardcore2", 
    "anarchy1", "anarchy2", "building1", "building2", "velocity"
]

DB_CONFIG = {
    "host": os.environ.get("NSMP_DB_HOST", "127.0.0.1:3306"),
    "database": os.environ.get("NSMP_DB_NAME", "neversmp"),
    "username": os.environ.get("NSMP_DB_USER", "nsmp_user"),
    "password": os.environ.get("NSMP_DB_PASSWORD", "YOUR_MYSQL_PASSWORD_HERE"),
    "table_prefix": "lp_"
}

def update_luckperms_config(server_dir: str, srv_name: str):
    lp_dir = os.path.join(server_dir, "plugins", "LuckPerms")
    config_path = os.path.join(lp_dir, "config.yml")
    
    if not os.path.exists(config_path):
        print(f"[-] LuckPerms config not found on {srv_name} (will be created on first start)")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update storage-method to MySQL
    content = re.sub(r'storage-method:\s*["\']?\w+["\']?', 'storage-method: "MySQL"', content)
    
    # 2. Update messaging service to sql for instant cross-server updates
    content = re.sub(r'messaging-service:\s*["\']?\w+["\']?', 'messaging-service: "sql"', content)
    
    # 3. Update server name tag in LuckPerms
    content = re.sub(r'server:\s*["\']?\w+["\']?', f'server: "{srv_name}"', content)

    # 4. Update data block address, database, username, password, table-prefix
    content = re.sub(r'address:\s*["\']?[^"\']+["\']?', f'address: "{DB_CONFIG["host"]}"', content, count=1)
    content = re.sub(r'database:\s*["\']?[^"\']+["\']?', f'database: "{DB_CONFIG["database"]}"', content, count=1)
    content = re.sub(r'username:\s*["\']?[^"\']+["\']?', f'username: "{DB_CONFIG["username"]}"', content, count=1)
    content = re.sub(r'password:\s*["\']?[^"\']*["\']?', f'password: "{DB_CONFIG["password"]}"', content, count=1)
    content = re.sub(r'table-prefix:\s*["\']?[^"\']*["\']?', f'table-prefix: "{DB_CONFIG["table_prefix"]}"', content, count=1)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Updated LuckPerms MySQL config for: {srv_name}")

def main():
    print("==================================================")
    print("⚔ NeverSMP — Применение настроек централизованной БД")
    print("==================================================")
    
    for srv in SERVERS:
        srv_dir = os.path.join(SERVER_ROOT, srv)
        if os.path.isdir(srv_dir):
            update_luckperms_config(srv_dir, srv)
        else:
            print(f"[-] Directory {srv} not found, skipping.")
            
    print("==================================================")
    print("✅ Конфигурации LuckPerms переведены на единую MariaDB!")

if __name__ == "__main__":
    main()
