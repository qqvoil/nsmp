import os

blocks = [
    ("iron_block", 2),
    ("gold_block", 3),
    ("diamond_block", 5),
    ("emerald_block", 7),
    ("diamond_ore", 10),
    ("emerald_ore", 15),
    ("deepslate_emerald_ore", 20),
]

os.makedirs("/Users/voil/data/nsmp/core/templates/SMP/plugins/ProtectionStones/blocks", exist_ok=True)

template = """
# name of block (must be unique)
type = "{block_type}"
# block type/alias (can be multiple for the same type of PS region)
aliases = ["{block_type}"]

# Set whether this block should be allowed to be placed without creating a region.
# Only players with the permission 'protectionstones.allow_place_unprotected' will be able to do this.
restrict_obtaining = false

[region]
# size of the region from the protection block
radius_x = {radius}
radius_y = {radius}
radius_z = {radius}

# Flags to set on the region by default
# For WorldGuard 7+ (1.13+), you can use placeholders %player% and %uuid%
flags = [
    "pvp deny",
    "greeting &aВы вошли в регион &e%player%",
    "farewell &cВы покинули регион &e%player%",
    "creeper-explosion deny",
    "tnt deny",
    "build deny",
    "interact deny"
]

# Set the maximum number of regions this block can create
# Set to -1 for unlimited
max_regions = -1

[block_data]
display_name = "&bПриват {radius}x{radius}x{radius}"
lore = [
    "&7Поставьте этот блок на землю,",
    "&7чтобы заприватить территорию!"
]
"""

for block_type, radius in blocks:
    content = template.format(block_type=block_type, radius=radius)
    with open(f"/Users/voil/data/nsmp/core/templates/SMP/plugins/ProtectionStones/blocks/{block_type}.toml", "w", encoding="utf-8") as f:
        f.write(content.strip())
