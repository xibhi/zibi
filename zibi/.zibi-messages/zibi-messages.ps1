# zibi Message Manager - Handles success/error messages with cycling
# This script manages the display and rotation of success/error messages for zibi commands

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("success", "error")]
    [string]$Type,
    
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$Replacements = @{}
)

$messagesDir = "x:\Downloads\zibi"
$successFile = Join-Path $messagesDir "success.txt"
$errorFile = Join-Path $messagesDir "error.txt"
$stateFile = Join-Path $messagesDir ".message-state.json"
$outputFile = Join-Path $messagesDir "$Type.txt"

# Initialize state file if it doesn't exist
function Initialize-StateFile {
    if (-not (Test-Path $stateFile)) {
        @{} | ConvertTo-Json | Set-Content $stateFile
    }
}

# Parse messages from a file
function Parse-Messages {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    $messages = @{}
    $currentCommand = $null
    $currentMessages = @()
    
    foreach ($line in $content -split "`n") {
        if ($line -match "^# (.+)$") {
            # Store previous command's messages
            if ($currentCommand) {
                $messages[$currentCommand] = $currentMessages
                # Also create aliases for alternative formats
                if ($currentCommand -like "*/*") {
                    $parts = $currentCommand -split " *\/ *"
                    foreach ($part in $parts) {
                        if ($part) {
                            $messages[$part.Trim()] = $currentMessages
                        }
                    }
                }
            }
            $currentCommand = $matches[1].Trim()
            $currentMessages = @()
        }
        elseif ($line -match "^`"(.+)`"$") {
            $currentMessages += $matches[1]
        }
    }
    
    # Store last command
    if ($currentCommand) {
        $messages[$currentCommand] = $currentMessages
        # Also create aliases for alternative formats
        if ($currentCommand -like "*/*") {
            $parts = $currentCommand -split " *\/ *"
            foreach ($part in $parts) {
                if ($part) {
                    $messages[$part.Trim()] = $currentMessages
                }
            }
        }
    }
    
    return $messages
}

# Get the next message for a command
function Get-NextMessage {
    param(
        [string]$Type,
        [string]$Command,
        [hashtable]$Messages
    )
    
    Initialize-StateFile
    
    # Get or create state
    $stateJson = Get-Content $stateFile -Raw | ConvertFrom-Json
    $stateObj = @{}
    
    # Convert PSObject to hashtable
    if ($stateJson -is [pscustomobject]) {
        $stateJson.PSObject.Properties | ForEach-Object {
            $stateObj[$_.Name] = $_.Value
        }
    }
    
    $key = "$Type`:$Command"
    $currentIndex = if ($stateObj.ContainsKey($key)) { [int]$stateObj[$key] } else { 0 }
    
    # Get messages for this command
    $commandMessages = $Messages[$Command]
    
    if (-not $commandMessages -or $commandMessages.Count -eq 0) {
        return $null
    }
    
    # Get current message
    $message = $commandMessages[$currentIndex]
    
    # Update state for next time (cycle through messages)
    $nextIndex = ($currentIndex + 1) % $commandMessages.Count
    $stateObj[$key] = $nextIndex
    
    # Convert hashtable back to PSObject for JSON serialization
    $stateForJson = New-Object psobject
    $stateObj.GetEnumerator() | ForEach-Object {
        $stateForJson | Add-Member -NotePropertyName $_.Key -NotePropertyValue $_.Value
    }
    
    # Save updated state
    $stateForJson | ConvertTo-Json | Set-Content $stateFile
    
    return $message
}

# Replace placeholders in message
function Replace-Placeholders {
    param(
        [string]$Message,
        [hashtable]$Replacements
    )
    
    foreach ($key in $Replacements.Keys) {
        $Message = $Message -replace "\{$key\}", $Replacements[$key]
    }
    
    return $Message
}

# Main execution
try {
    $messagesFile = if ($Type -eq "success") { $successFile } else { $errorFile }
    $messages = Parse-Messages $messagesFile
    
    $message = Get-NextMessage -Type $Type -Command $Command -Messages $messages
    
    if ($message) {
        # Replace any placeholders
        $message = Replace-Placeholders -Message $message -Replacements $Replacements
        Write-Output $message
    }
    else {
        Write-Error "No message found for command: $Command"
    }
}
catch {
    Write-Error "Error: $_"
    exit 1
}
