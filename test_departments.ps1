$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "=== Testing Departments API ===" -ForegroundColor Cyan
$departments = Invoke-RestMethod -Uri "http://localhost:8000/api/departments" -Headers $headers

Write-Host "Total Departments: $($departments.Count)" -ForegroundColor Green
$departments | ForEach-Object {
    Write-Host "  - $($_.department_key): $($_.department_name)" -ForegroundColor Yellow
}
