# zibi Command Wrapper - Execute commands and handle success/error messages
# Usage: .\zibi-command.ps1 -Command "--copy" -Args "hello" -OnSuccess $true
# Or: .\zibi-command.ps1 -Command "--fetch" -Args "0" -OnSuccess $false -ErrorType "index out of range" -Data @{n=5; max=3}

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$Args,
    
    [Parameter(Mandatory=$true)]
    [bool]$OnSuccess,
    
    [Parameter(Mandatory=$false)]
    [string]$ErrorType,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$Data = @{}
)

$messagesDir = "x:\Downloads\zibi"
$messageScript = Join-Path $messagesDir "zibi-messages.ps1"

try {
    if ($OnSuccess) {
        # Call success message
        $splat = @{
            Type = "success"
            Command = $Command
        }
        if ($Data.Count -gt 0) {
            $splat["Replacements"] = $Data
        }
        
        $message = & $messageScript @splat
        Write-Host $message
        
        # Optionally append to success.txt if you want to keep a log
        # Add-Content (Join-Path $messagesDir "success-log.txt") "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Command: $message"
    }
    else {
        # Call error message with error type
        $errorKey = if ($ErrorType) { "$Command $ErrorType" } else { $Command }
        
        $splat = @{
            Type = "error"
            Command = $errorKey
        }
        if ($Data.Count -gt 0) {
            $splat["Replacements"] = $Data
        }
        
        $message = & $messageScript @splat
        if ($message) {
            Write-Host $message -ForegroundColor Red
        } else {
            Write-Host "Error occurred during: $Command" -ForegroundColor Red
        }
        
        # Optionally append to error.txt if you want to keep a log
        # Add-Content (Join-Path $messagesDir "error-log.txt") "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $errorKey: $message"
    }
}
catch {
    Write-Error "Error executing command: $_"
    exit 1
}
