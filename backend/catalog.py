"""
Catalog of donation items, subscriptions, and token packages for NeverSMP.
"""

# Base exchange rate: 1 RUB = 25 Tokens (40 RUB = 1,000 Tokens)
BASE_TOKENS_PER_RUB = 25

# Premium subscription tiers
PREMIUM_TIERS = {
    30: {
        "days": 30,
        "price_rub": 99,
        "price_tokens": 15000,
        "name": "Премиум (30 дней)",
        "label": "30 дней"
    },
    60: {
        "days": 60,
        "price_rub": 149,
        "price_tokens": 25000,
        "name": "Премиум (60 дней)",
        "label": "60 дней • Скидка 25%",
        "badge": "Выгодно"
    },
    90: {
        "days": 90,
        "price_rub": 249,
        "price_tokens": 40000,
        "name": "Премиум (90 дней)",
        "label": "90 дней • Скидка 35%",
        "badge": "Максимум"
    }
}

PREMIUM_PERKS = [
    "⏳ Хардкор: в 2 раза больше времени в зоне новичков",
    "🛡️ Анархия: 6 приват-блоков вместо 3",
    "💰 Анархия & SMP: 10 слотов на аукционе вместо 5",
    "🏠 Анархия & SMP: 5 точек дома (/sethome) вместо 3",
    "🏰 Building: полный доступ к серверу мирного выживания",
    "✨ Эксклюзивный префикс &d[PREMIUM]&f в табе и чате",
    "💎 Возможность выставлять предметы на аукционе за Токены"
]

# Pre-calculated token packages with progressive discount up to 30% at 100k tokens
TOKEN_PACKAGES = [
    {
        "id": "tokens_1k",
        "tokens": 1000,
        "price": 40,
        "discount_percent": 0,
        "badge": "Старт"
    },
    {
        "id": "tokens_5k",
        "tokens": 5000,
        "price": 189,
        "discount_percent": 5,
        "badge": "5% Скидка"
    },
    {
        "id": "tokens_15k",
        "tokens": 15000,
        "price": 539,
        "discount_percent": 10,
        "badge": "Хит • Хватит на Премиум!"
    },
    {
        "id": "tokens_30k",
        "tokens": 30000,
        "price": 999,
        "discount_percent": 17,
        "badge": "17% Скидка"
    },
    {
        "id": "tokens_50k",
        "tokens": 50000,
        "price": 1549,
        "discount_percent": 23,
        "badge": "23% Скидка"
    },
    {
        "id": "tokens_100k",
        "tokens": 100000,
        "price": 2799,
        "discount_percent": 30,
        "badge": "🔥 МАКС. СКИДКА 30%"
    }
]

def calculate_custom_tokens(amount_tokens: int) -> dict:
    """Calculate price and discount for arbitrary token amount (1k to 100k)."""
    amount_tokens = max(1000, min(100000, amount_tokens))
    # Base price without discount (1 rub = 25 tokens)
    base_price = amount_tokens / BASE_TOKENS_PER_RUB
    # Progressive discount curve: 0% at 1k, up to 30% at 100k
    progress = (amount_tokens - 1000) / 99000.0  # 0.0 to 1.0
    discount_pct = round(progress * 30.0, 1)
    final_price = max(10, int(round(base_price * (1 - discount_pct / 100.0))))
    return {
        "tokens": amount_tokens,
        "price": final_price,
        "base_price": int(base_price),
        "discount_percent": discount_pct
    }

CATALOG = {
    "premium_30": {
        "id": "premium_30",
        "category": "subscription",
        "name": "Премиум на 30 дней",
        "price": 99,
        "price_tokens": 15000,
        "days": 30,
        "badge": "Подписка 30 дней",
        "color": "#e056fd",
        "description": "Полный набор привилегий для всех серверов NeverSMP.",
        "perks": PREMIUM_PERKS,
        "commands": [
            "lp user {player} parent addtemp premium 30d",
            "lp user {player} permission settemp neversmp.server.building true 30d",
            "broadcast <gradient:#e056fd:#aa00aa>⚔ NeverSMP ⚔</gradient> <white>Игрок</white> <gradient:light_purple:white>{player}</gradient> <white>приобрел</white> <light_purple>ПРЕМИУМ на 30 дней</light_purple>!"
        ]
    },
    "premium_60": {
        "id": "premium_60",
        "category": "subscription",
        "name": "Премиум на 60 дней",
        "price": 149,
        "price_tokens": 25000,
        "days": 60,
        "badge": "Выгодно • 60 дней",
        "color": "#e056fd",
        "description": "Полный набор привилегий с экономией 25%.",
        "perks": PREMIUM_PERKS,
        "commands": [
            "lp user {player} parent addtemp premium 60d",
            "lp user {player} permission settemp neversmp.server.building true 60d",
            "broadcast <gradient:#e056fd:#aa00aa>⚔ NeverSMP ⚔</gradient> <white>Игрок</white> <gradient:light_purple:white>{player}</gradient> <white>приобрел</white> <light_purple>ПРЕМИУМ на 60 дней</light_purple>!"
        ]
    },
    "premium_90": {
        "id": "premium_90",
        "category": "subscription",
        "name": "Премиум на 90 дней",
        "price": 249,
        "price_tokens": 40000,
        "days": 90,
        "badge": "Максимум • 90 дней",
        "color": "#e056fd",
        "description": "Максимальный срок привилегий с экономией 35%.",
        "perks": PREMIUM_PERKS,
        "commands": [
            "lp user {player} parent addtemp premium 90d",
            "lp user {player} permission settemp neversmp.server.building true 90d",
            "broadcast <gradient:#e056fd:#aa00aa>⚔ NeverSMP ⚔</gradient> <white>Игрок</white> <gradient:light_purple:white>{player}</gradient> <white>приобрел</white> <light_purple>ПРЕМИУМ на 90 дней</light_purple>!"
        ]
    },
    "building_pass": {
        "id": "building_pass",
        "category": "pass",
        "name": "Building Pass (Мирное выживание)",
        "price": 149,
        "badge": "Проходка",
        "color": "#6ab04c",
        "description": "Доступ на сервер спокойного и мирного выживания без классических тёрок.",
        "perks": [
            "Вечный пропуск на сервер Building 1 и Building 2",
            "Мирное ламповое выживание без токсичности и грифа",
            "Увеличенный лимит приватов",
            "Косметические эффекты"
        ],
        "commands": [
            "lp user {player} permission set neversmp.server.building true",
            "broadcast <gradient:#6ab04c:#badc58>⚔ NeverSMP ⚔</gradient> <white>Игрок</white> <gradient:green:white>{player}</gradient> <white>открыл доступ к серверу</white> <green>BUILDING</green>!"
        ]
    },
    "unban": {
        "id": "unban",
        "category": "service",
        "name": "Разбан аккаунта",
        "price": 149,
        "badge": "Услуга",
        "color": "#eb4d4b",
        "description": "Снятие текущей блокировки на всех серверах сети.",
        "perks": [
            "Мгновенный разбан на всей сети серверов",
            "Снятие мута в чате"
        ],
        "commands": [
            "pardon {player}",
            "tempban:unban {player}",
            "mute:unmute {player}"
        ]
    },
    "hardcore_revive": {
        "id": "hardcore_revive",
        "category": "service",
        "name": "Возрождение на Хардкоре",
        "price": 249,
        "price_tokens": 40000,
        "badge": "Хардкор 1 Жизнь",
        "color": "#eb4d4b",
        "description": "Мгновенное воскрешение персонажа после гибели на серверах Хардкора.",
        "perks": [
            "Мгновенный сброс смерти и разбан на Hardcore-1 и Hardcore-2",
            "Возврат в текущий сезон без потери прогресса и ожидания вайпа",
            "Защитный бафф новичка на спавне после воскрешения",
            "Доступно за 249 ₽ на сайте или за 40 000 Токенов в игре"
        ],
        "commands": [
            "pardon {player}",
            "lp user {player} permission unset hardcore.dead",
            "broadcast <gradient:#eb4d4b:#ff7675>☠ Хардкор ☠</gradient> <white>Игрок</white> <red>{player}</red> <white>воскрес из мертвых и вернулся в битву!</white>"
        ]
    }
}

# Add token packages into catalog
for pkg in TOKEN_PACKAGES:
    CATALOG[pkg["id"]] = {
        "id": pkg["id"],
        "category": "currency",
        "name": f"{pkg['tokens']:,} Токенов".replace(",", " "),
        "price": pkg["price"],
        "tokens": pkg["tokens"],
        "discount_percent": pkg["discount_percent"],
        "badge": pkg["badge"],
        "color": "#f9ca24",
        "description": "Внутриигровая донат-валюта NeverSMP. Можно тратить на Премиум и аукцион.",
        "perks": [
            f"{pkg['tokens']:,} токенов на игровой баланс".replace(",", " "),
            "Возможность купить Премиум за 15k токенов",
            "Покупка редких предметов у игроков на аукционе"
        ],
        "commands": [
            f"p give {{player}} {pkg['tokens']}"
        ]
    }
