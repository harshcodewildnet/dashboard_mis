# Test the profit_by_cost_center API endpoint
$baseUrl = "http://localhost:8000"

# Login  
Write-Host "Attempting login..." -ForegroundColor Cyan
try {
    # Use default test credentials
    $loginBody = @{
        username = "test"
        password = "test"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/token" -Method POST -Body "username=test&password=test" -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
    
    # Test profit_by_cost_center endpoint
    Write-Host "`nTesting /api/profit_by_cost_center endpoint..." -ForegroundColor Cyan
    $headers = @{ "Authorization" = "Bearer $token" }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/profit_by_cost_center" -Headers $headers -ErrorAction Stop
    
    Write-Host "✓ API call successful" -ForegroundColor Green
    Write-Host "`nResponse preview:" -ForegroundColor Yellow
    Write-Host "- Month Labels: $($response.month_labels -join ', ')"
    Write-Host "- Number of Cost Centers: $($response.matrix.Count)"
    Write-Host "`nCost Centers:"
    foreach ($row in $response.matrix) {
        Write-Host "  - $($row.cost_center): Total = ₹$('{0:N0}' -f $row.total)"
    }
    
    Write-Host "`nFull Response:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}
