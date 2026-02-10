$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "=== Testing /api/expense ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
    Write-Host "Total Expense: $($response.total_expense)" -ForegroundColor Green
    Write-Host "Items count: $($response.items.Count)" -ForegroundColor Green
    if ($response.items.Count -gt 0) {
        Write-Host "`nFirst item:" -ForegroundColor Yellow
        $item = $response.items[0]
        Write-Host "  Ledger: $($item.ledger)"
        Write-Host "  Current Amount: $($item.current_amount)"
        Write-Host "  Previous Amount: $($item.previous_amount)"
        Write-Host "  Two Months Ago: $($item.two_months_ago_amount)"
        Write-Host "  Variance %: $($item.variance_pct)"
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
