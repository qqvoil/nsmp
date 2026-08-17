import re

PREFIX = "&5&l! &f"

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '=' in line and not line.startswith('#'):
        key, val = line.split('=', 1)
        val = val.strip()
        # Remove old broken MiniMessage and Hex tags
        val = val.replace('<#aa00aa><bold>!</bold></#aa00aa> <white>', '')
        val = val.replace('</white>', '')
        val = val.replace('&#aa00aa&l! &f', '')
        
        # Inject standard legacy format
        new_val = f"{PREFIX}{val}"
        new_lines.append(f"{key}={new_val}\n")
    else:
        new_lines.append(line)

with open('/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed VeloAuth legacy format.")
