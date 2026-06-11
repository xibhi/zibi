Write-Host "=== Zibi Message System - Full Test Suite ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Success message cycling for --copy
Write-Host "Test 1: --copy success messages (cycling)" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--copy' -OnSuccess 1
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--copy' -OnSuccess 1
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--copy' -OnSuccess 1
Write-Host ""

# Test 2: Error message cycling
Write-Host "Test 2: Error messages (cycling)" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--fetch' -OnSuccess 0 -ErrorType '/ recall index out of range' -Data @{n=10; max=5}
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--fetch' -OnSuccess 0 -ErrorType '/ recall index out of range' -Data @{n=10; max=5}
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--fetch' -OnSuccess 0 -ErrorType '/ recall index out of range' -Data @{n=10; max=5}
Write-Host ""

# Test 3: Transform success messages
Write-Host "Test 3: Transform success messages" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--transform (upper)' -OnSuccess 1
Write-Host ""

# Test 4: Transform errors
Write-Host "Test 4: Transform error with placeholder" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--transform' -OnSuccess 0 -ErrorType 'unknown mode' -Data @{mode='backwards'}
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--transform' -OnSuccess 0 -ErrorType 'unknown mode' -Data @{mode='sideways'}
Write-Host ""

# Test 5: Share success messages
Write-Host "Test 5: Share success messages" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--share (termbin)' -OnSuccess 1
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--share (paste.rs)' -OnSuccess 1
Write-Host ""

# Test 6: File not found error
Write-Host "Test 6: File error with placeholder" -ForegroundColor Yellow
& 'x:\Downloads\zibi\zibi-command.ps1' -Command '--copy' -OnSuccess 0 -ErrorType '--file file not found' -Data @{path='missing.txt'}
Write-Host ""

# Check state file
Write-Host "Test 7: State file created" -ForegroundColor Yellow
if (Test-Path 'x:\Downloads\zibi\.message-state.json') {
    Write-Host "Status: State file exists at x:\Downloads\zibi\.message-state.json" -ForegroundColor Green
    Write-Host ""
    Write-Host "Current state:" -ForegroundColor Cyan
    Get-Content 'x:\Downloads\zibi\.message-state.json' | ConvertFrom-Json | Format-Table -AutoSize
} else {
    Write-Host "Status: State file not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Suite Complete ===" -ForegroundColor Green
