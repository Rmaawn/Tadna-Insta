# Network-resilient install for unstable connections (ECONNRESET / ETIMEDOUT).
# Uses the official registry, a single socket, and aggressive retries.
# Re-run it if it stops — npm resumes from its cache.

Write-Host "Installing frontend dependencies (resilient mode)..." -ForegroundColor Cyan

$ok = $false
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Attempt $i of 5..." -ForegroundColor Yellow
    npm install `
        --registry=https://registry.npmjs.org `
        --no-audit --no-fund `
        --maxsockets=1 `
        --fetch-retries=12 `
        --fetch-retry-mintimeout=20000 `
        --fetch-retry-maxtimeout=180000 `
        --fetch-timeout=600000
    if ($LASTEXITCODE -eq 0) { $ok = $true; break }
    Write-Host "Attempt $i failed (network). Retrying in 10s..." -ForegroundColor Red
    Start-Sleep -Seconds 10
}

if ($ok) {
    Write-Host "`nDependencies installed. Run:  npm run dev" -ForegroundColor Green
} else {
    Write-Host "`nStill failing. Try a more stable connection or a VPN, then re-run ./install.ps1" -ForegroundColor Red
}
