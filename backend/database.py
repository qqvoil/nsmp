import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "nsmp_donates.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS mc_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            item_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            server_target TEXT NOT NULL DEFAULT 'global',
            status TEXT NOT NULL DEFAULT 'pending',
            platega_payload TEXT UNIQUE,
            promo_code TEXT,
            vpn_promo_given TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT
        );
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS mc_promocodes (
            code TEXT PRIMARY KEY,
            discount_percent INTEGER NOT NULL DEFAULT 10,
            max_uses INTEGER NOT NULL DEFAULT 0,
            current_uses INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Insert standard welcome promo code if not exists
        # Initialization complete
        conn.commit()

def create_invoice(player_name: str, item_id: str, item_name: str, amount: int, server_target: str = "global", promo_code: str = None) -> int:
    with get_db() as conn:
        cursor = conn.execute("""
        INSERT INTO mc_invoices (player_name, item_id, item_name, amount, server_target, promo_code)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (player_name, item_id, item_name, amount, server_target, promo_code))
        invoice_id = cursor.lastrowid
        payload = f"mc_{invoice_id}"
        conn.execute("UPDATE mc_invoices SET platega_payload = ? WHERE id = ?", (payload, invoice_id))
        conn.commit()
        return invoice_id, payload

def get_invoice(invoice_id: int):
    with get_db() as conn:
        return conn.execute("SELECT * FROM mc_invoices WHERE id = ?", (invoice_id,)).fetchone()

def get_invoice_by_payload(payload: str):
    with get_db() as conn:
        return conn.execute("SELECT * FROM mc_invoices WHERE platega_payload = ?", (payload,)).fetchone()

def mark_invoice_paid(invoice_id: int, vpn_promo: str = None):
    with get_db() as conn:
        conn.execute("""
        UPDATE mc_invoices 
        SET status = 'paid', paid_at = datetime('now'), vpn_promo_given = ?
        WHERE id = ?
        """, (vpn_promo, invoice_id))
        conn.commit()

def get_recent_donates(limit: int = 10):
    with get_db() as conn:
        return conn.execute("""
        SELECT player_name, item_name, amount, paid_at 
        FROM mc_invoices 
        WHERE status = 'paid' 
        ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
