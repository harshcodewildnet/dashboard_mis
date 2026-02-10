$baseUrl = "http://localhost:8000"

try {
    # 1. Get a ledger name
    $ledgers = Invoke-RestMethod -Uri "$baseUrl/api/ledgers" -Method Get
    $ledgerName = $ledgers[0]
    Write-Host "Testing with ledger: $ledgerName"

    # 2. Fetch details (Global View)
    $response = Invoke-RestMethod -Uri "$baseUrl/api/ledger?name=$ledgerName" -Method Get

    # 3. Check department_breakdown structure
    if ($response.department_breakdown) {
        Write-Host "Success! department_breakdown found." -ForegroundColor Green
        $item = $response.department_breakdown[0]
        if ($item.PSObject.Properties["current"] -and $item.PSObject.Properties["previous"] -and $item.PSObject.Properties["variance"]) {
             Write-Host "Structure Valid: Has current, previous, and variance." -ForegroundColor Green
             $response.department_breakdown | Select-Object label, current, previous, variance | Format-Table
        } else {
             Write-Host "Invalid Structure: Missing keys." -ForegroundColor Red
             $item | Format-List
        }
    } else {
        Write-Host "department_breakdown is missing/null (might be empty data, but no error)." -ForegroundColor Yellow
    }
} catch {
    Write-Host "API Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errBody = $reader.ReadToEnd()
        Write-Host "Response Body: $errBody" -ForegroundColor Red
    }
}
