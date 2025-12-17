# Create desktop shortcut with icon for MCP Clipboard
$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = "$env:USERPROFILE\Desktop\LLM Response Collector.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\willh\.mcp-servers\docs-mcp\coderef\working\mcp-dash\dist\MCP-Clipboard.exe"
$Shortcut.WorkingDirectory = "C:\Users\willh\.mcp-servers\docs-mcp\coderef\working\mcp-dash"
$Shortcut.Description = "Collect LLM responses and code for review workflows"
# Use a clipboard icon from imageres.dll (index 260 is a document with arrow)
$Shortcut.IconLocation = "C:\Windows\System32\imageres.dll,260"
$Shortcut.Save()

# Remove old shortcut if it exists
$OldShortcut = "$env:USERPROFILE\Desktop\MCP-Clipboard.lnk"
if (Test-Path $OldShortcut) {
    Remove-Item $OldShortcut -Force
    Write-Host "Removed old shortcut"
}

Write-Host "Desktop shortcut created: LLM Response Collector"
