---
description: Archive files to assistant/coderef/archived/{project}/ organized by project
---

Run the archive script to move the provided file paths to the assistant archive.

**Script Location:** `C:\Users\willh\Desktop\assistant\scripts\archive\archive-files.ps1`

**How it works:**
- Extracts project name from file path (e.g., "coderef-dashboard" from path)
- Creates archive directory if needed: `assistant/coderef/archived/{project-name}/`
- Moves files to appropriate project folder
- Displays status for each file

**Usage:** User provides file paths as arguments to this command.

**Your task:**
1. Extract the file paths from the command arguments
2. Run: `powershell -ExecutionPolicy Bypass -File "C:\Users\willh\Desktop\assistant\scripts\archive\archive-files.ps1" "path1" "path2" ...`
3. Report the results to the user

**Important:** The script automatically detects project names from paths formatted as `C:\Users\willh\Desktop\{project-name}\...`
