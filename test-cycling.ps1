Write-Host "Testing message cycling:" -ForegroundColor Cyan
Write-Host ""

$zibi = 'C:\Users\Krish\AppData\Local\Python\pythoncore-3.14-64\Scripts\zibi.exe'

Write-Host "Call 1:" -ForegroundColor Yellow
& $zibi --copy "test1"
Write-Host ""

Write-Host "Call 2:" -ForegroundColor Yellow
& $zibi --copy "test2"
Write-Host ""

Write-Host "Call 3:" -ForegroundColor Yellow
& $zibi --copy "test3"
Write-Host ""

Write-Host "Call 4 (should cycle back):" -ForegroundColor Yellow
& $zibi --copy "test4"
Write-Host ""

Write-Host "Testing other commands:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Clear command:" -ForegroundColor Yellow
& $zibi --clear
Write-Host ""

Write-Host "Clear again (cycling):" -ForegroundColor Yellow
& $zibi --clear
