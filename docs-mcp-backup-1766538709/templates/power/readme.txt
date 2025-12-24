framework: POWER
purpose: Generate README.md as the discovery entry document.
# NOTE: Placeholders like {{readme_summary}} are for AI guidance only.
# They indicate which previous documents to reference but are not
# automatically substituted. The AI assistant will use them as
# context instructions.
output: Must follow required header/footer format with [Project Name], [Date], [Version], [Maintainer]. Include overview, quickstart steps, usage examples, prerequisites, and troubleshooting patterns.
work: Scan project root, configs, and entry points. Do not modify code.
examples:
- Installation command with sample output
- Common error message and resolution
requirements: Must include command sequences, decision trees, and AI-focused footer.
save_as: README.md
store_as: readme_summary
