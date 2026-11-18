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

write_log "INFO" "Starting Linux System Health Check..."

# 1. Check disk space (Root partition /)
USED_PERCENT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
FREE_PERCENT=$((100 - USED_PERCENT))

if [ "$FREE_PERCENT" -lt "$MIN_FREE_PERCENT" ]; then
    write_log "WARN" "Free disk space on / is only ${FREE_PERCENT}% (Threshold: ${MIN_FREE_PERCENT}%)"
else
    write_log "INFO" "Disk space / OK (${FREE_PERCENT}% free)"
fi

# 2. Check available memory
FREE_MEM_MB=$(free -m | awk 'NR==2 {print $7}')
write_log "INFO" "Available memory: ${FREE_MEM_MB} MB"

# 3. Check critical system services
SERVICES=("cron" "systemd-journald")
for SERVICE in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$SERVICE"; then
        write_log "INFO" "Service '$SERVICE' is running properly."
    else
        write_log "WARN" "Service '$SERVICE' is not running or was not found."
    fi
done

write_log "INFO" "System Health Check completed."
