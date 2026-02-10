# Test frontend is serving content
Write-Host "=== Testing Frontend and API Access ===" -ForegroundColor Cyan

Write-Host "`n1. Testing Frontend (http://localhost:4173)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4173/" -UseBasicParsing
    Write-Host "   ✓ Frontend accessible - Status: $($response.StatusCode)" -ForegroundColor Green
    if ($response.Content -match 'script') {
        Write-Host "   ✓ JavaScript files found in HTML" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Frontend NOT accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Testing API without auth (should fail with 401)" -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/expense" -UseBasicParsing | Out-Null
    Write-Host "   ✗ API accessible without auth (unexpected)" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✓ API correctly requires authentication" -ForegroundColor Green
    } else {
        Write-Host "   ? Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`n3. Testing API with auth" -ForegroundColor Yellow
try {
    $token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
    $headers = @{"Authorization"="Bearer $token"}
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
    Write-Host "   ✓ API working - Total Expense: ₹$($response.total_expense)" -ForegroundColor Green
    Write-Host "   ✓ Items in response: $($response.items.Count)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n4. Checking CORS headers" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/home" -Method Options -UseBasicParsing -Headers @{"Origin"="http://localhost:4173"}
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "   ✓ CORS headers present: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
    } else {
        Write-Host "   ✗ No CORS headers found" -ForegroundColor Red
    }
} catch {
    Write-Host "   ? Could not test CORS: $($_.Exception.Message)" -ForegroundColor Yellow
}
