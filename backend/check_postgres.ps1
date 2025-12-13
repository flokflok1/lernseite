# Check PostgreSQL Service Status
Write-Host "Checking PostgreSQL service..." -ForegroundColor Cyan
Get-Service -Name "postgresql*" | Format-Table Name, Status, DisplayName -AutoSize

Write-Host "`nTesting connection with different passwords..." -ForegroundColor Cyan

# Common default passwords to try
$passwords = @("postgres", "", "admin", "password", "root")
$host = "localhost"
$port = "5432"
$user = "postgres"

foreach ($pwd in $passwords) {
    Write-Host "`nTrying password: '$pwd'..." -ForegroundColor Yellow

    $env:PGPASSWORD = $pwd
    $result = & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U $user -h $host -p $port -c "SELECT version();" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS! Password is: '$pwd'" -ForegroundColor Green
        Write-Host "`nPlease update your .env file with:" -ForegroundColor Green
        Write-Host "DB_PASSWORD=$pwd" -ForegroundColor Yellow
        break
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nNone of the common passwords worked." -ForegroundColor Red
    Write-Host "You need to find your PostgreSQL password or reset it." -ForegroundColor Yellow
}
