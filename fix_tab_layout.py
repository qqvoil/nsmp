import glob
import re
import os

config_replacements = {
    # Replace old header
    r'      header:\n        - " &8✗ &#aa00aa&lN&#9224b6&le&#7949c2&lv&#616dce&le&#4992db&lr&#31b6e7&lS&#18dbf3&lM&#00ffff&lP &8✗"\n        - ""\n        - " &fОнлайн: &#aa00aa%online% &f\| TPS: &#aa00aa%tps%"\n        - " &fИгроки на сервере:"\n        - ""': 
    '      header:\n        - ""\n        - " &#aa00aa&l* &f&lNeverSMP &#aa00aa&l*"\n        - "  &#e056fdВыживание & Анархия  "\n        - ""\n        - " &fОнлайн: &#aa00aa%online% &8| &fТПС: &#aa00aa%tps%"\n        - ""',
    
    # Replace old footer
    r'      footer:\n        - ""\n        - " &fНаш сайт: &#00ffffdonate.neversmp.ru"\n        - " &fНаш тгк: &#00fffft.me/NeverSMP"':
    '      footer:\n        - ""\n        - " &#aa00aa&lМЫ В СЕТИ:"\n        - " &fСайт: &#e056fddonate.neversmp.ru"\n        - " &fТГК: &#e056fdt.me/NeverSMP"\n        - ""'
}

config_files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/TAB/config.yml')
for f in config_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    for old, new in config_replacements.items():
        content = re.sub(old, new, content)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

groups_content = """# NeverSMP Tab Groups
owner:
  tabprefix: "&8[&4&lВЛАДЕЛЕЦ&8] &4"
  tagprefix: "&8[&4&lВЛАДЕЛЕЦ&8] &4"
admin:
  tabprefix: "&8[&#aa00aa&lАДМИН&8] &#e056fd"
  tagprefix: "&8[&#aa00aa&lАДМИН&8] &#e056fd"
moder:
  tabprefix: "&8[&9&lМОДЕР&8] &9"
  tagprefix: "&8[&9&lМОДЕР&8] &9"
vip:
  tabprefix: "&8[&#e056fd&lVIP&8] &#e056fd"
  tagprefix: "&8[&#e056fd&lVIP&8] &#e056fd"
default:
  tabprefix: "&8[&7Игрок&8] &f"
  tagprefix: "&8[&7Игрок&8] &f"

_DEFAULT_:
  tabprefix: "&8[&7Игрок&8] &f"
  tagprefix: "&8[&7Игрок&8] &f"
  customtabname: "%player%"
  tabsuffix: "%luckperms-suffix%"
  tagsuffix: "%luckperms-suffix%"
"""

groups_files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/TAB/groups.yml')
for f in groups_files:
    with open(f, 'w', encoding='utf-8') as file:
        file.write(groups_content)

print("Updated TAB config layout and groups.")
