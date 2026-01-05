# validate-resource-sheets.ps1
# Validates resource sheet naming conventions and UDS compliance

param(
    [Parameter(Mandatory=$false)]
    [string]$Path = ".",

    [switch]$ShowDetails,
    [switch]$FixNaming
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

Write-Host "`n🔍 Resource Sheet Validation" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan

# Find all resource sheets (REFERENCE-SHEET is deprecated)
$resourceSheets = @(Get-ChildItem -Path $Path -Recurse -Filter "*-RESOURCE-SHEET.md" -ErrorAction SilentlyContinue)
$deprecatedSheets = @(Get-ChildItem -Path $Path -Recurse -Filter "*-REFERENCE-SHEET.md" -ErrorAction SilentlyContinue)

# Warn about deprecated REFERENCE-SHEET files
if ($deprecatedSheets.Count -gt 0) {
    Write-Host "⚠️  Found $($deprecatedSheets.Count) deprecated REFERENCE-SHEET file(s):" -ForegroundColor $Yellow
    foreach ($sheet in $deprecatedSheets) {
        Write-Host "   - $($sheet.Name) (should be renamed to use -RESOURCE-SHEET)" -ForegroundColor $Yellow
    }
    Write-Host ""
}

$allSheets = @($resourceSheets)

if ($allSheets.Count -eq 0) {
    Write-Host "No resource sheets found in $Path" -ForegroundColor $Yellow
    if ($deprecatedSheets.Count -gt 0) {
        Write-Host "Note: Found deprecated REFERENCE-SHEET files. Please rename to -RESOURCE-SHEET.md" -ForegroundColor $Yellow
    }
    exit 0
}

Write-Host "Found $($allSheets.Count) resource sheet(s) to validate`n" -ForegroundColor $Cyan

# Validation tracking
$validationLog = @{
    TotalSheets = $allSheets.Count
    Passed = 0
    Failed = 0
    Warnings = 0
    Errors = @()
}

# UDS required headers
$requiredHeaders = @(
    "Executive Summary",
    "Audience & Intent",
    "Quick Reference"
)

function Test-YAMLFrontMatter {
    param($FilePath)

    $content = Get-Content $FilePath -Raw

    # Check if file starts with YAML front matter
    if (-not ($content -match "^---\r?\n")) {
        return @{
            Valid = $false
            Error = "Missing YAML front matter (must start with '---')"
        }
    }

    # Extract front matter (with multiline support)
    if ($content -match "(?s)^---\s*\r?\n(.*?)\r?\n---") {
        $frontMatter = $matches[1]

        # Check required UDS fields
        $requiredUDSFields = @("agent", "date", "task")
        $missingUDSFields = @()

        foreach ($field in $requiredUDSFields) {
            if (-not ($frontMatter -match "$field\s*:")) {
                $missingUDSFields += $field
            }
        }

        if ($missingUDSFields.Count -gt 0) {
            return @{
                Valid = $false
                Error = "Missing required UDS fields: $($missingUDSFields -join ', ')"
            }
        }

        # Check required RSMS v2.0 fields
        $requiredRSMSFields = @("subject", "parent_project", "category")
        $missingRSMSFields = @()

        foreach ($field in $requiredRSMSFields) {
            if (-not ($frontMatter -match "$field\s*:")) {
                $missingRSMSFields += $field
            }
        }

        if ($missingRSMSFields.Count -gt 0) {
            return @{
                Valid = $false
                Error = "Missing required RSMS v2.0 fields: $($missingRSMSFields -join ', ')"
            }
        }

        # Validate date format (YYYY-MM-DD)
        if ($frontMatter -match "date\s*:\s*(\S+)") {
            $date = $matches[1]
            if (-not ($date -match "^\d{4}-\d{2}-\d{2}$")) {
                return @{
                    Valid = $false
                    Error = "Invalid date format '$date' (must be YYYY-MM-DD)"
                }
            }
        }

        # Validate task enum
        if ($frontMatter -match "task\s*:\s*(\S+)") {
            $task = $matches[1]
            $validTasks = @("REVIEW", "CONSOLIDATE", "DOCUMENT", "UPDATE", "CREATE")
            if ($task -notin $validTasks) {
                return @{
                    Valid = $false
                    Error = "Invalid task '$task' (must be one of: $($validTasks -join ', '))"
                }
            }
        }

        # Validate category enum
        if ($frontMatter -match "category\s*:\s*(\S+)") {
            $category = $matches[1]
            $validCategories = @("service", "controller", "model", "utility", "integration", "component", "middleware", "validator", "schema", "config", "other")
            if ($category -notin $validCategories) {
                return @{
                    Valid = $false
                    Error = "Invalid category '$category' (must be one of: $($validCategories -join ', '))"
                }
            }
        }

        # Validate version format (semver) if present
        if ($frontMatter -match "version\s*:\s*(\S+)") {
            $version = $matches[1]
            if (-not ($version -match "^\d+\.\d+\.\d+$")) {
                return @{
                    Valid = $false
                    Error = "Invalid version format '$version' (must be semver: X.Y.Z)"
                }
            }
        }

        # Validate related_files format if present
        if ($frontMatter -match "related_files\s*:") {
            # Extract list items (lines starting with - under related_files)
            $fileLines = ($frontMatter -split "`n") | Where-Object { $_ -match "^\s*-\s*(.+)" }
            foreach ($line in $fileLines) {
                if ($line -match "^\s*-\s*(.+)") {
                    $file = $matches[1].Trim()
                    if (-not ($file -match "^[a-zA-Z0-9/_.-]+\.[a-zA-Z0-9]+$")) {
                        return @{
                            Valid = $false
                            Error = "Invalid file path format in related_files: '$file' (must be valid file path with extension)"
                        }
                    }
                }
            }
        }

        # Validate related_docs format if present
        if ($frontMatter -match "related_docs\s*:") {
            # Extract list items (lines starting with - under related_docs)
            $docLines = ($frontMatter -split "`n") | Where-Object { $_ -match "^\s*-\s*(.+\.md)" }
            foreach ($line in $docLines) {
                if ($line -match "^\s*-\s*(.+)") {
                    $doc = $matches[1].Trim()
                    if (-not ($doc -match "^[a-zA-Z0-9/_.-]+\.md$")) {
                        return @{
                            Valid = $false
                            Error = "Invalid doc path format in related_docs: '$doc' (must end with .md)"
                        }
                    }
                }
            }
        }

        return @{ Valid = $true }

    } else {
        return @{
            Valid = $false
            Error = "Malformed YAML front matter (missing closing '---')"
        }
    }
}

function Test-NamingConvention {
    param($FilePath)

    $fileName = Split-Path $FilePath -Leaf
    $content = Get-Content $FilePath -Raw

    # Extract component name from filename
    if ($fileName -match "^(.+?)-RESOURCE-SHEET\.md$") {
        $fileComponent = $matches[1]

        # Check if subject/component name appears in YAML front matter
        # First try 'subject' (RSMS v2.0), then fall back to deprecated 'component'
        $yamlSubject = $null
        if ($content -match "subject\s*:\s*(\S+)") {
            $yamlSubject = $matches[1]
        } elseif ($content -match "component\s*:\s*(\S+)") {
            $yamlSubject = $matches[1]
        }

        if ($yamlSubject -and ($fileComponent -ne $yamlSubject)) {
            return @{
                Valid = $false
                Error = "Filename component '$fileComponent' doesn't match YAML subject '$yamlSubject'"
                Suggestion = "Rename to: $yamlSubject-RESOURCE-SHEET.md"
            }
        }

        return @{ Valid = $true }

    } else {
        return @{
            Valid = $false
            Error = "Filename must match pattern: {ComponentName}-RESOURCE-SHEET.md (Note: REFERENCE-SHEET is deprecated)"
        }
    }
}

function Test-UDSHeaders {
    param($FilePath)

    $content = Get-Content $FilePath -Raw
    $missingHeaders = @()

    foreach ($header in $requiredHeaders) {
        # Check for markdown header (# or ##)
        if (-not ($content -match "^#{1,2}\s+$header" -or $content -match "\n#{1,2}\s+$header")) {
            $missingHeaders += $header
        }
    }

    if ($missingHeaders.Count -gt 0) {
        return @{
            Valid = $false
            Error = "Missing UDS-compliant headers: $($missingHeaders -join ', ')"
        }
    }

    return @{ Valid = $true }
}

# Validate each sheet
foreach ($sheet in $allSheets) {
    $sheetName = $sheet.Name
    $passed = $true
    $issues = @()

    Write-Host "Validating: $sheetName" -ForegroundColor $Cyan

    # Test 1: YAML front matter
    $yamlResult = Test-YAMLFrontMatter -FilePath $sheet.FullName
    if (-not $yamlResult.Valid) {
        $passed = $false
        $issues += "  [YAML] $($yamlResult.Error)"
        Write-Host "  ❌ YAML Front Matter: $($yamlResult.Error)" -ForegroundColor $Red
    } else {
        Write-Host "  ✅ YAML Front Matter" -ForegroundColor $Green
    }

    # Test 2: Naming convention
    $namingResult = Test-NamingConvention -FilePath $sheet.FullName
    if (-not $namingResult.Valid) {
        $passed = $false
        $issues += "  [NAMING] $($namingResult.Error)"
        Write-Host "  ❌ Naming Convention: $($namingResult.Error)" -ForegroundColor $Red

        if ($namingResult.Suggestion) {
            Write-Host "     💡 Suggestion: $($namingResult.Suggestion)" -ForegroundColor $Yellow
        }
    } else {
        Write-Host "  ✅ Naming Convention" -ForegroundColor $Green
    }

    # Test 3: UDS headers
    $udsResult = Test-UDSHeaders -FilePath $sheet.FullName
    if (-not $udsResult.Valid) {
        $validationLog.Warnings++
        $issues += "  [UDS] $($udsResult.Error)"
        Write-Host "  ⚠️  UDS Headers: $($udsResult.Error)" -ForegroundColor $Yellow
    } else {
        Write-Host "  ✅ UDS Headers" -ForegroundColor $Green
    }

    # Update totals
    if ($passed) {
        $validationLog.Passed++
        Write-Host "  ✅ PASSED`n" -ForegroundColor $Green
    } else {
        $validationLog.Failed++
        $validationLog.Errors += @{
            File = $sheetName
            Issues = $issues
        }
        Write-Host "  ❌ FAILED`n" -ForegroundColor $Red
    }
}

# Summary
Write-Host ("=" * 60) -ForegroundColor $Cyan
Write-Host "📊 Validation Summary" -ForegroundColor $Cyan
Write-Host ("=" * 60) -ForegroundColor $Cyan
Write-Host "   Total Sheets: $($validationLog.TotalSheets)" -ForegroundColor $Cyan
Write-Host "   ✅ Passed: $($validationLog.Passed)" -ForegroundColor $Green
Write-Host "   ❌ Failed: $($validationLog.Failed)" -ForegroundColor $Red
Write-Host "   ⚠️  Warnings: $($validationLog.Warnings)" -ForegroundColor $Yellow

if ($validationLog.Failed -gt 0) {
    Write-Host "`n❌ Validation failed for $($validationLog.Failed) file(s)" -ForegroundColor $Red
    Write-Host "Fix errors and re-run validation" -ForegroundColor $Red
    exit 1
} else {
    Write-Host "`n✅ All resource sheets valid!" -ForegroundColor $Green
    exit 0
}
