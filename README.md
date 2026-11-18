# 🛠️ Admin & Datenbank Automatisierungs-Skripte

Dieses Repository enthält eine Auswahl an Skripten zur Automatisierung wiederkehrender Aufgaben in der System- und Datenbankadministration.

## 📋 Enthaltene Skripte

* **`db_backup.py`** – Erstellt automatisierte, zeitgestempelte Sicherungen von SQL-Datenbanken inklusive Bereinigung alter Backups (Retention Policy).
* **`data_sync_check.py`** – Vergleicht CSV-Exporte mit Datenbankbeständen, erkennt Abweichungen und erstellt ein übersichtliches Prüfprotokoll.
* **`system_health_check.ps1` / `.sh`** – Überprüft kritische Systemressourcen (Festplattenspeicher, Arbeitsspeicher, laufende Dienste) unter Windows und Linux und protokolliert Warnmeldungen.

## 🎯 Fokus & Best Practices

* **Nachvollziehbarkeit:** Durchgängiges Logging aller Skript-Läufe für eine lückenlose Dokumentation.
* **Sicherheit:** Strikte Trennung von Code und Zugangsdaten über Konfigurationsdateien bzw. Umgebungsvariablen.
* **Wartbarkeit:** Modularer Aufbau und verständliche Fehlerbehandlung (Error Handling).

## ⚙️ Voraussetzungen & Nutzung

* **Umgebung:** Python 3.10+ sowie PowerShell 5.1 / 7+ (Windows) oder Bash (Linux)
* **Konfiguration:** Vor der ersten Ausführung die `config.example.json` kopieren und als `config.json` mit den lokalen Zielpfaden und Datenbank-Parametern speichern.
