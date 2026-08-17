import os
import glob
import re

def update_deluxemenus():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/DeluxeMenus/gui_menus/**/*.yml', recursive=True)
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace colors in menu_title
        content = re.sub(r"menu_title: '&#5a5a5a", r"menu_title: '&#aa00aa", content)
        content = re.sub(r"menu_title: '&#000000", r"menu_title: '&#aa00aa", content)
        content = re.sub(r"menu_title: '&8", r"menu_title: '&#aa00aa", content)
        
        # Replace colors in display_name
        content = re.sub(r"display_name: '&#ffff55", r"display_name: '&#e056fd", content)
        content = re.sub(r"display_name: '&#5a5a5a", r"display_name: '&#aa00aa", content)
        content = re.sub(r"display_name: '&e", r"display_name: '&#e056fd", content)
        content = re.sub(r"display_name: '&6", r"display_name: '&#aa00aa", content)
        content = re.sub(r"display_name: '&8", r"display_name: '&#aa00aa", content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
    print("Updated DeluxeMenus configs globally.")

update_deluxemenus()
