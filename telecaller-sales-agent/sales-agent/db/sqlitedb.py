"""SQLite data layer for the telecaller sales agent.

Holds the schema, seed data, and the data-access functions that the agent's
tools will call later. `sqlite3` is in the stdlib, so there are no extra deps.

Run this file directly to create + seed the DB:

    cd sales-agent
    uv run python -m db.sqlitedb
"""

import sqlite3
from pathlib import Path

# Keep the DB file next to this module (sales-agent/db/sales.db).
DB_PATH = Path(__file__).parent / "sales.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- Seed data (inserted only when the table is empty) ---------------------

SEED_LEADS = [
    # (name, phone, company, status, notes)
    ("Acme Corp", "+15551110001", "Acme Corp", "new",
     "Inbound website enquiry. Interested in the Pro plan."),
    ("Riya Sharma", "+15551110002", "BrightLeaf Pvt Ltd", "contacted",
     "Spoke once; asked us to call back next week."),
    ("John Patel", "+15551110003", "Nimbus Retail", "qualified",
     "Wants a demo for the team of 20."),
]

SEED_PRODUCTS = [
    # (name, description, price)
    ("Starter Plan", "Up to 3 users, core CRM features, email support.", 29.0),
    ("Pro Plan", "Up to 25 users, automation, analytics, priority support.", 99.0),
    ("Enterprise Plan", "Unlimited users, SSO, dedicated success manager.", 299.0),
    ("Onboarding Package", "One-time guided setup and data migration.", 499.0),
]


def init_db() -> None:
    """Create the tables if needed and seed default rows when empty.

    Idempotent: safe to call on every startup. Seed rows are only inserted
    when a table has no rows, so re-running never duplicates data.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                phone   TEXT,
                company TEXT,
                status  TEXT,
                notes   TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS calls (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id    INTEGER NOT NULL,
                outcome    TEXT,
                notes      TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS callbacks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id      INTEGER NOT NULL,
                scheduled_at TEXT,
                notes        TEXT,
                created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT,
                price       REAL
            )
            """
        )

        # Seed only when empty.
        if cur.execute("SELECT COUNT(*) FROM leads").fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO leads (name, phone, company, status, notes) "
                "VALUES (?, ?, ?, ?, ?)",
                SEED_LEADS,
            )
        if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO products (name, description, price) "
                "VALUES (?, ?, ?)",
                SEED_PRODUCTS,
            )

        conn.commit()
    finally:
        conn.close()


# --- Data-access functions (used by the agent's tools later) ---------------

def fetch_lead(name_or_phone: str) -> dict | None:
    """Look up a single lead by name or phone (case-insensitive, partial name)."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT * FROM leads
            WHERE LOWER(name) LIKE LOWER(?) OR phone = ?
            LIMIT 1
            """,
            (f"%{name_or_phone}%", name_or_phone),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_call(lead_id: int, outcome: str, notes: str = "") -> int:
    """Record a call outcome for a lead. Returns the new call id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO calls (lead_id, outcome, notes) VALUES (?, ?, ?)",
            (lead_id, outcome, notes),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_callback(lead_id: int, scheduled_at: str, notes: str = "") -> int:
    """Schedule a follow-up callback for a lead. Returns the new callback id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO callbacks (lead_id, scheduled_at, notes) "
            "VALUES (?, ?, ?)",
            (lead_id, scheduled_at, notes),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def fetch_products() -> list[dict]:
    """Return all products with their pricing."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY price"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialised DB at: {DB_PATH}\n")

    print("Seeded leads:")
    conn = get_connection()
    try:
        for row in conn.execute("SELECT * FROM leads"):
            print(f"  [{row['id']}] {row['name']} ({row['company']}) "
                  f"- {row['status']} - {row['phone']}")
    finally:
        conn.close()

    print("\nSeeded products:")
    for p in fetch_products():
        print(f"  [{p['id']}] {p['name']} - ${p['price']:.2f} - {p['description']}")
