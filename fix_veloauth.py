import re

PREFIX = "<#aa00aa><bold>!</bold></#aa00aa> <white>"

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '=' in line and not line.startswith('#'):
        key, val = line.split('=', 1)
        val = val.strip()
        # Remove old broken legacy codes
        val = val.replace('&#aa00aa&l! &f', '')
        
        # Inject MiniMessage prefix for everything to override internal colors
        new_val = f"{PREFIX}{val}</white>"
        new_lines.append(f"{key}={new_val}\n")
    else:
        new_lines.append(line)

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed VeloAuth MiniMessage format.")
