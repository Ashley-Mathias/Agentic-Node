# backend/scripts/ — optional Railway / Postgres seed helpers.
# Run backend/seed.sql against Railway Postgres.
# Usage:
#   $env:RAILWAY_DATABASE_PUBLIC_URL = "postgresql://postgres:xxx@xxx.railway.app:port/railway"
#   .\backend\scripts\seed-railway.ps1
# Or one-liner:
#   $env:RAILWAY_DATABASE_PUBLIC_URL = "YOUR_URL"; .\backend\scripts\seed-railway.ps1

$url = $env:RAILWAY_DATABASE_PUBLIC_URL
if (-not $url) {
    Write-Host "Set RAILWAY_DATABASE_PUBLIC_URL first (from Postgres-gANW -> Variables -> DATABASE_PUBLIC_URL)." -ForegroundColor Yellow
    exit 1
}

$seedPath = Join-Path $PSScriptRoot "..\seed.sql"
if (-not (Test-Path $seedPath)) {
    Write-Host "Not found: $seedPath" -ForegroundColor Red
    exit 1
}

$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    Write-Host "psql not found. Install PostgreSQL client or run seed.sql manually in Railway Connect / a DB GUI." -ForegroundColor Yellow
    exit 1
}

& psql $url -f $seedPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Seed completed." -ForegroundColor Green
