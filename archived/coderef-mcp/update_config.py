#!/usr/bin/env python3
"""Update Claude Code config to add coderef2-mcp server."""

import json
import os

# Read current config
config_path = os.path.expanduser('~/.claude.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Get current project path (with proper escaping)
project_path = r'C:\Users\willh\Desktop\projects\coderef-system'

# Initialize project config if it doesn't exist
if project_path not in config.get('projects', {}):
    if 'projects' not in config:
        config['projects'] = {}
    config['projects'][project_path] = {
        'allowedTools': [],
        'history': [],
        'mcpContextUris': [],
        'mcpServers': {},
        'enabledMcpjsonServers': [],
        'disabledMcpjsonServers': [],
        'hasTrustDialogAccepted': False,
        'projectOnboardingSeenCount': 0,
        'hasClaudeMdExternalIncludesApproved': False,
        'hasClaudeMdExternalIncludesWarningShown': False
    }

# Add coderef2-mcp server to the current project
config['projects'][project_path]['mcpServers']['coderef2-mcp'] = {
    'command': 'python',
    'args': ['-m', 'server'],
    'cwd': r'C:\Users\willh\.mcp-servers\coderef2-mcp'
}

# Write back
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('✓ coderef2-mcp server added to project config')
print('✓ Restart Claude Code to load the server')
print(f'✓ Project: {project_path}')
