● Here are all 39 tools in docs-mcp:

  | #   | Tool Name                      | Category          |
  |-----|--------------------------------|-------------------|
  | 1   | list_templates                 | Documentation     |
  | 2   | get_template                   | Documentation     |
  | 3   | generate_foundation_docs       | Documentation     |
  | 4   | generate_individual_doc        | Documentation     |
  | 5   | get_changelog                  | Changelog         |
  | 6   | add_changelog_entry            | Changelog         |
  | 7   | update_changelog               | Changelog         |
  | 8   | generate_quickref_interactive  | Documentation     |
  | 9   | establish_standards            | Standards         |
  | 10  | audit_codebase                 | Standards         |
  | 11  | check_consistency              | Standards         |
  | 12  | get_planning_template          | Planning          |
  | 13  | analyze_project_for_planning   | Planning          |
  | 14  | gather_context                 | Planning          |
  | 15  | validate_implementation_plan   | Planning          |
  | 16  | generate_plan_review_report    | Planning          |
  | 17  | create_plan                    | Planning          |
  | 18  | inventory_manifest             | Inventory         |
  | 19  | dependency_inventory           | Inventory         |
  | 20  | api_inventory                  | Inventory         |
  | 21  | database_inventory             | Inventory         |
  | 22  | config_inventory               | Inventory         |
  | 23  | test_inventory                 | Inventory         |
  | 24  | documentation_inventory        | Inventory         |
  | 25  | generate_deliverables_template | Deliverables      |
  | 26  | update_deliverables            | Deliverables      |
  | 27  | generate_agent_communication   | Multi-Agent       |
  | 28  | assign_agent_task              | Multi-Agent       |
  | 29  | verify_agent_completion        | Multi-Agent       |
  | 30  | aggregate_agent_deliverables   | Multi-Agent       |
  | 31  | track_agent_status             | Multi-Agent       |
  | 32  | archive_feature                | Feature Lifecycle |
  | 33  | update_all_documentation       | Agentic           |
  | 34  | execute_plan                   | Execution         |
  | 35  | log_workorder                  | Workorder         |
  | 36  | get_workorder_log              | Workorder         |
  | 37  | generate_handoff_context       | Handoff           |
  | 38  | assess_risk                    | Risk Assessment   |
  | 39  | consolidate_llm_outputs        | LLM Workflow      |

> slash commands list? 

● Search(pattern: "**/*.md", path: "docs-mcp\.claude\commands")
  ⎿  Found 45 files (ctrl+o to expand)

● Search(pattern: "**/*.md", path: "~\.claude\commands")
  ⎿  Found 64 files (ctrl+o to expand)

● docs-mcp Local Commands (44 total, excluding README):

  | Category          | Commands                                                                                                                                                        |
  |-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | Documentation     | /generate-docs, /generate-user-guide, /generate-my-guide, /generate-quickref, /list-templates, /get-template, /update-foundation-docs                           |
  | Changelog         | /get-changelog, /add-changelog, /update-changelog                                                                                                               |
  | Standards         | /establish-standards, /audit-codebase, /check-consistency                                                                                                       |
  | Planning          | /get-planning-template, /analyze-for-planning, /gather-context, /create-plan, /validate-plan, /generate-plan-review                                             |
  | Inventory         | /inventory-manifest, /dependency-inventory, /api-inventory, /database-inventory, /config-inventory, /test-inventory, /documentation-inventory, /quick-inventory |
  | Deliverables      | /generate-deliverables, /update-deliverables                                                                                                                    |
  | Multi-Agent       | /generate-agent-communication, /assign-agent-task, /verify-agent-completion, /aggregate-agent-deliverables, /track-agent-status                                 |
  | Feature Lifecycle | /archive-feature, /create-workorder, /execute-plan                                                                                                                 |
  | Workorder         | /log-workorder, /get-workorder-log                                                                                                                              |
  | Handoff           | /generate-handoff-context                                                                                                                                       |
  | LLM Workflow      | /llm-prompt, /consolidate                                                                                                                                       |
  | Misc              | /update-docs, /stub                                                                                                                                             |

  ---
  Global Commands (~64 total, excluding README):

  | Category              | Commands                                                                                                    |
  |-----------------------|-------------------------------------------------------------------------------------------------------------|
  | Personas              | /lloyd, /ava, /taylor, /devon, /marcus, /quinn, /use-persona                                                |
  | Experts               | /docs-expert, /coderef-expert, /nfl-scraper-expert                                                          |
  | CodeRef               | /coderef-query, /coderef-analyze, /coderef-audit, /coderef-validate, /coderef-batch-validate, /coderef-docs |
  | docs-mcp (duplicates) | All 44 from above are also globally available                                                               |
  | Utility               | /list-tools, /list-commands, /handoff, /prompt-workflow                                                     |