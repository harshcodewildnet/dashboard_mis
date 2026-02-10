# Login using form data (OAuth2 format)
$loginBody = "username=admin@company.com&password=admin123"
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
$token = $loginResponse.access_token
Write-Host "Token obtained: $($token.Substring(0, 20))..."

$headers = @{
    "Authorization" = "Bearer $token"
}

# Test /api/home endpoint
Write-Host "`n=== Testing /api/home ===" 
$homeData = Invoke-RestMethod -Uri "http://localhost:8000/api/home" -Headers $headers
Write-Host "Income: $($homeData.income)"
Write-Host "Expense: $($homeData.expense)"
Write-Host "Profit: $($homeData.profit)"
Write-Host "Monthly Expenses Count: $($homeData.monthly_expenses.Count)"
Write-Host "Daily Profit Count: $($homeData.daily_profit.Count)"

# Test /api/departments
Write-Host "`n=== Testing /api/departments ==="
$depts = Invoke-RestMethod -Uri "http://localhost:8000/api/departments" -Headers $headers
Write-Host "Departments count: $($depts.Count)"
$depts | ForEach-Object { Write-Host "  - $($_.department_name) ($($_.department_key))" }

# Test /api/monthly_trends
Write-Host "`n=== Testing /api/monthly_trends ===" 
$trends = Invoke-RestMethod -Uri "http://localhost:8000/api/monthly_trends?months=3" -Headers $headers
Write-Host "Trends count: $($trends.trends.Count)"
$trends.trends | ForEach-Object { Write-Host "  $($_.month_label): Income=$($_.income), Expense=$($_.expense), Profit=$($_.profit)" }
