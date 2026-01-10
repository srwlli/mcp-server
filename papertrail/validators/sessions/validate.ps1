# validate-sessions.ps1
# Validates all communication.json files against the JSON schema

param(
    [switch]$Verbose,
    [switch]$FixTypos
)

$ErrorActionPreference = "Stop"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

Write-Host "`nSession Validation Report" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan

# Check if ajv-cli is installed
$ajvInstalled = $null -ne (Get-Command ajv -ErrorAction SilentlyContinue)

if (-not $ajvInstalled) {
    Write-Host "`najv-cli not found. Installing..." -ForegroundColor $Yellow
    Write-Host "Running: npm install -g ajv-cli" -ForegroundColor $Yellow
    npm install -g ajv-cli

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nFailed to install ajv-cli" -ForegroundColor $Red
        Write-Host "Please install manually: npm install -g ajv-cli" -ForegroundColor $Yellow
        exit 1
    }
    Write-Host "ajv-cli installed successfully`n" -ForegroundColor $Green
}

# Paths
$papertrailRoot = "C:\Users\willh\.mcp-servers\papertrail"
$sessionsDir = "C:\Users\willh\.mcp-servers\coderef\sessions"
$schemaPath = Join-Path $papertrailRoot "schemas\sessions\communication-schema.json"

# Verify schema exists
if (-not (Test-Path $schemaPath)) {
    Write-Host "`nSchema not found: $schemaPath" -ForegroundColor $Red
    exit 1
}

# Find all communication.json files
$commFiles = Get-ChildItem -Path $sessionsDir -Recurse -Filter "communication.json" |
    Where-Object { $_.DirectoryName -notmatch "node_modules" }

if ($commFiles.Count -eq 0) {
    Write-Host "`nNo communication.json files found in sessions directory" -ForegroundColor $Yellow
    exit 0
}

Write-Host "`nFound $($commFiles.Count) session(s) to validate`n"

# Validation results
$results = @{
    Valid = @()
    Invalid = @()
    Fixed = @()
}

# Common typo fixes
$typoFixes = @{
    "completed" = "complete"
    "done" = "complete"
    "finished" = "complete"
    "started" = "in_progress"
    "running" = "in_progress"
    "pending" = "not_started"
}

foreach ($file in $commFiles) {
    $sessionName = $file.Directory.Name
    $relativePath = $file.FullName.Replace($sessionsDir + "\", "")

    # Read and parse JSON
    try {
        $json = Get-Content $file.FullName -Raw | ConvertFrom-Json
    } catch {
        Write-Host "[FAIL] $relativePath" -ForegroundColor $Red
        Write-Host "   ERROR: Invalid JSON syntax - $_" -ForegroundColor $Red
        $results.Invalid += @{
            Path = $relativePath
            Error = "Invalid JSON syntax"
        }
        continue
    }

    # Check for common typos if -FixTypos is enabled
    if ($FixTypos) {
        $modified = $false

        # Check session status
        if ($typoFixes.ContainsKey($json.status)) {
            Write-Host "[FIX] $relativePath" -ForegroundColor $Yellow
            Write-Host "   Fixing: status '$($json.status)' -> '$($typoFixes[$json.status])'" -ForegroundColor $Yellow
            $json.status = $typoFixes[$json.status]
            $modified = $true
        }

        # Check orchestrator status
        if ($typoFixes.ContainsKey($json.orchestrator.status)) {
            Write-Host "[FIX] $relativePath" -ForegroundColor $Yellow
            Write-Host "   Fixing: orchestrator.status '$($json.orchestrator.status)' -> '$($typoFixes[$json.orchestrator.status])'" -ForegroundColor $Yellow
            $json.orchestrator.status = $typoFixes[$json.orchestrator.status]
            $modified = $true
        }

        # Check agent statuses
        for ($i = 0; $i -lt $json.agents.Count; $i++) {
            if ($typoFixes.ContainsKey($json.agents[$i].status)) {
                Write-Host "[FIX] $relativePath" -ForegroundColor $Yellow
                Write-Host "   Fixing: agents[$i].status '$($json.agents[$i].status)' -> '$($typoFixes[$json.agents[$i].status])'" -ForegroundColor $Yellow
                $json.agents[$i].status = $typoFixes[$json.agents[$i].status]
                $modified = $true
            }
        }

        # Save if modified
        if ($modified) {
            $json | ConvertTo-Json -Depth 10 | Set-Content $file.FullName
            $results.Fixed += $relativePath
        }
    }

    # Validate against schema
    $validationOutput = ajv validate -s $schemaPath -d $file.FullName 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] $relativePath" -ForegroundColor $Green
        if ($Verbose) {
            Write-Host "   Workorder: $($json.workorder_id)" -ForegroundColor $Green
            Write-Host "   Status: $($json.status)" -ForegroundColor $Green
            $completedCount = ($json.agents | Where-Object { $_.status -eq "complete" }).Count
            Write-Host "   Agents: $completedCount/$($json.agents.Count) complete" -ForegroundColor $Green
        }
        $results.Valid += $relativePath
    } else {
        Write-Host "[FAIL] $relativePath" -ForegroundColor $Red

        # Parse validation errors
        $errorLines = $validationOutput | Where-Object { $_ -match "instancePath|message|allowedValues" }

        foreach ($line in $errorLines) {
            Write-Host "   $line" -ForegroundColor $Red
        }

        $results.Invalid += @{
            Path = $relativePath
            Error = $validationOutput -join "`n"
        }
    }

    Write-Host ""
}

# Summary
Write-Host ("=" * 60) -ForegroundColor $Cyan
Write-Host "`nSummary" -ForegroundColor $Cyan
Write-Host "   Total: $($commFiles.Count)" -ForegroundColor $Cyan
Write-Host "   Valid: $($results.Valid.Count)" -ForegroundColor $Green
Write-Host "   Invalid: $($results.Invalid.Count)" -ForegroundColor $Red

if ($results.Fixed.Count -gt 0) {
    Write-Host "   Fixed: $($results.Fixed.Count)" -ForegroundColor $Yellow
}

# Exit with error if any invalid
if ($results.Invalid.Count -gt 0) {
    Write-Host "`nValidation failed for $($results.Invalid.Count) file(s)" -ForegroundColor $Yellow
    Write-Host "Run with -FixTypos to automatically fix common status typos`n" -ForegroundColor $Yellow
    exit 1
} else {
    Write-Host "`nAll sessions valid!`n" -ForegroundColor $Green
    exit 0
}
