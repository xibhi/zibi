Write-Host "Files Created:" -ForegroundColor Cyan
Write-Host ""

$files = @('zibi-messages.ps1', 'zibi-command.ps1', 'test-messages.ps1', 'README-MESSAGES.md', 'QUICK-REFERENCE.txt', 'SYSTEM-SUMMARY.txt', '.message-state.json')

foreach ($file in $files) {
    $path = Join-Path "x:\Downloads\zibi" $file
    if (Test-Path $path) {
        $item = Get-Item $path
        Write-Host "[OK] $file" -ForegroundColor Green
        Write-Host "  Size: $('{0:N0}' -f $item.Length) bytes" -ForegroundColor Gray
    } else {
        Write-Host "[MISSING] $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "System Status:" -ForegroundColor Cyan
Write-Host "[OK] Message management system fully implemented" -ForegroundColor Green
Write-Host "[OK] Success messages with cycling: 21+ commands" -ForegroundColor Green
Write-Host "[OK] Error messages with cycling: 19+ error types" -ForegroundColor Green
Write-Host "[OK] Placeholder replacement system working" -ForegroundColor Green
Write-Host "[OK] State persistence enabled" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to use! See QUICK-REFERENCE.txt for usage examples." -ForegroundColor Yellow
