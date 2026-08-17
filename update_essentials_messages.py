import re
import glob
import shutil

with open('/Users/voil/data/nsmp/messages_ru.properties', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<dark_red>', '&#aa00aa&l! &f')
content = content.replace('<red>', '&#aa00aa')
content = content.replace('<yellow>', '&#e056fd')
content = content.replace('<green>', '&f')
content = content.replace('<gold>', '&#aa00aa')
content = content.replace('<primary>', '&#e056fd')
content = content.replace('<secondary>', '&#aa00aa')
content = content.replace('<dark_aqua>', '&#aa00aa')

# For things that were previously "errorWithMessage=\u00a7cОшибка: \u00a74{0}" etc (just in case they used legacy codes)
content = content.replace('\u00a74', '&#aa00aa&l! &f')
content = content.replace('\u00a7c', '&#aa00aa')
content = content.replace('\u00a76', '&#e056fd')

# Let's fix up multiple "!" if they happen
content = content.replace('&#aa00aa&l! &f&#aa00aa&l! &f', '&#aa00aa&l! &f')

# Save it to a modified file
with open('/Users/voil/data/nsmp/messages_ru_modified.properties', 'w', encoding='utf-8') as f:
    f.write(content)

# Copy to all templates
templates = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/Essentials')
for t in templates:
    shutil.copy('/Users/voil/data/nsmp/messages_ru_modified.properties', f"{t}/messages_ru.properties")

print("Updated Essentials messages globally.")
