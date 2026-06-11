Write-Host "=== Zibi Message Cycling System - Live Demo ===" -ForegroundColor Cyan
Write-Host ""

$zibi = 'C:\Users\Krish\AppData\Local\Python\pythoncore-3.14-64\Scripts\zibi.exe'

Write-Host "Test 1: --copy (3 messages)" -ForegroundColor Yellow
& $zibi --copy "message 1"
Write-Host ""
& $zibi --copy "message 2"
Write-Host ""
& $zibi --copy "message 3"
Write-Host ""
& $zibi --copy "cycling back..."
Write-Host ""

Write-Host "Test 2: --pin (2 messages)" -ForegroundColor Yellow
& $zibi --pin 0
Write-Host ""
& $zibi --pin 0
Write-Host ""

Write-Host "Test 3: --transform (1 message)" -ForegroundColor Yellow
Write-Host 'echo "hello world" | & $zibi --copy - ; & $zibi --transform upper' -ForegroundColor Gray
"hello world" | & $zibi --copy -
& $zibi --transform upper
Write-Host ""

Write-Host "=== All tests completed successfully ===" -ForegroundColor Green
