<#
.SYNOPSIS
    Überprüft kritische Systemressourcen und protokolliert Warnmeldungen.
.DESCRIPTION
    Prüft freien Festplattenspeicher, Arbeitsspeicher-Auslastung sowie wichtige Windows-Dienste.
#>

param (
    [int]$MinFreeSpacePercent = 15,
    [string]$LogPath = ".\logs\system_health.log"
)

$LogDir = Split-Path -Path $LogPath -Parent
if (!(Test-Path -Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Write-Log {
    param ([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Entry = "$Timestamp [$Level] $Message"
    Add-Content -Path $LogPath -Value $Entry
    Write-Host $Entry
}

Write-Log "Starte System-Health-Check..."

$Disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
$FreePercent = [math]::Round(($Disk.FreeSpace / $Disk.Size) * 100, 2)

if ($FreePercent -lt $MinFreeSpacePercent) {
    Write-Log "WARNUNG: Freier Speicher auf C: liegt bei nur $FreePercent% (Schwellenwert: $MinFreeSpacePercent%)" "WARN"
} else {
    Write-Log "Festplattenspeicher C: OK ($FreePercent% frei)" "INFO"
}

$OS = Get-CimInstance -ClassName Win32_OperatingSystem
$FreeMemoryGB = [math]::Round($OS.FreePhysicalMemory / 1MB, 2)
Write-Log "Freier Arbeitsspeicher: $FreeMemoryGB GB" "INFO"

$ServicesToCheck = @("EventLog", "wuauserv")
foreach ($ServiceName in $ServicesToCheck) {
    $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $Service) {
        Write-Log "Dienst '$ServiceName' nicht gefunden." "WARN"
    } elseif ($Service.Status -ne "Running") {
        Write-Log "WARNUNG: Dienst '$($Service.DisplayName)' läuft nicht (Status: $($Service.Status))" "WARN"
    } else {
        Write-Log "Dienst '$($Service.DisplayName)' läuft ordnungsgemäß." "INFO"
    }
}

Write-Log "System-Health-Check abgeschlossen."
