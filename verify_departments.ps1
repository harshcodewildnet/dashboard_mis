$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

Write-Host "=== Checking Departments API ===" -ForegroundColor Cyan
$departments = Invoke-RestMethod -Uri "http://localhost:8000/api/departments" -Headers $headers

Write-Host "`nTotal Departments: $($departments.Count)" -ForegroundColor Green
if ($departments.Count -eq 0) {
    Write-Host "WARNING: No departments found!" -ForegroundColor Red
} else {
    Write-Host "`nDepartment List:" -ForegroundColor Yellow
    $departments | ForEach-Object {
        Write-Host "  - $($_.department_key): $($_.department_name)" -ForegroundColor White
    }
}

Write-Host "`n=== Expected Departments ===" -ForegroundColor Cyan
Write-Host "If you're expecting more departments, you need to add them to the database." -ForegroundColor Yellow
Write-Host "Currently only showing: DM (Digital Marketing) and OH (Overhead)" -ForegroundColor Yellow
