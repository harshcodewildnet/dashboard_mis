$token = (Invoke-RestMethod -Uri 'http://localhost:8000/token' -Method Post -Body 'username=admin@company.com&password=admin123' -ContentType 'application/x-www-form-urlencoded').access_token
$headers = @{"Authorization"="Bearer $token"}

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/expense" -Headers $headers
Write-Host "Items count: $($response.items.Count)"
if ($response.items.Count -gt 0) {
    $item = $response.items[0]
    Write-Host "First item two_months_ago_amount: $($item.two_months_ago_amount)"
}
