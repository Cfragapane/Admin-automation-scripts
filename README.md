# 🛠️ Admin & Database Automation Scripts

This repository contains a collection of scripts for automating recurring tasks in system and database administration.

## 📋 Included Scripts

* **`db_backup.py`** – Creates automated, timestamped backups of SQL databases including cleanup of outdated backups (Retention Policy).
* **`data_sync_check.py`** – Compares CSV exports against database records, detects discrepancies, and generates a clear audit log.
* **`system_health_check.ps1` / `.sh`** – Monitors critical system resources (disk space, memory, running services) on Windows and Linux and logs warnings.

## 🎯 Focus & Best Practices

* **Traceability:** Consistent logging of all script executions for complete documentation.
* **Security:** Strict separation of code and credentials via configuration files or environment variables.
* **Maintainability:** Modular structure and clear error handling.

## ⚙️ Prerequisites & Usage

* **Environment:** Python 3.10+ as well as PowerShell 5.1 / 7+ (Windows) or Bash (Linux)
* **Configuration:** Before the first run, copy `config.example.json` and save it as `config.json` with your local target paths and database parameters.
