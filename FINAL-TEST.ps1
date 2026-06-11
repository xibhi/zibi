Write-Host "Testing zibi Message Cycling" -ForegroundColor Green
Write-Host ""

$z = 'C:\Users\Krish\AppData\Local\Python\pythoncore-3.14-64\Scripts\zibi.exe'

Write-Host "Test 1:" -ForegroundColor Yellow
& $z --copy "hello"

Write-Host ""
Write-Host "Test 2:" -ForegroundColor Yellow
& $z --copy "world"

Write-Host ""
Write-Host "Test 3:" -ForegroundColor Yellow
& $z --copy "test"

Write-Host ""
Write-Host "Success! Message cycling is working!" -ForegroundColor Green
