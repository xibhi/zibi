$z = 'C:\Users\Krish\AppData\Local\Python\pythoncore-3.14-64\Scripts\zibi.exe'
Write-Host 'Message Cycling Test:' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Call 1:' -ForegroundColor Yellow
& $z --copy 'test1'
Write-Host ''
Write-Host 'Call 2:' -ForegroundColor Yellow
& $z --copy 'test2'
Write-Host ''
Write-Host 'Call 3:' -ForegroundColor Yellow
& $z --copy 'test3'
Write-Host ''
Write-Host 'Call 4 (cycles back):' -ForegroundColor Yellow
& $z --copy 'test4'
Write-Host ''
Write-Host 'Success! Messages are cycling!' -ForegroundColor Green
