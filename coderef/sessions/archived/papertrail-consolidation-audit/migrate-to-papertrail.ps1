# migrate-to-papertrail.ps1
# Migrates validation/schema/standards files to papertrail based on orchestrator-migration-manifest.json

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Red = "Red"

Write-Host "`nPapertrail Migration Script" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan

if ($DryRun) {
    Write-Host "[DRY RUN MODE] - No files will be copied`n" -ForegroundColor $Yellow
}

# Paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $scriptDir "orchestrator-migration-manifest.json"
$papertrailRoot = "C:\Users\willh\.mcp-servers\papertrail"

# Verify manifest exists
if (-not (Test-Path $manifestPath)) {
    Write-Host "ERROR: Manifest not found: $manifestPath" -ForegroundColor $Red
    exit 1
}

# Load manifest
Write-Host "Loading migration manifest..." -ForegroundColor $Cyan
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

# Project root paths
$projectRoots = @{
    "coderef-workflow" = "C:\Users\willh\.mcp-servers\coderef-workflow"
    "coderef-testing" = "C:\Users\willh\.mcp-servers\coderef-testing"
    "coderef-packages" = "C:\Users\willh\Desktop\projects\coderef-system\packages"
    "coderef-context" = "C:\Users\willh\.mcp-servers\coderef-context"
    "papertrail" = $papertrailRoot
}

# Migration tracking
$migrationLog = @{
    TotalFiles = 0
    Copied = 0
    Skipped = 0
    Failed = 0
    Errors = @()
}

# Helper: Resolve file path
function Resolve-SourcePath {
    param($fileRef, $projectName)

    # Extract relative path from file reference
    if ($fileRef -is [string]) {
        $relativePath = $fileRef
    } else {
        $relativePath = $fileRef.file
    }

    # Remove project prefix if present
    $relativePath = $relativePath -replace "^$projectName/", ""

    # Join with project root
    $projectRoot = $projectRoots[$projectName]
    if (-not $projectRoot) {
        throw "Unknown project: $projectName"
    }

    $fullPath = Join-Path $projectRoot $relativePath
    return $fullPath
}

# Helper: Copy file with directory creation
function Copy-MigrationFile {
    param(
        [string]$SourcePath,
        [string]$DestPath,
        [string]$Phase,
        [switch]$DryRun
    )

    $migrationLog.TotalFiles++

    if (-not (Test-Path $SourcePath)) {
        Write-Host "[SKIP] Source not found: $SourcePath" -ForegroundColor $Yellow
        $migrationLog.Skipped++
        $migrationLog.Errors += "Source not found: $SourcePath"
        return $false
    }

    $destDir = Split-Path -Parent $DestPath

    if ($DryRun) {
        Write-Host "[DRY RUN] Would copy:" -ForegroundColor $Yellow
        Write-Host "   FROM: $SourcePath" -ForegroundColor $Cyan
        Write-Host "   TO:   $DestPath" -ForegroundColor $Cyan
        Write-Host "   PHASE: $Phase" -ForegroundColor $Cyan
        $migrationLog.Copied++
        return $true
    }

    try {
        # Create destination directory
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            Write-Host "[MKDIR] $destDir" -ForegroundColor $Green
        }

        # Copy file
        Copy-Item -Path $SourcePath -Destination $DestPath -Force
        Write-Host "[COPY] $SourcePath -> $DestPath" -ForegroundColor $Green
        $migrationLog.Copied++
        return $true

    } catch {
        Write-Host "[FAIL] Error copying $SourcePath : $_" -ForegroundColor $Red
        $migrationLog.Failed++
        $migrationLog.Errors += "Failed to copy $SourcePath : $_"
        return $false
    }
}

# Phase 1: Security Validation Schema
Write-Host "`n[PHASE 1] Security Validation Schema" -ForegroundColor $Cyan
Write-Host ("-" * 60) -ForegroundColor $Cyan

$phase1Files = @(
    @{
        Source = "coderef-workflow/coderef/schemas/validation-schema.json"
        Dest = "$papertrailRoot/schemas/security/validation-schema.json"
        Project = "coderef-workflow"
    }
)

foreach ($file in $phase1Files) {
    $sourcePath = Resolve-SourcePath $file.Source $file.Project
    Copy-MigrationFile -SourcePath $sourcePath -DestPath $file.Dest -Phase "PHASE 1" -DryRun:$DryRun
}

# Phase 3: Core MCP Schemas
Write-Host "`n[PHASE 3] Core MCP Schemas" -ForegroundColor $Cyan
Write-Host ("-" * 60) -ForegroundColor $Cyan

$phase3Files = @(
    "error-responses-schema.json",
    "server-schema.json",
    "tool-handlers-schema.json",
    "mcp-client-schema.json",
    "type-defs-schema.json"
)

foreach ($fileName in $phase3Files) {
    $sourcePath = Resolve-SourcePath "coderef/schemas/$fileName" "coderef-workflow"
    $destPath = "$papertrailRoot/schemas/mcp/$fileName"
    Copy-MigrationFile -SourcePath $sourcePath -DestPath $destPath -Phase "PHASE 3" -DryRun:$DryRun
}

# Phase 6: Planning Schemas
Write-Host "`n[PHASE 6] Planning Schemas" -ForegroundColor $Cyan
Write-Host ("-" * 60) -ForegroundColor $Cyan

$phase6Files = @(
    "plan.schema.json",
    "planning-analyzer-schema.json",
    "planning-generator-schema.json",
    "plan-validator-schema.json",
    "constants-schema.json"
)

foreach ($fileName in $phase6Files) {
    $sourcePath = Resolve-SourcePath "coderef/schemas/$fileName" "coderef-workflow"
    $destPath = "$papertrailRoot/schemas/planning/$fileName"
    Copy-MigrationFile -SourcePath $sourcePath -DestPath $destPath -Phase "PHASE 6" -DryRun:$DryRun
}

# Phase 7: Plan Validators
Write-Host "`n[PHASE 7] Plan Validators" -ForegroundColor $Cyan
Write-Host ("-" * 60) -ForegroundColor $Cyan

$phase7Files = @(
    @{ File = "generators/plan_validator.py"; Dest = "validators/planning/plan_validator.py" },
    @{ File = "plan_format_validator.py"; Dest = "validators/planning/plan_format_validator.py" },
    @{ File = "schema_validator.py"; Dest = "validators/planning/schema_validator.py" }
)

foreach ($file in $phase7Files) {
    $sourcePath = Resolve-SourcePath $file.File "coderef-workflow"
    $destPath = "$papertrailRoot/$($file.Dest)"
    Copy-MigrationFile -SourcePath $sourcePath -DestPath $destPath -Phase "PHASE 7" -DryRun:$DryRun
}

# Phase 4: Test Infrastructure
Write-Host "`n[PHASE 4] Test Infrastructure" -ForegroundColor $Cyan
Write-Host ("-" * 60) -ForegroundColor $Cyan

$phase4Files = @(
    @{ File = "src/models.py"; Dest = "test-infrastructure/models.py" },
    @{ File = "src/result_analyzer.py"; Dest = "test-infrastructure/result_analyzer.py" },
    @{ File = "src/test_runner.py"; Dest = "test-infrastructure/test_runner.py" },
    @{ File = "src/test_aggregator.py"; Dest = "test-infrastructure/test_aggregator.py" },
    @{ File = "src/framework_detector.py"; Dest = "test-infrastructure/framework_detector.py" },
    @{ File = "TESTING_GUIDE.md"; Dest = "test-infrastructure/docs/TESTING_GUIDE.md" },
    @{ File = "coderef/user/USER-GUIDE.md"; Dest = "test-infrastructure/docs/USER-GUIDE.md" },
    @{ File = "coderef/foundation-docs/ARCHITECTURE.md"; Dest = "test-infrastructure/docs/ARCHITECTURE.md" },
    @{ File = "coderef/foundation-docs/SCHEMA.md"; Dest = "test-infrastructure/docs/SCHEMA.md" }
)

foreach ($file in $phase4Files) {
    $sourcePath = Resolve-SourcePath $file.File "coderef-testing"
    $destPath = "$papertrailRoot/$($file.Dest)"
    Copy-MigrationFile -SourcePath $sourcePath -DestPath $destPath -Phase "PHASE 4" -DryRun:$DryRun
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor $Cyan
Write-Host "Migration Summary" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan
Write-Host "   Total Files: $($migrationLog.TotalFiles)" -ForegroundColor $Cyan
Write-Host "   Copied: $($migrationLog.Copied)" -ForegroundColor $Green
Write-Host "   Skipped: $($migrationLog.Skipped)" -ForegroundColor $Yellow
Write-Host "   Failed: $($migrationLog.Failed)" -ForegroundColor $Red

if ($migrationLog.Errors.Count -gt 0) {
    Write-Host "`nErrors:" -ForegroundColor $Red
    foreach ($error in $migrationLog.Errors) {
        Write-Host "   - $error" -ForegroundColor $Red
    }
}

if ($DryRun) {
    Write-Host "`n[DRY RUN COMPLETE] Run without -DryRun to perform actual migration" -ForegroundColor $Yellow
} else {
    Write-Host "`n[MIGRATION COMPLETE]" -ForegroundColor $Green
}

# Create migration log file
$logPath = Join-Path $scriptDir "migration-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$migrationLog | ConvertTo-Json -Depth 10 | Set-Content $logPath
Write-Host "`nLog saved to: $logPath" -ForegroundColor $Cyan

if ($migrationLog.Failed -gt 0) {
    exit 1
} else {
    exit 0
}
