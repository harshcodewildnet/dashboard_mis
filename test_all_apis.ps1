$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "=== Testing All Endpoints ===" -ForegroundColor Cyan

# Test Income
Write-Host "`n1. Testing /api/income" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/income" -Headers $headers
    Write-Host "   ✓ Income API working - Items: $($response.items.Count)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Income API FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Expense
Write-Host "`n2. Testing /api/expense" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
    Write-Host "   ✓ Expense API working - Items: $($response.items.Count)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Expense API FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Rows
Write-Host "`n3. Testing /api/rows" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/rows?limit=10" -Headers $headers
    Write-Host "   ✓ Rows API working - Rows: $($response.count)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Rows API FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Home
Write-Host "`n4. Testing /api/home" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/home" -Headers $headers
    Write-Host "   ✓ Home API working" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Home API FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
