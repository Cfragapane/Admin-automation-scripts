import os
import shutil
import sqlite3
import logging
from datetime import datetime, timedelta
import json

CONFIG_FILE = "config.json" if os.path.exists("config.json") else "config.example.json"
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

os.makedirs(config["log_dir"], exist_ok=True)
os.makedirs(config["backup_dir"], exist_ok=True)

log_file = os.path.join(config["log_dir"], "db_backup.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def init_demo_database(db_path):
    """Erstellt eine Demo-Datenbank für das Ordnungsamt, falls noch keine existiert."""
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE personal_bestand (
                personal_nr TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                abteilung TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        demo_daten = [
            ("OA-101", "Max Mustermann", "Kommunaler Ordnungsdienst", "Aktiv"),
            ("OA-102", "Erika Musterfrau", "Bußgeldstelle", "Aktiv"),
            ("OA-103", "Thomas Schmidt", "Gewerbeaufsicht", "Aktiv")
        ]
        cursor.executemany("INSERT INTO personal_bestand VALUES (?, ?, ?, ?)", demo_daten)
        conn.commit()
        conn.close()
        logging.info(f"Demo-Datenbank unter {db_path} initialisiert.")

def create_backup(db_path, backup_dir):
    """Erstellt eine zeitgestempelte Sicherungskopie der Datenbank."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_ordnungsamt_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    shutil.copy2(db_path, backup_path)
    logging.info(f"Backup erfolgreich erstellt: {backup_path}")
    print(f"[OK] Backup erstellt: {backup_path}")

def cleanup_old_backups(backup_dir, retention_days):
    """Löscht Backups, die älter als die festgelegte Aufbewahrungsfrist sind."""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0

    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_mtime < cutoff_date:
                os.remove(filepath)
                logging.info(f"Altes Backup gemäß Retention Policy gelöscht: {filename}")
                deleted_count += 1

    print(f"[INFO] Bereinigung abgeschlossen. Gelöschte alte Backups: {deleted_count}")

if __name__ == "__main__":
    try:
        init_demo_database(config["database_path"])
        create_backup(config["database_path"], config["backup_dir"])
        cleanup_old_backups(config["backup_dir"], config["retention_days"])
    except Exception as e:
        logging.error(f"Fehler beim Backup-Prozess: {e}")
        print(f"[FEHLER] {e}")
