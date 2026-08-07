#!/usr/bin/env python3
import os
import shutil
import tarfile

SRC = "/Users/voil/Downloads/server"
DST = "/Users/voil/data/nsmp/core"

def clean_copy_tree(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        # Filter out junk and heavy directories
        dirs[:] = [d for d in dirs if d not in [
            'libraries', 'cache', 'versions', '.paper-remapped', 'logs', 
            'crash-reports', 'playerdata', 'stats', 'advancements', '.git',
            'world', 'world_nether', 'world_the_end'
        ]]
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path) if rel_path != '.' else dst_dir
        os.makedirs(target_root, exist_ok=True)
        
        for f in files:
            if f.endswith('.jar') or f.endswith('.log') or f in ['session.lock', 'uid.dat', '.DS_Store', '.console_history']:
                continue
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_root, f)
            shutil.copy2(src_file, dst_file)

def collect_plugins():
    pool_dir = os.path.join(DST, "plugins_pool")
    os.makedirs(pool_dir, exist_ok=True)
    # Only copy JARs directly in <server>/plugins/ (not in subdirectories like .paper-remapped)
    for srv in os.listdir(SRC):
        plugins_dir = os.path.join(SRC, srv, "plugins")
        if os.path.isdir(plugins_dir):
            for f in os.listdir(plugins_dir):
                if f.endswith('.jar') and os.path.isfile(os.path.join(plugins_dir, f)):
                    shutil.copy2(os.path.join(plugins_dir, f), os.path.join(pool_dir, f))
    print(f"✓ Collected unique plugins to {pool_dir}")

def compress_map(src_world, dst_tar_gz):
    if not os.path.exists(src_world):
        return
    os.makedirs(os.path.dirname(dst_tar_gz), exist_ok=True)
    print(f"📦 Compressing world {src_world} -> {dst_tar_gz}...")
    with tarfile.open(dst_tar_gz, "w:gz") as tar:
        for item in os.listdir(src_world):
            if item in ['playerdata', 'stats', 'advancements', 'session.lock', 'uid.dat']:
                continue
            item_path = os.path.join(src_world, item)
            tar.add(item_path, arcname=item)
    print(f"✓ Created {dst_tar_gz} ({os.path.getsize(dst_tar_gz) / (1024*1024):.2f} MB)")

def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)
    os.makedirs(DST, exist_ok=True)
    
    # 1. Collect templates (configs only, no world files)
    for srv in ['Limbo', 'Lobby', 'SMP1', 'anarchy1', 'hardcore1', 'building1', 'velocity']:
        template_name = srv
        if srv == 'SMP1': template_name = 'SMP'
        clean_copy_tree(os.path.join(SRC, srv), os.path.join(DST, "templates", template_name))
        print(f"✓ Extracted clean configs for {template_name}")
        
    # 2. Collect plugins pool
    collect_plugins()
    
    # 3. Compress maps cleanly
    compress_map(os.path.join(SRC, "Lobby", "world"), os.path.join(DST, "maps", "lobby_world.tar.gz"))
    compress_map(os.path.join(SRC, "building1", "world"), os.path.join(DST, "maps", "building_world.tar.gz"))
    compress_map(os.path.join(SRC, "hardcore1", "world"), os.path.join(DST, "maps", "hardcore_world.tar.gz"))

if __name__ == "__main__":
    main()
