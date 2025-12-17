#!/usr/bin/env python3
"""Strip all emojis from coderef-system CLI source files."""
import os
import re

cli_src = r'C:\Users\willh\Desktop\projects\coderef-system\packages\cli\src'

# Common emojis used in the CLI
emojis_to_remove = [
    '🔍', '✅', '❌', '⚠️', '📊', '🔧', '💡', '🚀', '📁', '📄',
    '🔗', '✨', '🎯', '📋', '🔔', '💾', '🔄', '⏳', '🔎', '📦',
    '🎨', '🔥', '💥', '⭐', '🌟', '💪', '👍', '👎', '🤔', '😊',
    '🛠️', '📝', '🏷️', '🔒', '🔓', '⚡', '🌐', '📡', '🔀', '➡️',
    '⬅️', '⬆️', '⬇️', '↩️', '↪️', '🔃', '🔙', '🔚', '🔛', '🔜',
    '🔝', '✔️', '☑️', '🔘', '⚪', '⚫', '🔴', '🟢', '🟡', '🔵',
    '🟠', '🟣', '🟤', '⬛', '⬜', '◼️', '◻️', '◾', '◽', '▪️',
    '▫️', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💠', '🔲', '🔳'
]

files_updated = []

for root, dirs, files in os.walk(cli_src):
    for file in files:
        if file.endswith(('.ts', '.js')):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            for emoji in emojis_to_remove:
                new_content = new_content.replace(emoji, '')

            # Also handle unicode escapes like \u{1F50D}
            unicode_pattern = r'\\u\{[0-9A-Fa-f]+\}'
            new_content = re.sub(unicode_pattern, '', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                files_updated.append(os.path.relpath(filepath, cli_src))

print(f'Updated {len(files_updated)} files:')
for f in files_updated:
    print(f'  - {f}')
