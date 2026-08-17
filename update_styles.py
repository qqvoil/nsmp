import os
import glob

# Style Definitions
GRADIENT_NEVERSMP = "&#aa00aa&lN&#9224b6&le&#7949c2&lv&#616dce&le&#4992db&lr&#31b6e7&lS&#18dbf3&lM&#00ffff&lP"
PURPLE = "&#aa00aa"
LIGHT_PURPLE = "&#e056fd"
CYAN = "&#00ffff"

def update_tab():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/TAB/config.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Header/Footer
        content = content.replace('" &f⚔ &d&lNeverSMP &f⚔"', f'" &8✗ {GRADIENT_NEVERSMP} &8✗"')
        content = content.replace('" &fОнлайн: &d%online% &f| TPS: &d%tps%"', f'" &fОнлайн: {PURPLE}%online% &f| TPS: {PURPLE}%tps%"')
        content = content.replace('" &fНаш сайт: &ddonate.neversmp.ru"', f'" &fНаш сайт: {CYAN}donate.neversmp.ru"')
        content = content.replace('" &fНаш тгк: &dt.me/NeverSMP"', f'" &fНаш тгк: {CYAN}t.me/NeverSMP"')
        
        # Bossbar
        content = content.replace('text: "&fНаш сайт: &bdonate.neversmp.ru"', f'text: "&fНаш сайт: {CYAN}donate.neversmp.ru"')
        content = content.replace('color: "%animation:barcolors%"', 'color: "PURPLE"')
        
        # Scoreboard (if enabled in TAB)
        content = content.replace('" &7⚔ &d&lNeverSmp &7⚔"', f'" &8✗ {GRADIENT_NEVERSMP} &8✗"')
        content = content.replace('"&d┌"', f'"{PURPLE}&l┌"')
        content = content.replace('"&d│ &fНик: &d%player_name%"', f'"{PURPLE}&l│ &fНик: {LIGHT_PURPLE}%player_name%"')
        content = content.replace('"&d│ &fДонат: %luckperms_prefix%"', f'"{PURPLE}&l│ &fДонат: %luckperms_prefix%"')
        content = content.replace('"&d│"', f'"{PURPLE}&l│"')
        content = content.replace('"&d│ &fУ/С: &a%statistic_player_kills%&f/&c%statistic_deaths%"', f'"{PURPLE}&l│ &fУ/С: &a%statistic_player_kills%&f/&c%statistic_deaths%"')
        content = content.replace('"&d│ &fБаланс: &e%vault_eco_balance_fixed%⛁"', f'"{PURPLE}&l│ &fБаланс: {LIGHT_PURPLE}%vault_eco_balance_fixed%&f⛁"')
        content = content.replace('"&d│ &fТокены: &d%playerpoints_points%⛁"', f'"{PURPLE}&l│ &fТокены: {LIGHT_PURPLE}%playerpoints_points%&f⛁"')
        content = content.replace('"&d│ &fНаиграно: &d%statistic_hours_played%ч."', f'"{PURPLE}&l│ &fНаиграно: {LIGHT_PURPLE}%statistic_hours_played%&fч."')
        content = content.replace('"&d└&f"', f'"{PURPLE}&l└"')

        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated TAB config: {f}")

def update_donutscoreboard():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/DonutScoreboard/config.yml')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Lines icons replacement
        content = content.replace("'&f&#00FF00&l$ &fMoney &#00FF000'", f"'&f{PURPLE}⛁ &fMoney {LIGHT_PURPLE}%vault_eco_balance_fixed%'")
        content = content.replace("'&f&#FF0000🗡 &fKills &#FF0000%kills%'", f"'&f{PURPLE}🗡 &fKills {LIGHT_PURPLE}%kills%'")
        content = content.replace("'&f&#FC7703☠ &fDeaths &#FC7703%deaths%'", f"'&f{PURPLE}☠ &fDeaths {LIGHT_PURPLE}%deaths%'")
        content = content.replace("'&f&#FFE600⌚ &fPlaytime &#FFE600%playtime%'", f"'&f{PURPLE}⌚ &fPlaytime {LIGHT_PURPLE}%playtime%'")
        content = content.replace("'&#00A6FF🪓 &#FFFFFFTeam &#00A6FFnone'", f"'{PURPLE}🪓 &fTeam {LIGHT_PURPLE}none'")
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated DonutScoreboard config: {f}")

update_tab()
update_donutscoreboard()
