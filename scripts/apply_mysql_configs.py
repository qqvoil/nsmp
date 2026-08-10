#!/usr/bin/env python3
"""
NeverSMP — Automated MySQL Configurator for LuckPerms & Plugins
Switches all backend servers to unified MariaDB storage with real-time SQL messaging.
"""

import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER_ROOT = os.path.join(BASE_DIR, "server")

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
    
    # Velocity uses luckperms.conf, Bukkit uses config.yml
    is_velocity = (srv_name == "velocity")
    config_name = "luckperms.conf" if is_velocity else "config.yml"
    config_path = os.path.join(lp_dir, config_name)
    
    if not os.path.exists(config_path):
        if is_velocity:
            print(f"[*] Creating default LuckPerms MySQL config for Velocity...")
            os.makedirs(lp_dir, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(f'''server="{srv_name}"
storage-method="MySQL"
data {{
  address="{DB_CONFIG['host']}"
  database="{DB_CONFIG['database']}"
  username="{DB_CONFIG['username']}"
  password="{DB_CONFIG['password']}"
  table-prefix="{DB_CONFIG['table_prefix']}"
}}
messaging-service="sql"
''')
            print(f"[+] Created Velocity LuckPerms config: {srv_name}")
            return
        else:
            print(f"[-] LuckPerms config not found on {srv_name} (will be created on first start)")
            return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update storage-method to MySQL
    content = re.sub(r'storage-method:\s*["\']?\w+["\']?', 'storage-method: "MySQL"', content)
    content = re.sub(r'storage-method="?\w+"?', 'storage-method="MySQL"', content)
    
    # 2. Update messaging service to sql for instant cross-server updates
    content = re.sub(r'messaging-service:\s*["\']?\w+["\']?', 'messaging-service: "sql"', content)
    content = re.sub(r'messaging-service="?\w+"?', 'messaging-service="sql"', content)
    
    # 3. Update server name tag in LuckPerms
    content = re.sub(r'server:\s*["\']?\w+["\']?', f'server: "{srv_name}"', content)
    content = re.sub(r'server="?\w+"?', f'server="{srv_name}"', content)

    # 4. Update data block address, database, username, password, table-prefix
    content = re.sub(r'address:\s*["\']?[^"\']+["\']?', f'address: "{DB_CONFIG["host"]}"', content, count=1)
    content = re.sub(r'address="?[^"\']+"?', f'address="{DB_CONFIG["host"]}"', content, count=1)
    
    content = re.sub(r'database:\s*["\']?[^"\']+["\']?', f'database: "{DB_CONFIG["database"]}"', content, count=1)
    content = re.sub(r'database="?[^"\']+"?', f'database="{DB_CONFIG["database"]}"', content, count=1)
    
    content = re.sub(r'username:\s*["\']?[^"\']+["\']?', f'username: "{DB_CONFIG["username"]}"', content, count=1)
    content = re.sub(r'username="?[^"\']+"?', f'username="{DB_CONFIG["username"]}"', content, count=1)
    
    content = re.sub(r'password:\s*["\']?[^"\']*["\']?', f'password: "{DB_CONFIG["password"]}"', content, count=1)
    content = re.sub(r'password="?[^"\']*"?', f'password="{DB_CONFIG["password"]}"', content, count=1)
    
    content = re.sub(r'table-prefix:\s*["\']?[^"\']*["\']?', f'table-prefix: "{DB_CONFIG["table_prefix"]}"', content, count=1)
    content = re.sub(r'table-prefix="?[^"\']*"?', f'table-prefix="{DB_CONFIG["table_prefix"]}"', content, count=1)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Updated LuckPerms MySQL config for: {srv_name}")

def update_playerpoints_config(server_dir: str, srv_name: str):
    pp_dir = os.path.join(server_dir, "plugins", "PlayerPoints")
    config_path = os.path.join(pp_dir, "config.yml")
    
    if not os.path.exists(config_path):
        # Velocity usually doesn't have PlayerPoints
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We need to enable mysql and set connection details
    # The config format looks like:
    # mysql-settings:
    #   enabled: false
    #   hostname: 127.0.0.1
    #   port: 3306
    #   database-name: ''
    #   user-name: ''
    #   user-password: ''

    # Strip port from host for hostname, or parse it
    db_host = DB_CONFIG["host"].split(":")[0]
    db_port = "3306"
    if ":" in DB_CONFIG["host"]:
        db_port = DB_CONFIG["host"].split(":")[1]

    # Regex replacements
    # 1. Enable MySQL
    content = re.sub(r'enabled:\s*false', 'enabled: true', content, count=1)
    
    # 2. Update credentials in mysql-settings block
    content = re.sub(r'hostname:\s*[\'"]?[\w\.]+[\'"]?', f'hostname: {db_host}', content)
    content = re.sub(r'port:\s*\d+', f'port: {db_port}', content)
    content = re.sub(r'database-name:\s*[\'"]?[\w]*[\'"]?', f'database-name: {DB_CONFIG["database"]}', content)
    content = re.sub(r'user-name:\s*[\'"]?[\w]*[\'"]?', f'user-name: {DB_CONFIG["username"]}', content)
    content = re.sub(r'user-password:\s*[\'"]?[\w]*[\'"]?', f'user-password: {DB_CONFIG["password"]}', content)
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Updated PlayerPoints MySQL config for: {srv_name}")

def main():
    print("==================================================")
    print("⚔ NeverSMP — Применение настроек централизованной БД")
    print("==================================================")
    
    for srv in SERVERS:
        srv_dir = os.path.join(SERVER_ROOT, srv)
        if os.path.isdir(srv_dir):
            update_luckperms_config(srv_dir, srv)
            update_playerpoints_config(srv_dir, srv)
        else:
            print(f"[-] Directory {srv} not found, skipping.")
            
    print("==================================================")
    print("✅ Конфигурации LuckPerms и PlayerPoints переведены на единую MariaDB!")

if __name__ == "__main__":
    main()
