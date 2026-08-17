import glob
import re

files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/TAB/config.yml')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Disable bossbar
    content = re.sub(
        r"bossbar:\n  enabled: true",
        r"bossbar:\n  enabled: false",
        content
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Disabled TAB bossbars to prevent UI overlap.")
