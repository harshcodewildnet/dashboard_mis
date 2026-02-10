$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "Testing /api/expense response structure" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
    Write-Host "`nResponse structure:" -ForegroundColor Yellow
    Write-Host "  total_expense: $($response.total_expense)"
    Write-Host "  current_month: $($response.current_month)"
    Write-Host "  items count: $($response.items.Count)"
    
    if ($response.items.Count -gt 0) {
        $item = $response.items[0]
        Write-Host "`nFirst item structure:" -ForegroundColor Yellow
        Write-Host "  ledger: $($item.ledger)"
        Write-Host "  current_amount: $($item.current_amount)"
        Write-Host "  previous_amount: $($item.previous_amount)"
        Write-Host "  two_months_ago_amount: $($item.two_months_ago_amount)"
        Write-Host "  variance_pct: $($item.variance_pct)"
        
        Write-Host "`nChecking for undefined/null values:" -ForegroundColor Yellow
        if ($null -eq $item.two_months_ago_amount) {
            Write-Host "  WARNING: two_months_ago_amount is NULL!" -ForegroundColor Red
        } else {
            Write-Host "  OK: two_months_ago_amount = $($item.two_months_ago_amount)" -ForegroundColor Green
        }
    }
    
    Write-Host "`n✓ API Response is valid" -ForegroundColor Green
} catch {
    Write-Host "`n✗ API Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception -ForegroundColor Red
}
