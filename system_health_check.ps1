<#
.SYNOPSIS
    Monitors critical system resources and logs warning messages.
.DESCRIPTION
    Checks free disk space, available memory, and essential Windows services.
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

Write-Log "Starting System Health Check..."

$Disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
$FreePercent = [math]::Round(($Disk.FreeSpace / $Disk.Size) * 100, 2)

if ($FreePercent -lt $MinFreeSpacePercent) {
    Write-Log "WARNING: Free disk space on C: is only $FreePercent% (Threshold: $MinFreeSpacePercent%)" "WARN"
} else {
    Write-Log "Disk space C: OK ($FreePercent% free)" "INFO"
}

$OS = Get-CimInstance -ClassName Win32_OperatingSystem
$FreeMemoryGB = [math]::Round($OS.FreePhysicalMemory / 1MB, 2)
Write-Log "Free memory: $FreeMemoryGB GB" "INFO"

$ServicesToCheck = @("EventLog", "wuauserv")
foreach ($ServiceName in $ServicesToCheck) {
    $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $Service) {
        Write-Log "Service '$ServiceName' not found." "WARN"
    } elseif ($Service.Status -ne "Running") {
        Write-Log "WARNING: Service '$($Service.DisplayName)' is not running (Status: $($Service.Status))" "WARN"
    } else {
        Write-Log "Service '$($Service.DisplayName)' is running properly." "INFO"
    }
}

Write-Log "System Health Check completed."
