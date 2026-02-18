
$ErrorActionPreference = "Stop"

$username = "admin@company.com"
$password = "admin123"
$baseUrl = "http://localhost:8000"

try {
    # 1. Get Token
    Write-Host "Authenticating as $username..."
    $body = @{
        username = $username
        password = $password
    }
    $tokenResponse = Invoke-RestMethod -Uri "$baseUrl/token" -Method Post -Body $body
    $token = $tokenResponse.access_token
    
    if (-not $token) {
        throw "Failed to get access token"
    }
    $headers = @{ Authorization = "Bearer $token" }

    # 2. Test DESC (Highest Profit) - Check Keys
    Write-Host "`nTesting Profit (DESC) and Keys..."
    $resDesc = Invoke-RestMethod -Uri "$baseUrl/api/profit_by_client?limit=1&sort=desc" -Method Get -Headers $headers
    
    if ($resDesc.matrix.Count -gt 0) {
        $top = $resDesc.matrix[0]
        Write-Host "Top Client: $($top.client) | Total: $($top.total)"
        Write-Host "Month Keys: $($top.months.PSObject.Properties.Name -join ', ')"
    }

} catch {
    Write-Error "Failed to verify endpoint: $_"
}
