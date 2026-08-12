import os
import logging
import json
import functools
import urllib.request
import urllib.error
import subprocess
import re

# Load .env if python-dotenv is available, otherwise read os.environ
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, request, jsonify, redirect, send_from_directory, render_template, session
from catalog import CATALOG, TOKEN_PACKAGES, PREMIUM_TIERS, calculate_custom_tokens
from database import init_db, create_invoice, get_invoice, get_invoice_by_payload, mark_invoice_paid, get_recent_donates, get_db
from rcon_client import execute_rcon_command

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "nsmp-dev-secret-key-2026")

# Initialize database
init_db()

# --- Configs & Environment Variables ---
PLATEGA_MERCHANT_ID = os.environ.get("PLATEGA_MERCHANT_ID")
PLATEGA_SECRET_KEY = os.environ.get("PLATEGA_SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "neversmp_admin_2026")
ADMIN_TG_ID = os.environ.get("ADMIN_TG_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")

# RCON configuration for primary servers
RCON_SERVERS = {
    "lobby": {"host": os.environ.get("RCON_LOBBY_HOST", "127.0.0.1"), "port": int(os.environ.get("RCON_LOBBY_PORT", 25575)), "pass": os.environ.get("RCON_PASS", "")},
    "smp1": {"host": os.environ.get("RCON_SMP1_HOST", "127.0.0.1"), "port": int(os.environ.get("RCON_SMP1_PORT", 25576)), "pass": os.environ.get("RCON_PASS", "")},
}

def is_admin_authenticated() -> bool:
    """Check if current request is authorized as admin via session or API header."""
    if session.get("is_admin") is True:
        return True
    
    header_pass = request.headers.get("X-Admin-Password") or request.headers.get("X-Admin-Key")
    if header_pass and header_pass == ADMIN_PASSWORD:
        return True
        
    return False

def require_admin(f):
    """Decorator to enforce admin authentication on API routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            return jsonify({"success": False, "error": "Unauthorized: Требуется авторизация администратора"}), 401
        return f(*args, **kwargs)
    return decorated_function

def notify_admin(message: str):
    """Send notification to admin's Telegram using standard urllib."""
    if ADMIN_TG_ID and BOT_TOKEN:
        try:
            tg_api_server = os.environ.get("TG_API_SERVER", "https://api.telegram.org")
            url = f"{tg_api_server}/bot{BOT_TOKEN}/sendMessage"
            payload = json.dumps({
                "chat_id": ADMIN_TG_ID,
                "text": message,
                "parse_mode": "HTML"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=4)
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}")

def execute_donation_rewards(player_name: str, item_id: str, custom_tokens: int = 0):
    """Execute LuckPerms and Minecraft commands via RCON."""
    commands = []
    if (item_id == "custom_tokens" or item_id.startswith("tokens_")) and custom_tokens > 0:
        commands = [
            f"p give {{player}} {custom_tokens}",
            f'tellraw @a ["",{{"text":"⭐ NeverSMP ⭐ ","color":"#f9ca24"}},{{"text":"Игрок ","color":"white"}},{{"text":"{{player}}","color":"gold"}},{{"text":" получил ","color":"white"}},{{"text":"{custom_tokens:,} Токенов!","color":"yellow"}}]'
        ]
    else:
        item = CATALOG.get(item_id)
        if item:
            commands = item.get("commands", [])
        else:
            logging.error(f"Item {item_id} not found in catalog during reward execution")
            return

    # High Availability & Cross-Server Broadcast:
    # Database commands (p give, lp) should only execute on ONE server to avoid duplication.
    # Broadcast commands (tellraw, broadcast) should execute on ALL servers.
    global_commands = [c for c in commands if not (c.startswith("tellraw ") or c.startswith("broadcast "))]
    local_commands = [c for c in commands if c.startswith("tellraw ") or c.startswith("broadcast ")]

    global_success = False
    for srv_name, srv_conf in RCON_SERVERS.items():
        if not global_success:
            success_for_this_server = True
            for cmd_template in global_commands:
                cmd = cmd_template.replace("{player}", player_name)
                try:
                    logging.info(f"Executing RCON Global Command on {srv_name}: {cmd}")
                    resp = execute_rcon_command(srv_conf["host"], srv_conf["port"], srv_conf["pass"], cmd)
                    logging.info(f"RCON response from {srv_name}: {resp}")
                except Exception as e:
                    logging.error(f"Failed RCON command '{cmd}' on {srv_name}: {e}")
                    success_for_this_server = False
                    break
            if success_for_this_server:
                global_success = True
                logging.info(f"Successfully executed global rewards on {srv_name}.")
        
        # Always execute local broadcasts on this server if it's reachable
        for cmd_template in local_commands:
            cmd = cmd_template.replace("{player}", player_name)
            try:
                logging.info(f"Executing RCON Local Broadcast on {srv_name}: {cmd}")
                execute_rcon_command(srv_conf["host"], srv_conf["port"], srv_conf["pass"], cmd)
            except Exception as e:
                logging.error(f"Failed RCON broadcast '{cmd}' on {srv_name}: {e}")

# --- Frontend Routes ---

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# --- Public API Endpoints ---

@app.route("/api/catalog", methods=["GET"])
def get_catalog():
    return jsonify({
        "success": True,
        "items": list(CATALOG.values()),
        "token_packages": TOKEN_PACKAGES,
        "premium_tiers": PREMIUM_TIERS
    })

@app.route("/api/calculate_tokens", methods=["GET"])
def calc_tokens():
    tokens_str = request.args.get("tokens", "1000")
    try:
        tokens = int(tokens_str)
    except ValueError:
        tokens = 1000
    calc = calculate_custom_tokens(tokens)
    return jsonify({"success": True, "data": calc})

@app.route("/api/create_payment", methods=["POST"])
def create_payment():
    data = request.json or {}
    player_name = (data.get("player_name") or "").strip()
    item_id = data.get("item_id")
    server_target = data.get("server_target", "global")
    promo_code = (data.get("promo_code") or "").strip().upper()
    custom_tokens = int(data.get("custom_tokens", 0))

    if not player_name or len(player_name) < 3 or len(player_name) > 16:
        return jsonify({"success": False, "error": "Введите корректный ник в Minecraft (3-16 символов)"}), 400

    if item_id == "custom_tokens" and custom_tokens >= 1000:
        calc = calculate_custom_tokens(custom_tokens)
        amount = calc["price"]
        item_name = f"{custom_tokens:,} Токенов (Скидка {calc['discount_percent']}%)".replace(",", " ")
    else:
        item = CATALOG.get(item_id)
        if not item:
            return jsonify({"success": False, "error": "Выбран несуществующий товар"}), 400
        amount = item["price"]
        item_name = item["name"]

    # Check promo code
    used_promo = None
    if promo_code:
        with get_db() as conn:
            promo = conn.execute("SELECT * FROM mc_promocodes WHERE code = ?", (promo_code,)).fetchone()
            if promo and (promo["max_uses"] == 0 or promo["current_uses"] < promo["max_uses"]):
                discount = promo["discount_percent"]
                amount = max(1, int(amount * (1 - discount / 100.0)))
                used_promo = promo["code"]
                conn.execute("UPDATE mc_promocodes SET current_uses = current_uses + 1 WHERE code = ?", (promo["code"],))
                conn.commit()

    invoice_id, payload = create_invoice(player_name, item_id, item_name, amount, server_target, used_promo)

    # If Platega credentials are configured, create transaction
    if PLATEGA_MERCHANT_ID and PLATEGA_SECRET_KEY:
        try:
            url = "https://app.platega.io/v2/transaction/process"
            return_url = os.environ.get("SITE_URL", "https://donate.neversmp.ru")
            req_payload = {
                "paymentDetails": {
                    "amount": int(float(amount)),
                    "currency": "RUB"
                },
                "description": f"NeverSMP: {item_name} ({player_name})",
                "return": f"{return_url}/?success=1&id={invoice_id}",
                "failedUrl": f"{return_url}/?failed=1",
                "payload": payload,
                "webhookUrl": f"{return_url}/api/webhook/platega"
            }
            json_bytes = json.dumps(req_payload).encode("utf-8")
            req = urllib.request.Request(url, data=json_bytes, headers={
                "X-MerchantId": PLATEGA_MERCHANT_ID,
                "X-Secret": PLATEGA_SECRET_KEY,
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                payment_url = resp_data.get("url")
                if payment_url:
                    return jsonify({"success": True, "payment_url": payment_url, "invoice_id": invoice_id})
            
            return jsonify({"success": False, "error": "Ошибка платежной системы. Попробуйте позже."}), 502
        except Exception as e:
            logging.error(f"Platega request failed: {e}")
            return jsonify({"success": False, "error": "Не удалось связаться с кассой."}), 500
    else:
        # Development / Simulation mode
        logging.warning("Platega credentials not set. Returning simulation URL.")
        return jsonify({
            "success": True,
            "payment_url": f"/api/simulate_pay/{invoice_id}",
            "invoice_id": invoice_id,
            "is_dev": True
        })

@app.route("/api/webhook/platega", methods=["POST"])
def platega_webhook():
    secret_key = os.environ.get("PLATEGA_SECRET_KEY")
    incoming_secret = request.headers.get("X-Secret")
    
    # Strict secret verification: Reject if secret is unset or mismatches
    if not secret_key or incoming_secret != secret_key:
        logging.warning("Platega webhook rejected: Invalid or missing secret")
        return "Unauthorized", 401

    data = request.json or {}
    status = data.get("status")
    payload = data.get("payload")

    logging.info(f"Received Platega webhook: {data}")

    if status == "CONFIRMED" and payload:
        invoice = get_invoice_by_payload(payload)
        if invoice and invoice["status"] == "pending":
            mark_invoice_paid(invoice["id"])

            # Resolve custom token count if applicable
            tokens_to_give = 0
            if invoice["item_id"] == "custom_tokens":
                try:
                    tokens_str = invoice["item_name"].split("Токенов")[0].replace(" ", "").strip()
                    tokens_to_give = int(tokens_str)
                except Exception:
                    tokens_to_give = int(invoice["amount"] * 10)
            elif invoice["item_id"] == "tokens_15k":
                tokens_to_give = 15000
            elif invoice["item_id"] == "tokens_50k":
                tokens_to_give = 50000
            elif invoice["item_id"] == "tokens_100k":
                tokens_to_give = 100000

            # Issue Minecraft rewards via RCON
            execute_donation_rewards(invoice["player_name"], invoice["item_id"], custom_tokens=tokens_to_give)

            # Send Telegram Alert
            tg_text = (
                f"⚔ <b>Новый донат NeverSMP!</b>\n"
                f"👤 Игрок: <code>{invoice['player_name']}</code>\n"
                f"🎁 Товар: <b>{invoice['item_name']}</b>\n"
                f"💰 Сумма: <b>{invoice['amount']} ₽</b>"
            )
            notify_admin(tg_text)

            return "OK", 200

    return "Ignored", 200

@app.route("/api/simulate_pay/<int:invoice_id>", methods=["GET"])
def simulate_payment(invoice_id: int):
    """Dev helper to simulate payment confirmation."""
    invoice = get_invoice(invoice_id)
    if invoice and invoice["status"] == "pending":
        mark_invoice_paid(invoice_id)
        
        tokens_to_give = 0
        if invoice["item_id"] == "custom_tokens":
            try:
                tokens_str = invoice["item_name"].split("Токенов")[0].replace(" ", "").strip()
                tokens_to_give = int(tokens_str)
            except Exception:
                tokens_to_give = int(invoice["amount"] * 10)
        elif invoice["item_id"] == "tokens_15k":
            tokens_to_give = 15000
        elif invoice["item_id"] == "tokens_50k":
            tokens_to_give = 50000

        execute_donation_rewards(invoice["player_name"], invoice["item_id"], custom_tokens=tokens_to_give)
        notify_admin(f"🧪 [DEV TEST] Донат подтвержден: {invoice['player_name']} купил {invoice['item_name']} ({invoice['amount']}₽)")
        return redirect(f"/?success=1&id={invoice_id}")
    return redirect("/")

@app.route("/api/invoice/<int:invoice_id>", methods=["GET"])
def check_invoice(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if not invoice:
        return jsonify({"success": False, "error": "Счет не найден"}), 404
    return jsonify({
        "success": True,
        "invoice": {
            "id": invoice["id"],
            "player_name": invoice["player_name"],
            "item_name": invoice["item_name"],
            "amount": invoice["amount"],
            "status": invoice["status"],
            "paid_at": invoice["paid_at"]
        }
    })

# --- Admin Authentication & Control Routes ---

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    password = data.get("password", "")
    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({"success": True, "message": "Авторизация успешна"})
    return jsonify({"success": False, "error": "Неверный пароль администратора"}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({"success": True, "message": "Вы вышли из панели"})

@app.route("/api/admin/check_auth", methods=["GET"])
def admin_check_auth():
    return jsonify({"authenticated": is_admin_authenticated()})

@app.route("/api/admin/invoices", methods=["GET"])
@require_admin
def admin_invoices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, player_name, item_id, item_name, amount, status, server_target, created_at, paid_at FROM mc_invoices ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    invoices = [
        {
            "id": r["id"],
            "player_name": r["player_name"],
            "item_id": r["item_id"],
            "item_name": r["item_name"],
            "amount": r["amount"],
            "status": r["status"],
            "server_target": r["server_target"],
            "created_at": r["created_at"],
            "paid_at": r["paid_at"]
        }
        for r in rows
    ]
    return jsonify({"success": True, "invoices": invoices})

@app.route("/api/admin/transfer_invoice", methods=["POST"])
@require_admin
def admin_transfer_invoice():
    data = request.get_json() or {}
    inv_id = data.get("invoice_id")
    new_nick = (data.get("new_nick") or "").strip()
    if not inv_id or not new_nick:
        return jsonify({"success": False, "message": "Заполните ID счета и новый никнейм"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mc_invoices WHERE id = ?", (inv_id,))
    inv = cursor.fetchone()
    if not inv:
        conn.close()
        return jsonify({"success": False, "message": "Счет не найден"}), 404

    old_nick = inv["player_name"]
    cursor.execute("UPDATE mc_invoices SET player_name = ? WHERE id = ?", (new_nick, inv_id))
    conn.commit()
    conn.close()

    # Deliver rewards to new nickname via RCON
    execute_donation_rewards(new_nick, inv["item_id"])
    notify_admin(f"🔄 <b>[ADMIN] Платеж перепривязан!</b>\nСчет #{inv_id}: <code>{old_nick}</code> ➔ <code>{new_nick}</code> ({inv['item_name']})")
    
    return jsonify({"success": True, "message": f"Счет #{inv_id} перепривязан с '{old_nick}' на '{new_nick}'. Награда выдана!"})

@app.route("/api/admin/manual_give", methods=["POST"])
@require_admin
def admin_manual_give():
    data = request.get_json() or {}
    nick = (data.get("player_name") or "").strip()
    item_id = data.get("item_id")
    custom_tokens = int(data.get("custom_tokens", 0))
    if not nick or not item_id:
        return jsonify({"success": False, "message": "Заполните никнейм и товар"}), 400

    if item_id == "custom_tokens" and custom_tokens > 0:
        execute_donation_rewards(nick, "custom_tokens", custom_tokens=custom_tokens)
        notify_admin(f"🎁 <b>[ADMIN] Ручная выдача:</b>\nИгроку <code>{nick}</code> выдано <b>{custom_tokens} токенов</b>.")
        return jsonify({"success": True, "message": f"{custom_tokens} токенов успешно выдано игроку '{nick}'!"})
    elif item_id == "tokens_30k":
        execute_donation_rewards(nick, "custom_tokens", custom_tokens=30000)
        notify_admin(f"🎁 <b>[ADMIN] Ручная выдача:</b>\nИгроку <code>{nick}</code> выдано <b>30 000 токенов</b>.")
        return jsonify({"success": True, "message": f"30 000 токенов успешно выдано игроку '{nick}'!"})
    elif item_id == "tokens_15k":
        execute_donation_rewards(nick, "custom_tokens", custom_tokens=15000)
        return jsonify({"success": True, "message": f"15 000 токенов успешно выдано игроку '{nick}'!"})
    elif item_id == "tokens_50k":
        execute_donation_rewards(nick, "custom_tokens", custom_tokens=50000)
        return jsonify({"success": True, "message": f"50 000 токенов успешно выдано игроку '{nick}'!"})
    elif item_id == "tokens_100k":
        execute_donation_rewards(nick, "custom_tokens", custom_tokens=100000)
        return jsonify({"success": True, "message": f"100 000 токенов успешно выдано игроку '{nick}'!"})
    else:
        execute_donation_rewards(nick, item_id)
        notify_admin(f"🎁 <b>[ADMIN] Ручная выдача:</b>\nИгроку <code>{nick}</code> выдан товар <b>{item_id}</b>.")
        return jsonify({"success": True, "message": f"Товар '{item_id}' успешно выдан игроку '{nick}'!"})

@app.route("/api/admin/console/<server_name>", methods=["GET"])
@require_admin
def admin_console_get(server_name):
    # Regex to remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    session_name = f"nsmp_{server_name}"
    try:
        # Capture last 100 lines of tmux pane
        result = subprocess.run(
            ["tmux", "capture-pane", "-pt", session_name, "-S", "-100"],
            capture_output=True, text=True, check=True
        )
        clean_text = ansi_escape.sub('', result.stdout)
        # Fix line endings to just \n
        clean_text = clean_text.replace('\r\n', '\n')
        return jsonify({"success": True, "log": clean_text})
    except subprocess.CalledProcessError:
        return jsonify({"success": False, "log": f"[Сервер {server_name} не запущен или консоль недоступна]"})

@app.route("/api/admin/console/<server_name>/send", methods=["POST"])
@require_admin
def admin_console_send(server_name):
    data = request.get_json() or {}
    command = data.get("command", "").strip()
    if not command:
        return jsonify({"success": False, "message": "Пустая команда"})
        
    session_name = f"nsmp_{server_name}"
    try:
        # Send keys to tmux session
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, command, "ENTER"],
            check=True
        )
        notify_admin(f"💻 <b>[ADMIN] Консоль ({server_name}):</b>\nВыполнена команда: <code>{command}</code>")
        return jsonify({"success": True, "message": "Команда отправлена"})
    except subprocess.CalledProcessError:
        return jsonify({"success": False, "message": "Ошибка: Сервер не запущен"})

# --- Promo Code Management Routes ---

@app.route("/api/check_promo", methods=["GET"])
def check_promo():
    code = request.args.get("code", "").strip().upper()
    if not code:
        return jsonify({"success": False, "error": "Пустой промокод"}), 400
        
    with get_db() as conn:
        promo = conn.execute("SELECT * FROM mc_promocodes WHERE code = ?", (code,)).fetchone()
        if not promo:
            return jsonify({"success": False, "error": "Неверный промокод"}), 404
            
        if promo["max_uses"] > 0 and promo["current_uses"] >= promo["max_uses"]:
            return jsonify({"success": False, "error": "Лимит использований исчерпан"}), 400
            
        return jsonify({
            "success": True,
            "discount_percent": promo["discount_percent"]
        })

@app.route("/api/admin/promocodes", methods=["GET"])
@require_admin
def admin_get_promocodes():
    with get_db() as conn:
        promocodes = conn.execute("SELECT * FROM mc_promocodes ORDER BY created_at DESC").fetchall()
        return jsonify({"success": True, "promocodes": [dict(p) for p in promocodes]})

@app.route("/api/admin/promocodes", methods=["POST"])
@require_admin
def admin_add_promocode():
    data = request.json or {}
    code = str(data.get("code", "")).strip().upper()
    try:
        discount = int(data.get("discount_percent", 10))
        max_uses = int(data.get("max_uses", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Неверный формат чисел"}), 400
        
    if not code:
        return jsonify({"success": False, "error": "Код не может быть пустым"}), 400
        
    if discount <= 0 or discount > 100:
        return jsonify({"success": False, "error": "Скидка должна быть от 1 до 100"}), 400
        
    import sqlite3
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO mc_promocodes (code, discount_percent, max_uses) VALUES (?, ?, ?)",
                (code, discount, max_uses)
            )
            conn.commit()
            return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Такой промокод уже существует"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/admin/promocodes/<code>", methods=["DELETE"])
@require_admin
def admin_delete_promocode(code):
    with get_db() as conn:
        conn.execute("DELETE FROM mc_promocodes WHERE code = ?", (code,))
        conn.commit()
        return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
