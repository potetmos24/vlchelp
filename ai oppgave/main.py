import sqlite3
import urllib.request

DB_NAME = "vlc_versions.db"
VLC_VERSION_URL = "https://update.videolan.org/vlc/status-win-x64"

def get_latest_vlc_version():
    with urllib.request.urlopen(VLC_VERSION_URL, timeout=10) as response:
        version = response.read().decode("utf-8").strip()

    if not version:
        raise RuntimeError("Fant ikke VLC-versjon")

    return version

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            product TEXT PRIMARY KEY,
            version TEXT
        )
    """)
    conn.commit()
    conn.close()

def main():
    init_db()
    latest_version = get_latest_vlc_version()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT version FROM versions WHERE product = 'vlc'")
    row = cur.fetchone()

    if row is None:
        print(f"Lagrer første versjon av VLC: {latest_version}")
        cur.execute(
            "INSERT INTO versions (product, version) VALUES ('vlc', ?)",
            (latest_version,)
        )
    elif row[0] != latest_version:
        print(f"Ny VLC-versjon funnet! {row[0]} → {latest_version}")
        cur.execute(
            "UPDATE versions SET version = ? WHERE product = 'vlc'",
            (latest_version,)
        )
    else:
        print(f"Ingen oppdatering. Siste versjon er {latest_version}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
