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
    """Creates a demo database for municipal administration if none exists yet."""
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE staff_records (
                staff_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        demo_data = [
            ("OA-101", "Max Mustermann", "Municipal Code Enforcement", "Active"),
            ("OA-102", "Erika Musterfrau", "Fines & Citations Office", "Active"),
            ("OA-103", "Thomas Schmidt", "Trade Supervision", "Active")
        ]
        cursor.executemany("INSERT INTO staff_records VALUES (?, ?, ?, ?)", demo_data)
        conn.commit()
        conn.close()
        logging.info(f"Demo database initialized at {db_path}.")

def create_backup(db_path, backup_dir):
    """Creates a timestamped backup copy of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_agency_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    shutil.copy2(db_path, backup_path)
    logging.info(f"Backup successfully created: {backup_path}")
    print(f"[OK] Backup created: {backup_path}")

def cleanup_old_backups(backup_dir, retention_days):
    """Deletes backups older than the defined retention period."""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0

    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_mtime < cutoff_date:
                os.remove(filepath)
                logging.info(f"Old backup deleted per retention policy: {filename}")
                deleted_count += 1

    print(f"[INFO] Cleanup completed. Deleted old backups: {deleted_count}")

if __name__ == "__main__":
    try:
        init_demo_database(config["database_path"])
        create_backup(config["database_path"], config["backup_dir"])
        cleanup_old_backups(config["backup_dir"], config["retention_days"])
    except Exception as e:
        logging.error(f"Error during backup process: {e}")
        print(f"[ERROR] {e}")
