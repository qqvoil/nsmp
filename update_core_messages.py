import glob
import re

PREFIX = "&#aa00aa&l! &f"

def update_spigot():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/spigot.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = re.sub(r'unknown-command:.*', f'unknown-command: "{PREFIX}Неизвестная команда. Введите &#e056fd/help"', content)
        content = re.sub(r'server-full:.*', f'server-full: "{PREFIX}Сервер переполнен!"', content)
        content = re.sub(r'whitelist:.*', f'whitelist: "{PREFIX}Вы не добавлены в вайтлист сервера!"', content)
        content = re.sub(r'outdated-client:.*', f'outdated-client: "{PREFIX}Устаревший клиент! Пожалуйста, используйте &#e056fd{{0}}"', content)
        content = re.sub(r'outdated-server:.*', f'outdated-server: "{PREFIX}Сервер находится на версии &#e056fd{{0}}"', content)
        content = re.sub(r'restart:.*', f'restart: "{PREFIX}Сервер перезапускается..."', content)

        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
def update_paper():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/config/paper-global.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = re.sub(
            r'no-permission: .*(\n\s+.*)?', 
            f'no-permission: "{PREFIX}У вас нет прав на использование этой команды."', 
            content
        )
        content = re.sub(
            r'connection-throttle: .*', 
            f'connection-throttle: "{PREFIX}Слишком частые подключения! Пожалуйста, подождите."', 
            content
        )
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

update_spigot()
update_paper()
print("Updated Spigot & Paper messages globally.")
