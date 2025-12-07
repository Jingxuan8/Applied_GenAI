from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database_setup import DatabaseSetup

DB_PATH = Path("support.db")

def ensure_db_initialized() -> None:
    if DB_PATH.exists():
        return

    print("[DB_ACCESS] support.db not found, running DatabaseSetup...")
    db = DatabaseSetup(str(DB_PATH))
    db.connect()
    db.create_tables()
    db.create_triggers()
    db.insert_sample_data()
    db.close()
    print("[DB_ACCESS] Database initialized at", DB_PATH)

def _get_connection() -> sqlite3.Connection:
    ensure_db_initialized()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Customer helpers
def fetch_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, name, email, phone, status, created_at, updated_at
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_customers(
    status: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        if status:
            cursor = conn.execute(
                """
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                WHERE status = ?
                LIMIT ?
                """,
                (status, limit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_customer_record(
    customer_id: int,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    allowed_fields = {"name", "email", "status"}
    updates: Dict[str, Any] = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return fetch_customer(customer_id)

    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT id FROM customers WHERE id = ?",
            (customer_id,),
        )
        if cursor.fetchone() is None:
            return None

        set_clause = ", ".join([f"{field} = ?" for field in updates])
        values = list(updates.values()) + [customer_id]

        conn.execute(
            f"UPDATE customers SET {set_clause} WHERE id = ?",
            values,
        )
        conn.commit()

    return fetch_customer(customer_id)

# Ticket helpers
def create_ticket_record(
    customer_id: int,
    issue: str,
    priority: str,
) -> Dict[str, Any]:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets(customer_id, issue, priority, status)
            VALUES(?,?,?,?)
            """,
            (customer_id, issue, priority, "open"),
        )
        ticket_id = cursor.lastrowid
        conn.commit()

        cursor = conn.execute(
            """
            SELECT id, customer_id, issue, priority, status, created_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        )
        row = cursor.fetchone()
        return dict(row)


def fetch_ticket_history(customer_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, customer_id, issue, priority, status, created_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
            """,
            (customer_id,),
        )
        rows: Iterable[sqlite3.Row] = cursor.fetchall()
        return [dict(row) for row in rows]


__all__ = [
    "DB_PATH",
    "fetch_customer",
    "fetch_customers",
    "update_customer_record",
    "create_ticket_record",
    "fetch_ticket_history",
]