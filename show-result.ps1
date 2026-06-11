Write-Host "Demonstrating the fix:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Before integration:" -ForegroundColor Yellow
Write-Host "  zibi --copy hello"
Write-Host "  -> Copied 5 chars from manual. Preview: ""hello"""
Write-Host ""
Write-Host "After integration (with cycling):" -ForegroundColor Yellow
Write-Host ""

$zibi = 'C:\Users\Krish\AppData\Local\Python\pythoncore-3.14-64\Scripts\zibi.exe'

Write-Host "Run 1:" -ForegroundColor Gray
& $zibi --copy 'hello'

Write-Host ""
Write-Host "Run 2 (message cycles):" -ForegroundColor Gray
& $zibi --copy 'world'

Write-Host ""
Write-Host "Run 3 (message cycles again):" -ForegroundColor Gray
& $zibi --copy 'test'

Write-Host ""
Write-Host "=== Message cycling successfully integrated ===" -ForegroundColor Green
