# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Offline SQLite Client & Horoscope CRM Database
Stores client profiles, birth details, contact info, consultation notes, and generated PDF paths.
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime

def get_user_data_root() -> str:
    """Return standard writable user data directory with graceful fallbacks."""
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "VedasKundli"),
        os.path.join(os.path.expanduser("~"), ".vedaskundli"),
        os.path.join(tempfile.gettempdir(), "VedasKundli"),
    ]
    for c in candidates:
        if not c:
            continue
        try:
            os.makedirs(c, exist_ok=True)
            test_file = os.path.join(c, "_perm_test.tmp")
            with open(test_file, "w") as tf:
                tf.write("1")
            os.remove(test_file)
            return c
        except Exception:
            continue
    return tempfile.gettempdir()


def _get_db_path() -> str:
    """Return the primary writable database path with graceful fallback for protected environments."""
    # 1. Preferred user-specific persistent path in LocalAppData
    user_root = get_user_data_root()
    user_db_dir = os.path.join(user_root, "data")
    os.makedirs(user_db_dir, exist_ok=True)
    user_db = os.path.join(user_db_dir, "gurukulam_crm.db")

    # Migrate local database if it exists and user_db doesn't exist yet
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    local_db = os.path.join(base_dir, "data", "gurukulam_crm.db")
    if os.path.exists(local_db) and not os.path.exists(user_db):
        try:
            import shutil
            shutil.copy2(local_db, user_db)
        except Exception:
            pass

    try:
        conn = sqlite3.connect(user_db)
        conn.cursor().execute("CREATE TABLE IF NOT EXISTS _perm_test (id INT)")
        conn.close()
        return user_db
    except Exception:
        pass

    # 2. Try Temp fallback
    candidates = [
        os.path.join(tempfile.gettempdir(), "VedasKundli", "gurukulam_crm.db"),
        ":memory:"
    ]
    for c in candidates:
        if c == ":memory:":
            return c
        try:
            os.makedirs(os.path.dirname(c), exist_ok=True)
            conn = sqlite3.connect(c)
            conn.cursor().execute("CREATE TABLE IF NOT EXISTS _perm_test (id INT)")
            conn.close()
            return c
        except Exception:
            continue
    return ":memory:"


def init_crm_db():
    db_path = _get_db_path()
    if db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sex TEXT DEFAULT 'Male',
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            second INTEGER DEFAULT 0,
            place TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            tz REAL DEFAULT 5.5,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            category TEXT DEFAULT 'General Consultation',
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS demo_keys (
            key_code TEXT PRIMARY KEY,
            client_name TEXT NOT NULL,
            duration_days INTEGER DEFAULT 7,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS branding (
            id INTEGER PRIMARY KEY,
            astrologer_name TEXT DEFAULT '',
            kendra_name TEXT DEFAULT 'Vedas Jyotish Kendra',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT '',
            tagline TEXT DEFAULT 'Ancient Vedic, KP & Lal Kitab Predictions',
            logo_data TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        )
    """)
    # 1. Seed Sample VIP Client (Harmanjot Singh) if clients table is empty
    cur.execute("SELECT COUNT(*) FROM clients")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO clients (name, sex, year, month, day, hour, minute, second, place, lat, lon, tz, phone, email, category, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Harmanjot Singh (Sample Kundli)",
            "Male",
            2005, 10, 3,
            10, 2, 6,
            "Ludhiana",
            30.9010, 75.8573, 5.5,
            "+91 98765 43210",
            "client@vedaskundli.com",
            "VIP Kundli Analysis",
            "Sample Pre-Loaded Kundli — Parashari Shodashvarga, KP Cuspal, Lal Kitab & Planetary Dashas loaded.",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    # 2. Seed Pre-Activated 30-Day Trial Encryption Key if not present
    cur.execute("SELECT COUNT(*) FROM demo_keys WHERE key_code = 'VEDAS-TRIAL-30D-8F92'")
    if cur.fetchone()[0] == 0:
        expires = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO demo_keys (key_code, client_name, duration_days, created_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "VEDAS-TRIAL-30D-8F92",
            "VIP Trial Client (30-Day Free Demo)",
            30,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            expires,
            "ACTIVE"
        ))

    cur.execute("SELECT COUNT(*) FROM branding WHERE id = 1")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO branding (id, astrologer_name, kendra_name, phone, email, address, tagline, updated_at)
            VALUES (1, 'Vedic Astrologer', 'Vedas Kundli Predictions', '', '', 'India', 'Ancient Vedic, KP & Lal Kitab Predictions', ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
    conn.commit()
    conn.close()


def get_branding():
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM branding WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {
        "astrologer_name": "Vedic Astrologer",
        "kendra_name": "Vedas Kundli Predictions",
        "phone": "",
        "email": "",
        "address": "India",
        "tagline": "Ancient Vedic, KP & Lal Kitab Predictions",
        "logo_data": ""
    }


def save_branding(data: dict):
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO branding (id, astrologer_name, kendra_name, phone, email, address, tagline, logo_data, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            astrologer_name=excluded.astrologer_name,
            kendra_name=excluded.kendra_name,
            phone=excluded.phone,
            email=excluded.email,
            address=excluded.address,
            tagline=excluded.tagline,
            logo_data=excluded.logo_data,
            updated_at=excluded.updated_at
    """, (
        data.get("astrologer_name", ""),
        data.get("kendra_name", "Vedas Kundli Predictions"),
        data.get("phone", ""),
        data.get("email", ""),
        data.get("address", ""),
        data.get("tagline", "Ancient Vedic, KP & Lal Kitab Predictions"),
        data.get("logo_data", ""),
        now_str
    ))
    conn.commit()
    conn.close()
    return get_branding()


def list_clients(search_query: str = ""):
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if search_query.strip():
        q = f"%{search_query.strip()}%"
        cur.execute("SELECT * FROM clients WHERE name LIKE ? OR place LIKE ? OR phone LIKE ? OR category LIKE ? ORDER BY id DESC", (q, q, q, q))
    else:
        cur.execute("SELECT * FROM clients ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_client(client_id: int):
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_client(data: dict) -> int:
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    client_id = data.get("id")
    if client_id:
        cur.execute("""
            UPDATE clients
            SET name=?, sex=?, year=?, month=?, day=?, hour=?, minute=?, second=?,
                place=?, lat=?, lon=?, tz=?, phone=?, email=?, category=?, notes=?
            WHERE id=?
        """, (
            data["name"], data.get("sex", "Male"),
            int(data["year"]), int(data["month"]), int(data["day"]),
            int(data["hour"]), int(data["minute"]), int(data.get("second", 0)),
            data["place"], float(data["lat"]), float(data["lon"]), float(data.get("tz", 5.5)),
            data.get("phone", ""), data.get("email", ""),
            data.get("category", "General Consultation"), data.get("notes", ""),
            int(client_id)
        ))
    else:
        cur.execute("""
            INSERT INTO clients (name, sex, year, month, day, hour, minute, second, place, lat, lon, tz, phone, email, category, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"], data.get("sex", "Male"),
            int(data["year"]), int(data["month"]), int(data["day"]),
            int(data["hour"]), int(data["minute"]), int(data.get("second", 0)),
            data["place"], float(data["lat"]), float(data["lon"]), float(data.get("tz", 5.5)),
            data.get("phone", ""), data.get("email", ""),
            data.get("category", "General Consultation"), data.get("notes", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        client_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(client_id)


def delete_client(client_id: int):
    init_crm_db()
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


import secrets
from datetime import timedelta

def create_demo_key(client_name: str, duration_days: int = 7) -> dict:
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    safe_name = "".join(c for c in client_name if c.isalnum()).upper()[:8] or "USER"
    rand_suffix = secrets.token_hex(2).upper()
    dur_label = f"{duration_days}D" if duration_days > 0 else "LIFE"
    key_code = f"VEDAS-{safe_name}-{dur_label}-{rand_suffix}"

    now = datetime.now()
    if duration_days <= 0:
        expires = now + timedelta(days=3650)
    else:
        expires = now + timedelta(days=duration_days)

    created_str = now.strftime("%Y-%m-%d %H:%M:%S")
    expires_str = expires.strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO demo_keys (key_code, client_name, duration_days, created_at, expires_at, status)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE')
    """, (key_code, client_name, duration_days, created_str, expires_str))
    conn.commit()
    conn.close()
    return {
        "key_code": key_code,
        "client_name": client_name,
        "duration_days": duration_days,
        "created_at": created_str,
        "expires_at": expires_str,
        "status": "ACTIVE"
    }

def list_demo_keys() -> list:
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT key_code, client_name, duration_days, created_at, expires_at, status FROM demo_keys ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    keys = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for r in rows:
        is_expired = (r[4] < now_str) and (r[2] > 0)
        eff_status = "EXPIRED" if is_expired and r[5] == "ACTIVE" else r[5]
        keys.append({
            "key_code": r[0],
            "client_name": r[1],
            "duration_days": r[2],
            "created_at": r[3],
            "expires_at": r[4],
            "status": eff_status
        })
    return keys

def toggle_demo_key_status(key_code: str, new_status: str) -> bool:
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    cur.execute("UPDATE demo_keys SET status = ? WHERE key_code = ?", (new_status, key_code))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0

def validate_access_key(key_code: str) -> dict:
    key_clean = key_code.strip()
    if not key_clean:
        return {"valid": False, "message": "Key cannot be empty"}
    conn = sqlite3.connect(_get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT key_code, client_name, duration_days, created_at, expires_at, status FROM demo_keys WHERE key_code = ?", (key_clean,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"valid": False, "message": "Invalid Key Code. Please check spelling or contact Admin."}

    status = row[5]
    if status == "STOPPED":
        return {"valid": False, "message": f"Access has been revoked by Admin for {row[1]}."}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row[2] > 0 and row[4] < now_str:
        return {"valid": False, "message": f"Demo key for {row[1]} expired on {row[4]}. Contact Admin to renew."}

    return {
        "valid": True,
        "key_code": row[0],
        "client_name": row[1],
        "expires_at": row[4],
        "status": "ACTIVE"
    }
