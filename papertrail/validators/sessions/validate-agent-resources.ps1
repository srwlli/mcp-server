# validate-agent-resources.ps1
# Validates agent subdirectory structure in hierarchical multi-agent sessions
# Checks for required files: communication.json, instructions.json, resources/index.md, outputs/

param(
    [string]$SessionPath,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

Write-Host "`nAgent Resources Validation Report" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan

# Validate session path
if (-not $SessionPath) {
    Write-Host "`nUsage: .\validate-agent-resources.ps1 -SessionPath <path-to-session>" -ForegroundColor $Yellow
    Write-Host "Example: .\validate-agent-resources.ps1 -SessionPath 'C:\Users\willh\.mcp-servers\coderef\sessions\scanner-context-enhancement'" -ForegroundColor $Yellow
    exit 1
}

if (-not (Test-Path $SessionPath)) {
    Write-Host "`nSession path not found: $SessionPath" -ForegroundColor $Red
    exit 1
}

$sessionName = Split-Path $SessionPath -Leaf
Write-Host "`nValidating session: $sessionName" -ForegroundColor $Cyan
Write-Host "Path: $SessionPath`n" -ForegroundColor $Cyan

# Required structure for each agent subdirectory
$requiredFiles = @(
    "communication.json",
    "instructions.json"
)

$requiredDirs = @(
    "resources",
    "outputs"
)

$requiredResourceFiles = @(
    "resources\index.md"
)

# Find agent subdirectories (exclude root-level files)
$agentDirs = Get-ChildItem -Path $SessionPath -Directory |
    Where-Object { $_.Name -notmatch "^(\.|node_modules)" }

if ($agentDirs.Count -eq 0) {
    Write-Host "No agent subdirectories found - this may be a flat (non-hierarchical) session" -ForegroundColor $Yellow
    Write-Host "Skipping agent resource validation`n" -ForegroundColor $Yellow
    exit 0
}

Write-Host "Found $($agentDirs.Count) agent subdirectory(s)`n"

# Validation results
$results = @{
    Valid = @()
    Invalid = @()
    Warnings = @()
}

foreach ($agentDir in $agentDirs) {
    $agentId = $agentDir.Name
    $agentPath = $agentDir.FullName
    $issues = @()
    $warnings = @()

    Write-Host "Validating: $agentId" -ForegroundColor $Cyan

    # Check required files
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $agentPath $file
        if (-not (Test-Path $filePath)) {
            $issues += "Missing required file: $file"
        } elseif ($Verbose) {
            Write-Host "   [OK] $file" -ForegroundColor $Green
        }
    }

    # Check required directories
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $agentPath $dir
        if (-not (Test-Path $dirPath)) {
            $issues += "Missing required directory: $dir\"
        } elseif ($Verbose) {
            Write-Host "   [OK] $dir\" -ForegroundColor $Green
        }
    }

    # Check required resource files
    foreach ($file in $requiredResourceFiles) {
        $filePath = Join-Path $agentPath $file
        if (-not (Test-Path $filePath)) {
            $warnings += "Missing recommended file: $file"
        } elseif ($Verbose) {
            Write-Host "   [OK] $file" -ForegroundColor $Green
        }
    }

    # Validate resources/index.md format if it exists
    $resourceIndexPath = Join-Path $agentPath "resources\index.md"
    if (Test-Path $resourceIndexPath) {
        $indexContent = Get-Content $resourceIndexPath -Raw

        # Check for proper markdown structure
        if ($indexContent -notmatch "^# Resources Index") {
            $warnings += 'resources\index.md should start with "# Resources Index" header'
        }

        # Check that it contains links (not copies)
        if ($indexContent -match "```" -or $indexContent.Length -gt 5000) {
            $warnings += 'resources\index.md appears to contain copied content (should only have links)'
        }

        if ($Verbose -and $warnings.Count -eq 0) {
            Write-Host '   [OK] resources\index.md format' -ForegroundColor $Green
        }
    }

    # Display results for this agent
    if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
        Write-Host '   [PASS] All required files and directories present' -ForegroundColor $Green
        $results.Valid += $agentId
    } elseif ($issues.Count -eq 0) {
        Write-Host '   [WARN] Structure valid with warnings' -ForegroundColor $Yellow
        foreach ($warning in $warnings) {
            Write-Host "      $warning" -ForegroundColor $Yellow
        }
        $results.Warnings += @{
            Agent = $agentId
            Warnings = $warnings
        }
    } else {
        Write-Host '   [FAIL] Structure incomplete' -ForegroundColor $Red
        foreach ($issue in $issues) {
            Write-Host "      $issue" -ForegroundColor $Red
        }
        foreach ($warning in $warnings) {
            Write-Host "      $warning" -ForegroundColor $Yellow
        }
        $results.Invalid += @{
            Agent = $agentId
            Issues = $issues
            Warnings = $warnings
        }
    }

    Write-Host ""
}

# Summary
Write-Host ("=" * 60) -ForegroundColor $Cyan
Write-Host "`nSummary" -ForegroundColor $Cyan
Write-Host "   Total Agents: $($agentDirs.Count)" -ForegroundColor $Cyan
Write-Host "   Valid: $($results.Valid.Count)" -ForegroundColor $Green
Write-Host "   Warnings: $($results.Warnings.Count)" -ForegroundColor $Yellow
Write-Host "   Invalid: $($results.Invalid.Count)" -ForegroundColor $Red

# Exit with error if any invalid
if ($results.Invalid.Count -gt 0) {
    Write-Host "`nValidation failed for $($results.Invalid.Count) agent(s)" -ForegroundColor $Yellow
    Write-Host "Agents must have: communication.json, instructions.json, resources/, outputs/`n" -ForegroundColor $Yellow
    exit 1
} else {
    Write-Host "`nAll agent subdirectories valid!`n" -ForegroundColor $Green
    exit 0
}
