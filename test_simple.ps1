Write-Host "=== Testing Frontend and API Access ===" -ForegroundColor Cyan

Write-Host "`n1. Testing Frontend" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4173/" -UseBasicParsing
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Testing API with auth" -ForegroundColor Yellow
try {
    $tokenResp = Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded'
    $headers = @{"Authorization"="Bearer $($tokenResp.access_token)"}
    $expenseResp = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
    Write-Host "   API working - Items: $($expenseResp.items.Count)" -ForegroundColor Green
    
    if ($expenseResp.items.Count -gt 0) {
        $item = $expenseResp.items[0]
        Write-Host "   First item has two_months_ago_amount: $($item.two_months_ago_amount -ne $null)" -ForegroundColor $(if ($item.two_months_ago_amount -ne $null) { "Green" } else { "Red" })
    }
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Cyan
