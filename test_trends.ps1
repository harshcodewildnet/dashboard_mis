$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

# Test monthly trends endpoint
Write-Host "=== Testing /api/monthly_trends with 12 months ===" 
$trends = Invoke-RestMethod -Uri "http://localhost:8000/api/monthly_trends?months=12" -Headers $headers

Write-Host "Total trends: $($trends.trends.Count)"
Write-Host "`nTrends data:"
$trends.trends | ForEach-Object { 
    Write-Host "$($_.month_label): Income=$($_.income), Expense=$($_.expense), Profit=$($_.profit)" 
}

Write-Host "`n=== Summary ===" 
Write-Host "Avg Income: $($trends.summary.avg_income)"
Write-Host "Avg Expense: $($trends.summary.avg_expense)"
Write-Host "Avg Profit: $($trends.summary.avg_profit)"
Write-Host "Best Month: $($trends.summary.best_month)"
Write-Host "Worst Month: $($trends.summary.worst_month)"
