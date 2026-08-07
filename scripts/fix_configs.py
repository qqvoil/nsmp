#!/usr/bin/env python3
"""
NeverSMP Server Config & Cleanup Automator
Fixes port collisions, RCON settings, simulation distances, removes duplicate plugins,
and scaffolds anarchy1 and anarchy2 servers.
"""

import os
import shutil
import re

DOWNLOADS_SERVER_DIR = os.path.expanduser("~/Downloads/server")

PORT_MAPPING = {
    "Lobby": {"port": 25566, "rcon": 25575, "hardcore": "false", "whitelist": "false"},
    "SMP1": {"port": 25590, "rcon": 25576, "hardcore": "false", "whitelist": "false"},
    "SMP2": {"port": 25587, "rcon": 25577, "hardcore": "false", "whitelist": "false"},
    "hardcore1": {"port": 25589, "rcon": 25578, "hardcore": "true", "whitelist": "false"},
    "hardcore2": {"port": 25586, "rcon": 25579, "hardcore": "true", "whitelist": "false"},
    "anarchy1": {"port": 25588, "rcon": 25580, "hardcore": "false", "whitelist": "false"},
    "anarchy2": {"port": 25585, "rcon": 25581, "hardcore": "false", "whitelist": "false"},
    "building1": {"port": 25583, "rcon": 25582, "hardcore": "false", "whitelist": "false"},
    "building2": {"port": 25584, "rcon": 25583, "hardcore": "false", "whitelist": "false"},
}

JUNK_PLUGINS = [
    "CommandVisibilityPlugin",
    "CommandVisibilityPlugin-1.20.1.jar",
    "HideTab",
    "HideTab.jar",
    "NoPlugins",
    "noplugins-1.2.0.jar",
    "sph-1.0.1.jar",
    "SimplePluginHider",
    "Geyser-Spigot"
]

def clean_plugins(plugins_dir: str):
    if not os.path.isdir(plugins_dir):
        return
    for item in os.listdir(plugins_dir):
        item_path = os.path.join(plugins_dir, item)
        if any(junk.lower() in item.lower() for junk in JUNK_PLUGINS):
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)
            else:
                os.remove(item_path)
            print(f"  🗑 Удален мусорный плагин: {item}")

def update_server_properties(srv_dir: str, config: dict):
    prop_path = os.path.join(srv_dir, "server.properties")
    if not os.path.exists(prop_path):
        return

    with open(prop_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Update port
    content = re.sub(r"^server-port=.*$", f"server-port={config['port']}", content, flags=re.M)
    # Update rcon port
    content = re.sub(r"^rcon\.port=.*$", f"rcon.port={config['rcon']}", content, flags=re.M)
    # Update hardcore
    content = re.sub(r"^hardcore=.*$", f"hardcore={config['hardcore']}", content, flags=re.M)
    # Update whitelist
    content = re.sub(r"^white-list=.*$", f"white-list={config['whitelist']}", content, flags=re.M)
    # Optimize simulation and view distances
    content = re.sub(r"^simulation-distance=.*$", "simulation-distance=6", content, flags=re.M)
    content = re.sub(r"^view-distance=.*$", "view-distance=10", content, flags=re.M)
    content = re.sub(r"^network-compression-threshold=.*$", "network-compression-threshold=-1", content, flags=re.M)

    with open(prop_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ Обновлен server.properties (Port: {config['port']}, RCON: {config['rcon']}, Hardcore: {config['hardcore']}, WL: {config['whitelist']})")

def setup_anarchy_server(source_dir: str, target_dir: str, config: dict):
    if not os.path.exists(target_dir):
        print(f"📦 Создание сервера {os.path.basename(target_dir)} из шаблона...")
        shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns("logs", "crash-reports", "world*", "cache"))
    update_server_properties(target_dir, config)
    clean_plugins(os.path.join(target_dir, "plugins"))

def main():
    root = DOWNLOADS_SERVER_DIR
    if not os.path.isdir(root):
        print(f"Каталог {root} не найден!")
        return

    print(f"🛠 Начало комплексной оптимизации NeverSMP в {root}...\n")

    # 1. Fix existing servers
    for srv_name, conf in PORT_MAPPING.items():
        srv_path = os.path.join(root, srv_name)
        if os.path.isdir(srv_path):
            print(f"🔧 Настройка сервера: {srv_name}")
            update_server_properties(srv_path, conf)
            clean_plugins(os.path.join(srv_path, "plugins"))

    # 2. Scaffold Anarchy 1 and 2 if missing
    smp_template = os.path.join(root, "SMP1")
    if os.path.isdir(smp_template):
        anarchy1_dir = os.path.join(root, "anarchy1")
        anarchy2_dir = os.path.join(root, "anarchy2")
        setup_anarchy_server(smp_template, anarchy1_dir, PORT_MAPPING["anarchy1"])
        setup_anarchy_server(smp_template, anarchy2_dir, PORT_MAPPING["anarchy2"])

    print("\n🎉 Все сервера NeverSMP успешно оптимизированы и готовы к запуску на дедике!")

if __name__ == "__main__":
    main()
