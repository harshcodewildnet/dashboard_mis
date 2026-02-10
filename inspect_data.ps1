$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

# Get first 10 rows to see actual data structure
Write-Host "=== Sample Data from /api/rows ===" 
$rows = Invoke-RestMethod -Uri "http://localhost:8000/api/rows?limit=10" -Headers $headers
Write-Host "Total rows: $($rows.count)"
Write-Host "`nFirst row sample:"
$rows.rows[0] | ConvertTo-Json -Depth 3

# Get unique ledgers
Write-Host "`n`n=== All Ledgers ===" 
$ledgers = Invoke-RestMethod -Uri "http://localhost:8000/api/ledgers" -Headers $headers
Write-Host "Total unique ledgers: $($ledgers.Count)"
Write-Host "`nFirst 20 ledgers:"
$ledgers[0..19] | ForEach-Object { Write-Host "  - $_" }
