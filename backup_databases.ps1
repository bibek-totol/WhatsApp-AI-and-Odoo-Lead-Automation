# backup_databases.ps1
# Automated Database Backup Script for Telegram AI & Odoo CRM Databases

$Date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupDir = Join-Path $PSScriptRoot "backups"


if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Starting Database Backup Process ($Date)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan


$TelegramAiBackup = Join-Path $BackupDir "telegram_ai_db_$Date.sql"
Write-Host "Backing up Telegram AI database..." -ForegroundColor Yellow
docker exec telegram_ai_postgres pg_dump -U n8n_user telegram_ai_db > $TelegramAiBackup

if ($LASTEXITCODE -eq 0 -and (Test-Path $TelegramAiBackup) -and (Get-Item $TelegramAiBackup).Length -gt 0) {
    Write-Host "[SUCCESS] Telegram AI DB saved to: $TelegramAiBackup" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to backup Telegram AI database." -ForegroundColor Red
}


$OdooBackup = Join-Path $BackupDir "odoo_db_$Date.sql"
Write-Host "Backing up Odoo CRM database..." -ForegroundColor Yellow
docker exec odoo_postgres pg_dump -U odoo odoo_db > $OdooBackup

if ($LASTEXITCODE -eq 0 -and (Test-Path $OdooBackup) -and (Get-Item $OdooBackup).Length -gt 0) {
    Write-Host "[SUCCESS] Odoo CRM DB saved to: $OdooBackup" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to backup Odoo CRM database." -ForegroundColor Red
}


Write-Host "Applying 30-day retention cleanup policy..." -ForegroundColor Gray
Get-ChildItem -Path $BackupDir -Filter "*.sql" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Backup Completed Successfully!" -ForegroundColor Cyan
Write-Host " Backup Directory: $BackupDir" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
