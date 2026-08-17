import glob
import re

files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/DeluxeMenus/gui_menus/*.yml')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the green [message] with purple
    content = re.sub(
        r"\[message\] &aПодключение к серверу",
        r"[message] &#aa00aa&l! &fПодключение к серверу",
        content
    )
    # Just in case they used single quotes or anything
    content = re.sub(
        r"\[message\] '&aПодключение к серверу",
        r"[message] '&#aa00aa&l! &fПодключение к серверу",
        content
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Updated DM connection messages.")
