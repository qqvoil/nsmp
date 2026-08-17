import glob
import re

config_replacements = {
    # Replace my previous cringe header
    r'      header:\n        - ""\n        - " &#aa00aa&l\* &f&lNeverSMP &#aa00aa&l\*"\n        - "  &#e056fdВыживание & Анархия  "\n        - ""\n        - " &fОнлайн: &#aa00aa%online% &8\| &fТПС: &#aa00aa%tps%"\n        - ""': 
    '      header:\n        - ""\n        - " &#e056fd&lNeverSMP "\n        - " &7Анархия и Выживание "\n        - ""\n        - " &8&m                                                  "\n        - " &fОнлайн: &#aa00aa%online% &8| &fТПС: &#aa00aa%tps%"\n        - " &8&m                                                  "\n        - ""',
    
    # Replace my previous cringe footer
    r'      footer:\n        - ""\n        - " &#aa00aa&lМЫ В СЕТИ:"\n        - " &fСайт: &#e056fddonate.neversmp.ru"\n        - " &fТГК: &#e056fdt.me/NeverSMP"\n        - ""':
    '      footer:\n        - ""\n        - " &8&m                                                  "\n        - " &fСайт: &#e056fddonate.neversmp.ru"\n        - " &fТГК: &#e056fdt.me/NeverSMP"\n        - " &8&m                                                  "\n        - ""'
}

config_files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/TAB/config.yml')
for f in config_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    for old, new in config_replacements.items():
        content = re.sub(old, new, content)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Cleaned up TAB layout.")
