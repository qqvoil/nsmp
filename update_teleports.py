import glob
import re

PREFIX_TPA = "&#aa00aa&lTPA &8»"
PREFIX_ERR = "&#aa00aa&l! &f"

def update_simpletpa():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/SimpleTPA/config.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace prefix
        content = content.replace("§8[§dTPA§8]", PREFIX_TPA)
        
        # Make the [ACCEPT] / [DENY] buttons prettier
        content = content.replace('accept_text: "\\n[✔ ПРИНЯТЬ]"', 'accept_text: "\\n&#aa00aa[<green>✔ ПРИНЯТЬ&#aa00aa]"')
        content = content.replace('deny_text: " [✖ ОТКЛОНИТЬ]"', 'deny_text: " &#aa00aa[<red>✖ ОТКЛОНИТЬ&#aa00aa]"')

        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

def update_advancedrtp():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/AdvancedRTP/config.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Cooldown message
        content = re.sub(
            r'message: "&cПодождите \{time\} сек. перед следующим использованием RTP!"',
            f'message: "{PREFIX_ERR}Подождите &#e056fd{{time}} сек&f. перед следующим использованием RTP!"',
            content
        )
        
        # Messages block
        content = re.sub(r'success: "&aВы успешно телепортированы в случайную точку мира!"', f'success: "{PREFIX_ERR}Вы успешно телепортированы в случайную точку!"', content)
        content = re.sub(r'no-safe-location: "&cНе удалось найти безопасное место.*"', f'no-safe-location: "{PREFIX_ERR}Не удалось найти безопасное место. Попробуйте еще раз."', content)
        content = re.sub(r'world-not-found: "&cМир не найден или запрещен для RTP."', f'world-not-found: "{PREFIX_ERR}Мир не найден или запрещен для RTP."', content)
        content = re.sub(r'no-permission: "&cУ вас нет прав для использования этой команды."', f'no-permission: "{PREFIX_ERR}У вас нет прав для использования этой команды."', content)
        content = re.sub(r'invalid-command: "&cНеверное использование.*"', f'invalid-command: "{PREFIX_ERR}Неверное использование. /rtp"', content)
        content = re.sub(r'teleport-start: "&eТелепортация через \{time\} сек\.\.\. Не двигайтесь!"', f'teleport-start: "{PREFIX_ERR}Телепортация через &#e056fd{{time}} сек&f... Не двигайтесь!"', content)
        content = re.sub(r'teleport-cancelled: "&cТелепортация отменена! Вы пошевелились."', f'teleport-cancelled: "{PREFIX_ERR}Телепортация отменена, вы пошевелились!"', content)

        # Titles
        content = re.sub(r'teleport-countdown-title: "&6&lТелепортация\.\.\."', r'teleport-countdown-title: "&#aa00aa&lТелепортация..."', content)
        content = re.sub(r'teleport-countdown-subtitle: "&eНе двигайтесь \{time\} сек\.!"', r'teleport-countdown-subtitle: "&fНе двигайтесь &#e056fd{time} сек&f!"', content)
        content = re.sub(r'teleport-cancelled-title: "&c&lОтменено"', r'teleport-cancelled-title: "&#aa00aa&lОтменено"', content)
        content = re.sub(r'teleport-cancelled-subtitle: "&cВы сдвинулись с места!"', r'teleport-cancelled-subtitle: "&fВы сдвинулись с места!"', content)

        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

update_simpletpa()
update_advancedrtp()
print("Updated SimpleTPA and AdvancedRTP globally.")
