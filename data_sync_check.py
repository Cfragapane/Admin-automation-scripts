import os
import csv
import sqlite3
import logging
import json

CONFIG_FILE = "config.json" if os.path.exists("config.json") else "config.example.json"
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

os.makedirs(config["log_dir"], exist_ok=True)
logging.basicConfig(
    filename=os.path.join(config["log_dir"], "data_sync.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_sync_check(db_path, csv_path):
    if not os.path.exists(db_path) or not os.path.exists(csv_path):
        raise FileNotFoundError("Database or CSV file not found. Please run db_backup.py first.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT staff_id, name, department, status FROM staff_records")
    db_records = {row[0]: {"name": row[1], "department": row[2], "status": row[3]} for row in cursor.fetchall()}
    conn.close()

    csv_records = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            csv_records[row["staff_id"]] = {
                "name": row["name"],
                "department": row["department"],
                "status": row["status"]
            }

    print("=== AUDIT LOG: DATA SYNCHRONIZATION ===")
    logging.info("Starting data synchronization check between CSV and database.")

    for s_id, data in csv_records.items():
        if s_id not in db_records:
            msg = f"[NEW IN CSV] {s_id} ({data['name']}) is missing in the database."
            print(msg)
            logging.warning(msg)
        elif data != db_records[s_id]:
            msg = f"[MISMATCH] {s_id} ({data['name']}): CSV={data} vs. DB={db_records[s_id]}"
            print(msg)
            logging.warning(msg)

    for s_id, data in db_records.items():
        if s_id not in csv_records:
            msg = f"[MISSING IN CSV] {s_id} ({data['name']}) exists in DB, but not in the current export."
            print(msg)
            logging.warning(msg)

    logging.info("Data synchronization check completed successfully.")
    print("=== AUDIT COMPLETED ===")

if __name__ == "__main__":
    try:
        run_sync_check(config["database_path"], config["csv_export_path"])
    except Exception as e:
        logging.error(f"Error during data synchronization: {e}")
        print(f"[ERROR] {e}")
