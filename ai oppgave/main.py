# main.py
import sqlite3
import requests
from bs4 import BeautifulSoup

DB_NAME = "vlc_versions.db"
VLC_URL = "https://www.videolan.org/vlc/"

def get_latest_vlc_version():
    response = requests.get(VLC_URL, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # VLC viser versjon i <span class="version">
    version_span = soup.find("span", class_="version")
    if not version_span:
        raise RuntimeError("Fant ikke VLC-versjon på nettsiden")

    return version_span.text.strip()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT UNIQUE,
            version TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_stored_version(product):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT version FROM versions WHERE product = ?", (product,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def update_version(product, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO versions (product, version)
        VALUES (?, ?)
        ON CONFLICT(product) DO UPDATE SET version = excluded.version
    """, (product, version))
    conn.commit()
    conn.close()

def main():
    init_db()

    product = "vlc"
    latest_version = get_latest_vlc_version()
    stored_version = get_stored_version(product)

    if stored_version is None:
        print(f"Lagrer første versjon av VLC: {latest_version}")
        update_version(product, latest_version)
    elif stored_version != latest_version:
        print(f"Ny versjon funnet! {stored_version} → {latest_version}")
        update_version(product, latest_version)
    else:
        print(f"Ingen oppdatering. Siste versjon er fortsatt {stored_version}")

if __name__ == "__main__":
    main()
