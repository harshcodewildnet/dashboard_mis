
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

    # 2. Test sort_by=deviation&sort=asc (Lowest Deviation)
    Write-Host "`nTesting Lowest Deviation (ASC)..."
    $resAsc = Invoke-RestMethod -Uri "$baseUrl/api/profit_by_client?limit=5&sort_by=deviation&sort=asc" -Method Get -Headers $headers
    
    if ($resAsc.matrix.Count -gt 0) {
        Write-Host "Results (ASC):"
        foreach ($item in $resAsc.matrix) {
            Write-Host "- $($item.client): $($item.deviation)"
        }
        
        # Verify first is lower than last (since we sorted asc)
        if ($resAsc.matrix.Count -gt 1) {
            $first = $resAsc.matrix[0].deviation
            $last = $resAsc.matrix[-1].deviation
            if ($first -le $last) {
                Write-Host "Success: Ascending order verified ($first <= $last)" -ForegroundColor Green
            } else {
                Write-Warning "Failure: Not in ascending order ($first > $last)"
            }
        }
    }

    # 3. Test sort_by=deviation&sort=desc (Highest Deviation)
    Write-Host "`nTesting Highest Deviation (DESC)..."
    $resDesc = Invoke-RestMethod -Uri "$baseUrl/api/profit_by_client?limit=5&sort_by=deviation&sort=desc" -Method Get -Headers $headers
    
    if ($resDesc.matrix.Count -gt 0) {
        Write-Host "Results (DESC):"
        foreach ($item in $resDesc.matrix) {
            Write-Host "- $($item.client): $($item.deviation)"
        }
        
        # Verify first is higher than last (since we sorted desc)
        if ($resDesc.matrix.Count -gt 1) {
            $first = $resDesc.matrix[0].deviation
            $last = $resDesc.matrix[-1].deviation
            if ($first -ge $last) {
                Write-Host "Success: Descending order verified ($first >= $last)" -ForegroundColor Green
            } else {
                Write-Warning "Failure: Not in descending order ($first < $last)"
            }
        }
    }

} catch {
    Write-Error "Failed to verify endpoint: $_"
}
