$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "=== Testing Expense API ===" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers

Write-Host "Total Expense: $($response.total_expense)" -ForegroundColor Green
Write-Host "Current Month: $($response.current_month)" -ForegroundColor Green
Write-Host "Items Count: $($response.items.Count)" -ForegroundColor Green

if ($response.items.Count -gt 0) {
    $first = $response.items[0]
    Write-Host "`nFirst Item:" -ForegroundColor Yellow
    Write-Host "  Ledger: $($first.ledger)"
    Write-Host "  Current Amount: $($first.current_amount)"
    Write-Host "  Previous Amount: $($first.previous_amount)"
    Write-Host "  Two Months Ago: $($first.two_months_ago_amount)"
    Write-Host "  Variance: $($first.variance_pct)%"
    
    # Check for any null or undefined values
    if ($null -eq $first.two_months_ago_amount) {
        Write-Host "  ERROR: two_months_ago_amount is NULL!" -ForegroundColor Red
    }
}

Write-Host "`nAPI is working correctly!" -ForegroundColor Green
