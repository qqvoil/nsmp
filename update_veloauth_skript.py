import glob

# VeloAuth
f = '/Users/voil/data/nsmp/core/templates/velocity/plugins/veloauth/lang/messages_ru.properties'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

content = content.replace(
    'connection.connecting=Подключение к игровому серверу...',
    'connection.connecting=&#aa00aa&l! &fПодключение к игровому серверу...'
)
content = content.replace(
    'general.welcome.full=Добро пожаловать на сервер! Приятной игры!',
    'general.welcome.full=&#aa00aa&l! &fДобро пожаловать на сервер! Приятной игры!'
)

with open(f, 'w', encoding='utf-8') as file:
    file.write(content)

# Skript
sk_files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/Skript/scripts/lobby_teleport.sk')
for sf in sk_files:
    with open(sf, 'r', encoding='utf-8') as file:
        sk_content = file.read()
    
    sk_content = sk_content.replace(
        'send "&eПодключение к главному лобби..." to player',
        'send "&#aa00aa&l! &fПодключение к главному лобби..." to player'
    )
    with open(sf, 'w', encoding='utf-8') as file:
        file.write(sk_content)

print("Updated VeloAuth and lobby_teleport.sk.")
