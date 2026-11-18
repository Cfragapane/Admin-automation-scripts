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
        raise FileNotFoundError("Datenbank oder CSV-Datei wurde nicht gefunden. Bitte zuerst db_backup.py ausführen.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT personal_nr, name, abteilung, status FROM personal_bestand")
    db_records = {row[0]: {"name": row[1], "abteilung": row[2], "status": row[3]} for row in cursor.fetchall()}
    conn.close()

    csv_records = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            csv_records[row["personal_nr"]] = {
                "name": row["name"],
                "abteilung": row["abteilung"],
                "status": row["status"]
            }

    print("=== PRÜFPROTOKOLL: DATENABGLEICH ===")
    logging.info("Starte Datenabgleich zwischen CSV und Datenbank.")

    for p_nr, data in csv_records.items():
        if p_nr not in db_records:
            msg = f"[NEU IN CSV] {p_nr} ({data['name']}) fehlt in der Datenbank."
            print(msg)
            logging.warning(msg)
        elif data != db_records[p_nr]:
            msg = f"[ABWEICHUNG] {p_nr} ({data['name']}): CSV={data} vs. DB={db_records[p_nr]}"
            print(msg)
            logging.warning(msg)

    for p_nr, data in db_records.items():
        if p_nr not in csv_records:
            msg = f"[FEHLT IN CSV] {p_nr} ({data['name']}) ist in DB vorhanden, aber nicht im aktuellen Export."
            print(msg)
            logging.warning(msg)

    logging.info("Datenabgleich erfolgreich beendet.")
    print("=== PRÜFUNG ABGESCHLOSSEN ===")

if __name__ == "__main__":
    try:
        run_sync_check(config["database_path"], config["csv_export_path"])
    except Exception as e:
        logging.error(f"Fehler beim Datenabgleich: {e}")
        print(f"[FEHLER] {e}")
