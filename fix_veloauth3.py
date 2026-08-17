import re

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '=' in line and not line.startswith('#'):
        key, val = line.split('=', 1)
        val = val.strip()
        
        # Replace & with native section sign
        val = val.replace('&5&l! &f', '§5§l! §f')
        
        new_lines.append(f"{key}={val}\n")
    else:
        new_lines.append(line)

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed VeloAuth native format.")
