import os
import glob
import re

def update_skripts():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/Skript/scripts/anarchy_spawn.sk')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replacements for spawn teleports
        content = content.replace('send "&cВы не можете телепортироваться на спавн во время боя!" to player', 'send "&#aa00aa&l! &fВы не можете телепортироваться во время боя!" to player')
        content = content.replace('send "&aТелепортация на спавн через &e3 сек&a. Не двигайтесь!" to player', 'send "&#aa00aa&l! &fТелепортация через &#e056fd3 сек&f. Не двигайтесь!" to player')
        content = content.replace('send "&cТелепортация отменена, вы сдвинулись с места!" to player', 'send "&#aa00aa&l! &fТелепортация отменена, вы сдвинулись с места!" to player')
        content = content.replace('send "&cТелепортация отменена из-за начала боя!" to player', 'send "&#aa00aa&l! &fТелепортация отменена из-за начала боя!" to player')
        content = content.replace('send "&aВы успешно телепортированы на спавн Анархии!" to player', 'send "&#aa00aa&l! &fВы успешно телепортированы на спавн!" to player')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
    print("Updated Skripts globally.")

update_skripts()
