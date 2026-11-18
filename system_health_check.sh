#!/bin/bash

MIN_FREE_PERCENT=15
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/system_health_linux.log"

mkdir -p "$LOG_DIR"

write_log() {
    local LEVEL=$1
    local MESSAGE=$2
    local TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    local ENTRY="$TIMESTAMP [$LEVEL] $MESSAGE"
    echo "$ENTRY" | tee -a "$LOG_FILE"
}

write_log "INFO" "Starte Linux System-Health-Check..."

# 1. Festplattenspeicher prüfen (Root-Partition /)
USED_PERCENT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
FREE_PERCENT=$((100 - USED_PERCENT))

if [ "$FREE_PERCENT" -lt "$MIN_FREE_PERCENT" ]; then
    write_log "WARN" "Freier Speicher auf / liegt bei nur ${FREE_PERCENT}% (Schwellenwert: ${MIN_FREE_PERCENT}%)"
else
    write_log "INFO" "Festplattenspeicher / OK (${FREE_PERCENT}% frei)"
fi

# 2. Freien Arbeitsspeicher prüfen
FREE_MEM_MB=$(free -m | awk 'NR==2 {print $7}')
write_log "INFO" "Verfügbarer Arbeitsspeicher: ${FREE_MEM_MB} MB"

# 3. Wichtige Systemdienste prüfen
SERVICES=("cron" "systemd-journald")
for SERVICE in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$SERVICE"; then
        write_log "INFO" "Dienst '$SERVICE' läuft ordnungsgemäß."
    else
        write_log "WARN" "Dienst '$SERVICE' läuft nicht oder wurde nicht gefunden."
    fi
done

write_log "INFO" "System-Health-Check abgeschlossen."
