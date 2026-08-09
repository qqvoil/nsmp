import yaml
import json

def get_base_menu(title, open_cmd=None):
    menu = {
        'menu_title': title,
        'size': 54,
        'items': {}
    }
    if open_cmd:
        menu['open_command'] = open_cmd
    return menu

def add_bg(menu):
    menu['items']['bg'] = {
        'material': 'PURPLE_STAINED_GLASS_PANE',
        'slots': ['0-9', '17-18', '26-27', '35-36', '44-53'],
        'display_name': ' '
    }

def add_item(menu, key, slot, material, name, amount, price, enchants=None):
    lore = [
        '',
        f'&7Количество: &f{amount} шт.',
        f'&7Цена: &e{price} монет',
        '',
        '&a▶ Нажмите для покупки'
    ]
    if enchants:
        lore.insert(1, '&dЗачарования:')
        for e in enchants:
            lore.insert(2, f'&8• &7{e[2]}')
        lore.insert(3 + len(enchants), '')
        
    item = {
        'material': material,
        'slot': slot,
        'amount': amount,
        'display_name': name,
        'lore': lore,
        'left_click_commands': [
            f'[console] eco take %player_name% {price}',
            f'[console] give %player_name% {material.lower()} {amount}' if not enchants else f'[console] give %player_name% {material.lower()} {amount} ' + ' '.join([f'{e[0]}:{e[1]}' for e in enchants]),
            f'[message] &aВы успешно купили {name} &aза &e{price} монет!'
        ],
        'left_click_requirement': {
            'requirements': {
                'money': {
                    'type': 'has money',
                    'amount': price,
                    'deny_commands': [
                        '[message] &cУ вас недостаточно монет! Нужно &e' + str(price)
                    ]
                }
            }
        }
    }
    if enchants:
        item['enchantments'] = [f'{e[0]};{e[1]}' for e in enchants]
    menu['items'][key] = item

def add_book(menu, key, slot, name, price, enchant_id, enchant_lvl):
    lore = [
        '',
        f'&7Количество: &f1 шт.',
        f'&7Цена: &e{price} монет',
        '',
        '&a▶ Нажмите для покупки'
    ]
    item = {
        'material': 'ENCHANTED_BOOK',
        'slot': slot,
        'amount': 1,
        'display_name': name,
        'lore': lore,
        'left_click_commands': [
            f'[console] eco take %player_name% {price}',
            f'[console] give %player_name% enchanted_book 1 {enchant_id}:{enchant_lvl}',
            f'[message] &aВы успешно купили {name} &aза &e{price} монет!'
        ],
        'left_click_requirement': {
            'requirements': {
                'money': {
                    'type': 'has money',
                    'amount': price,
                    'deny_commands': [
                        '[message] &cУ вас недостаточно монет! Нужно &e' + str(price)
                    ]
                }
            }
        }
    }
    menu['items'][key] = item

def add_potion(menu, key, slot, name, price, potion_type):
    lore = [
        '',
        f'&7Количество: &f1 шт.',
        f'&7Цена: &e{price} монет',
        '',
        '&a▶ Нажмите для покупки'
    ]
    item = {
        'material': potion_type,
        'slot': slot,
        'amount': 1,
        'display_name': name,
        'lore': lore,
        'left_click_commands': [
            f'[console] eco take %player_name% {price}',
            f'[console] give %player_name% {potion_type.lower()} 1',
            f'[message] &aВы успешно купили {name} &aза &e{price} монет!'
        ],
        'left_click_requirement': {
            'requirements': {
                'money': {
                    'type': 'has money',
                    'amount': price,
                    'deny_commands': [
                        '[message] &cУ вас недостаточно монет! Нужно &e' + str(price)
                    ]
                }
            }
        }
    }
    menu['items'][key] = item


p1 = get_base_menu('&#5a5a5a&lМагазин (Уровень 1)', 'coinshop')
p1['open_requirement'] = {
    'requirements': {
        'exp': {
            'type': '>=',
            'input': '%player_level%',
            'output': '10',
            'deny_commands': ['[message] &cМагазин доступен с 10 уровня опыта!']
        }
    }
}
add_bg(p1)
add_item(p1, 'iron_helmet', 10, 'IRON_HELMET', '&fЖелезный шлем', 1, 500)
add_item(p1, 'iron_chestplate', 19, 'IRON_CHESTPLATE', '&fЖелезная кираса', 1, 800)
add_item(p1, 'iron_leggings', 28, 'IRON_LEGGINGS', '&fЖелезные поножи', 1, 700)
add_item(p1, 'iron_boots', 37, 'IRON_BOOTS', '&fЖелезные ботинки', 1, 400)
add_item(p1, 'iron_sword', 12, 'IRON_SWORD', '&fЖелезный меч', 1, 600)
add_item(p1, 'iron_pickaxe', 21, 'IRON_PICKAXE', '&fЖелезная кирка', 1, 700)
add_item(p1, 'iron_axe', 30, 'IRON_AXE', '&fЖелезный топор', 1, 650)
add_item(p1, 'iron_shovel', 39, 'IRON_SHOVEL', '&fЖелезная лопата', 1, 300)
add_item(p1, 'water_bucket', 14, 'WATER_BUCKET', '&fВедро воды', 1, 800)
add_item(p1, 'gold_ingot', 23, 'GOLD_INGOT', '&fЗолотой слиток', 16, 150)
add_item(p1, 'iron_ingot', 32, 'IRON_INGOT', '&fЖелезный слиток', 16, 100)
add_item(p1, 'coal', 41, 'COAL', '&fУголь', 16, 200)
add_item(p1, 'bread', 16, 'BREAD', '&fХлеб', 32, 250)
add_item(p1, 'planks', 25, 'OAK_PLANKS', '&fДоски', 16, 100)

p1['items']['prev'] = {
    'material': 'BREEZE_ROD',
    'slot': 48,
    'display_name': '&cВыход',
    'click_commands': ['[close]']
}
p1['items']['next'] = {
    'material': 'BLAZE_ROD',
    'slot': 50,
    'display_name': '&aСледующая страница',
    'click_commands': ['[openmenu] coinshop2']
}


p2 = get_base_menu('&#5a5a5a&lМагазин (Уровень 2)')
p2['open_requirement'] = {
    'requirements': {
        'exp': {
            'type': '>=',
            'input': '%player_level%',
            'output': '20',
            'deny_commands': ['[message] &cЭта страница доступна с 20 уровня опыта!']
        }
    }
}
add_bg(p2)
add_item(p2, 'dia_helmet', 10, 'DIAMOND_HELMET', '&bАлмазный шлем', 1, 5000)
add_item(p2, 'dia_chestplate', 19, 'DIAMOND_CHESTPLATE', '&bАлмазная кираса', 1, 8000)
add_item(p2, 'dia_leggings', 28, 'DIAMOND_LEGGINGS', '&bАлмазные поножи', 1, 7000)
add_item(p2, 'dia_boots', 37, 'DIAMOND_BOOTS', '&bАлмазные ботинки', 1, 4000)
add_item(p2, 'dia_sword', 12, 'DIAMOND_SWORD', '&bАлмазный меч', 1, 6000)
add_item(p2, 'dia_pickaxe', 21, 'DIAMOND_PICKAXE', '&bАлмазная кирка', 1, 7000)
add_item(p2, 'dia_axe', 30, 'DIAMOND_AXE', '&bАлмазный топор', 1, 6500)
add_item(p2, 'dia_shovel', 39, 'DIAMOND_SHOVEL', '&bАлмазная лопата', 1, 3000)
add_item(p2, 'cobweb', 14, 'COBWEB', '&fПаутина', 32, 2000)
add_item(p2, 'wind_charge', 23, 'WIND_CHARGE', '&fЗаряд ветра', 32, 3000)
add_item(p2, 'lapis', 32, 'LAPIS_LAZULI', '&9Лазурит', 16, 1000)
add_item(p2, 'emerald', 41, 'EMERALD', '&aИзумруд', 16, 1500)
add_item(p2, 'gapple', 16, 'GOLDEN_APPLE', '&eЗолотое яблоко', 1, 3000)
add_potion(p2, 'potion', 25, '&dЗелье лечения', 5000, 'STRONG_HEALING_POTION') # Using essentials format: strong_healing_potion or similar? Better just give a default potion. I will give POTION. Actually essentials uses strong_healing_potion or similar. I will use 'POTION' in DeluxeMenus display but give strong_healing_potion.
# Let's override potion click command to give strong_healing_potion
p2['items']['potion']['left_click_commands'][1] = '[console] give %player_name% strong_healing_potion 1'

p2['items']['prev'] = {
    'material': 'BREEZE_ROD',
    'slot': 48,
    'display_name': '&cПредыдущая страница',
    'click_commands': ['[openmenu] coinshop']
}
p2['items']['next'] = {
    'material': 'BLAZE_ROD',
    'slot': 50,
    'display_name': '&aСледующая страница',
    'click_commands': ['[openmenu] coinshop3']
}


p3 = get_base_menu('&#5a5a5a&lМагазин (Уровень 3)')
p3['open_requirement'] = {
    'requirements': {
        'exp': {
            'type': '>=',
            'input': '%player_level%',
            'output': '30',
            'deny_commands': ['[message] &cЭта страница доступна с 30 уровня опыта!']
        }
    }
}
add_bg(p3)
p3_ench_arm = [('PROTECTION_ENVIRONMENTAL', 3, 'Защита III'), ('DURABILITY', 2, 'Прочность II')]
p3_ench_weap = [('DAMAGE_ALL', 3, 'Острота III'), ('DURABILITY', 1, 'Прочность I')]
p3_ench_tool = [('DIG_SPEED', 3, 'Эффективность III'), ('DURABILITY', 2, 'Прочность II')]

add_item(p3, 'dia_helmet_e', 10, 'DIAMOND_HELMET', '&bАлмазный шлем', 1, 30000, p3_ench_arm)
add_item(p3, 'dia_chestplate_e', 19, 'DIAMOND_CHESTPLATE', '&bАлмазная кираса', 1, 50000, p3_ench_arm)
add_item(p3, 'dia_leggings_e', 28, 'DIAMOND_LEGGINGS', '&bАлмазные поножи', 1, 45000, p3_ench_arm)
add_item(p3, 'dia_boots_e', 37, 'DIAMOND_BOOTS', '&bАлмазные ботинки', 1, 30000, p3_ench_arm)
add_item(p3, 'dia_sword_e', 12, 'DIAMOND_SWORD', '&bАлмазный меч', 1, 40000, p3_ench_weap)
add_item(p3, 'dia_pickaxe_e', 21, 'DIAMOND_PICKAXE', '&bАлмазная кирка', 1, 45000, p3_ench_tool)
add_item(p3, 'dia_axe_e', 30, 'DIAMOND_AXE', '&bАлмазный топор', 1, 35000, p3_ench_tool)
add_item(p3, 'dia_shovel_e', 39, 'DIAMOND_SHOVEL', '&bАлмазная лопата', 1, 20000, p3_ench_tool)
add_book(p3, 'mending_book', 14, '&dЗачарованная книга (Починка)', 25000, 'mending', 1)
add_item(p3, 'gapple2', 23, 'GOLDEN_APPLE', '&eЗолотое яблоко', 1, 8000)
add_item(p3, 'gcarrot', 32, 'GOLDEN_CARROT', '&6Золотая морковь', 32, 7000)
# Potions: we need to use give commands.
add_item(p3, 'pot_strength', 16, 'POTION', '&cЗелье силы', 1, 20000)
p3['items']['pot_strength']['left_click_commands'][1] = '[console] give %player_name% strong_strength_potion 1'
add_item(p3, 'pot_fire', 25, 'POTION', '&6Зелье огнестойкости', 1, 18000)
p3['items']['pot_fire']['left_click_commands'][1] = '[console] give %player_name% long_fire_resistance_potion 1'
add_item(p3, 'pot_speed', 34, 'POTION', '&bЗелье скорости', 1, 15000)
p3['items']['pot_speed']['left_click_commands'][1] = '[console] give %player_name% strong_swiftness_potion 1'
add_item(p3, 'pot_turtle', 43, 'POTION', '&2Зелье черепашьей мощи', 1, 25000)
p3['items']['pot_turtle']['left_click_commands'][1] = '[console] give %player_name% strong_turtle_master_potion 1'

p3['items']['prev'] = {
    'material': 'BREEZE_ROD',
    'slot': 48,
    'display_name': '&cПредыдущая страница',
    'click_commands': ['[openmenu] coinshop2']
}
p3['items']['next'] = {
    'material': 'BLAZE_ROD',
    'slot': 50,
    'display_name': '&8Следующая страница',
    'lore': ['&7Больше страниц нет']
}

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

for name, obj in [('coinshop', p1), ('coinshop2', p2), ('coinshop3', p3)]:
    with open(f'core/templates/SMP/plugins/DeluxeMenus/gui_menus/{name}.yml', 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, allow_unicode=True, default_flow_style=False, sort_keys=False, Dumper=MyDumper)

print("Generated!")
