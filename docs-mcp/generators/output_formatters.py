"""
Output Formatters - Generate JSON, Markdown, and HTML from consolidated LLM responses.

Part of the llm-workflow feature (WO-LLM-WORKFLOW-001).
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


def format_json(consolidated: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format consolidated results as JSON.

    Args:
        consolidated: Output from consolidate_responses()
        pretty: Whether to indent for readability

    Returns:
        JSON string
    """
    indent = 2 if pretty else None
    return json.dumps(consolidated, indent=indent, default=str)


def format_markdown(consolidated: Dict[str, Any], topic: str = "LLM Consolidation") -> str:
    """
    Format consolidated results as Markdown.

    Args:
        consolidated: Output from consolidate_responses()
        topic: Title for the document

    Returns:
        Markdown string
    """
    lines = []
    metadata = consolidated.get('metadata', {})
    summary = consolidated.get('summary', {})
    findings = consolidated.get('findings', {})
    recommendations = consolidated.get('recommendations', {})
    risks = consolidated.get('risks', {})
    conflicts = consolidated.get('conflicts', [])
    ranked_actions = consolidated.get('ranked_actions', [])

    # Header
    lines.append(f"# Consolidated: {topic}")
    lines.append("")
    lines.append(f"**Sources:** {', '.join(metadata.get('sources', []))}")
    lines.append(f"**Date:** {metadata.get('consolidated_at', datetime.now().isoformat())[:10]}")
    lines.append("")

    # Summary stats
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Findings:** {summary.get('total_findings', 0)}")
    lines.append(f"- **Unique Insights:** {summary.get('unique_insights', 0)}")
    lines.append(f"- **Recommendations:** {summary.get('total_recommendations', 0)}")
    lines.append(f"- **Risks Identified:** {summary.get('total_risks', 0)}")
    lines.append(f"- **Conflicts to Resolve:** {summary.get('conflicts_found', 0)}")
    if summary.get('avg_confidence'):
        lines.append(f"- **Average Confidence:** {summary['avg_confidence']}%")
    lines.append("")

    # Findings by severity
    if findings.get('by_severity'):
        lines.append("## Findings by Severity")
        lines.append("")
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_findings = findings['by_severity'].get(severity, [])
            if severity_findings:
                lines.append(f"### {severity.upper()}")
                lines.append("")
                for f in severity_findings:
                    sources_str = ", ".join(f.get('sources', []))
                    unique_marker = " *(unique)*" if f.get('is_unique') else ""
                    lines.append(f"- **{f.get('category', 'General')}**: {f.get('description', 'No description')}{unique_marker}")
                    if f.get('location'):
                        lines.append(f"  - Location: `{f['location']}`")
                    lines.append(f"  - Sources: {sources_str}")
                lines.append("")

    # Unique insights
    unique_insights = findings.get('unique_insights', [])
    if unique_insights:
        lines.append("## Unique Insights")
        lines.append("")
        lines.append("*These were only mentioned by one LLM - worth extra attention:*")
        lines.append("")
        for insight in unique_insights:
            f = insight['finding']
            lines.append(f"- **{f.get('description', 'No description')}** - only {insight['source']} caught this")
        lines.append("")

    # Recommendations
    all_recs = recommendations.get('all_recommendations', [])
    if all_recs:
        lines.append("## Recommendations")
        lines.append("")
        for rec in all_recs:
            priority = rec.get('priority', 'medium')
            effort = rec.get('effort', 'medium')
            agreement = rec.get('agreement_count', 1)
            sources_str = ", ".join(rec.get('sources', []))
            agreement_str = f" ({agreement} LLMs agree)" if agreement > 1 else ""

            lines.append(f"- **[{priority.upper()}]** {rec.get('description', 'No description')}{agreement_str}")
            lines.append(f"  - Effort: {effort} | Sources: {sources_str}")
        lines.append("")

    # Risks
    all_risks = risks.get('all_risks', [])
    if all_risks:
        lines.append("## Risks")
        lines.append("")
        for risk in all_risks:
            severity = risk.get('severity', 'medium')
            likelihood = risk.get('likelihood', 'medium')
            sources_str = ", ".join(risk.get('sources', []))

            lines.append(f"- **{severity.upper()} risk** (likelihood: {likelihood}): {risk.get('description', 'No description')}")
            lines.append(f"  - Sources: {sources_str}")
        lines.append("")

    # Conflicts
    if conflicts:
        lines.append("## Conflicts to Resolve")
        lines.append("")
        lines.append("*Different LLMs gave conflicting advice on these topics:*")
        lines.append("")
        for conflict in conflicts:
            lines.append(f"### {conflict.get('topic', 'Unknown topic')}")
            lines.append(f"Type: {conflict.get('type', 'unknown')}")
            lines.append("")
            for rec in conflict.get('recommendations', []):
                lines.append(f"- {rec.get('description', 'No description')} (priority: {rec.get('priority', 'unknown')})")
            lines.append("")

    # Ranked actions
    if ranked_actions:
        lines.append("## Recommended Action Priority")
        lines.append("")
        for action in ranked_actions[:10]:  # Top 10
            rank = action.get('consolidated_rank', '?')
            agreement = action.get('agreement_count', 1)
            impact = action.get('impact', 'medium')
            sources_str = ", ".join(action.get('sources', []))

            agreement_str = f" ({agreement} LLMs)" if agreement > 1 else ""
            lines.append(f"{rank}. **{action.get('action', 'No action')}**{agreement_str}")
            lines.append(f"   - Impact: {impact} | Reason: {action.get('reason', 'Not specified')}")
        lines.append("")

    return "\n".join(lines)


def format_html(consolidated: Dict[str, Any], topic: str = "LLM Consolidation") -> str:
    """
    Format consolidated results as HTML with visual styling.

    Args:
        consolidated: Output from consolidate_responses()
        topic: Title for the document

    Returns:
        HTML string
    """
    metadata = consolidated.get('metadata', {})
    summary = consolidated.get('summary', {})
    findings = consolidated.get('findings', {})
    recommendations = consolidated.get('recommendations', {})
    risks = consolidated.get('risks', {})
    conflicts = consolidated.get('conflicts', [])
    ranked_actions = consolidated.get('ranked_actions', [])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated: {topic}</title>
    <style>
        :root {{
            --critical: #dc2626;
            --high: #ea580c;
            --medium: #ca8a04;
            --low: #16a34a;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .meta {{ color: var(--muted); margin-bottom: 2rem; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; }}
        .stat-label {{ color: var(--muted); font-size: 0.875rem; }}
        section {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        h2 {{ font-size: 1.25rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border); }}
        .badge {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-critical {{ background: #fef2f2; color: var(--critical); }}
        .badge-high {{ background: #fff7ed; color: var(--high); }}
        .badge-medium {{ background: #fefce8; color: var(--medium); }}
        .badge-low {{ background: #f0fdf4; color: var(--low); }}
        .finding-item {{
            border-left: 4px solid var(--border);
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            background: var(--bg);
            border-radius: 0 4px 4px 0;
        }}
        .finding-item.critical {{ border-left-color: var(--critical); }}
        .finding-item.high {{ border-left-color: var(--high); }}
        .finding-item.medium {{ border-left-color: var(--medium); }}
        .finding-item.low {{ border-left-color: var(--low); }}
        .finding-header {{ display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.25rem; }}
        .finding-sources {{ color: var(--muted); font-size: 0.75rem; }}
        .unique-tag {{ background: #dbeafe; color: #1d4ed8; padding: 0.125rem 0.375rem; border-radius: 4px; font-size: 0.625rem; }}
        .action-item {{
            display: flex;
            gap: 1rem;
            padding: 0.75rem;
            background: var(--bg);
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }}
        .action-rank {{
            background: #3b82f6;
            color: white;
            width: 2rem;
            height: 2rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .action-content {{ flex: 1; }}
        .agreement {{ color: var(--muted); font-size: 0.75rem; }}
        .conflict-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        .empty-state {{ color: var(--muted); font-style: italic; text-align: center; padding: 2rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Consolidated: {topic}</h1>
        <p class="meta">
            Sources: {', '.join(metadata.get('sources', []))} |
            Generated: {metadata.get('consolidated_at', '')[:10]}
        </p>

        <div class="summary-grid">
            <div class="stat-card">
                <div class="stat-value">{summary.get('total_findings', 0)}</div>
                <div class="stat-label">Total Findings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('unique_insights', 0)}</div>
                <div class="stat-label">Unique Insights</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('total_recommendations', 0)}</div>
                <div class="stat-label">Recommendations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('total_risks', 0)}</div>
                <div class="stat-label">Risks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('conflicts_found', 0)}</div>
                <div class="stat-label">Conflicts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('avg_confidence', '-') or '-'}{'%' if summary.get('avg_confidence') else ''}</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        </div>
"""

    # Findings section
    html += '<section><h2>Findings</h2>'
    all_findings = findings.get('all_findings', [])
    if all_findings:
        for f in all_findings:
            severity = f.get('severity', 'medium')
            sources_str = ", ".join(f.get('sources', []))
            unique_tag = '<span class="unique-tag">UNIQUE</span>' if f.get('is_unique') else ''

            html += f'''
            <div class="finding-item {severity}">
                <div class="finding-header">
                    <span class="badge badge-{severity}">{severity}</span>
                    <strong>{f.get('category', 'General')}</strong>
                    {unique_tag}
                </div>
                <div>{f.get('description', 'No description')}</div>
                <div class="finding-sources">Sources: {sources_str}</div>
            </div>'''
    else:
        html += '<div class="empty-state">No findings reported</div>'
    html += '</section>'

    # Ranked actions section
    html += '<section><h2>Recommended Actions</h2>'
    if ranked_actions:
        for action in ranked_actions[:10]:
            rank = action.get('consolidated_rank', '?')
            agreement = action.get('agreement_count', 1)
            agreement_text = f"({agreement} LLMs agree)" if agreement > 1 else ""

            html += f'''
            <div class="action-item">
                <div class="action-rank">{rank}</div>
                <div class="action-content">
                    <strong>{action.get('action', 'No action')}</strong>
                    <span class="agreement">{agreement_text}</span>
                    <div style="color: var(--muted); font-size: 0.875rem;">
                        Impact: {action.get('impact', 'medium')} | {action.get('reason', '')}
                    </div>
                </div>
            </div>'''
    else:
        html += '<div class="empty-state">No actions recommended</div>'
    html += '</section>'

    # Conflicts section
    if conflicts:
        html += '<section><h2>Conflicts to Resolve</h2>'
        for conflict in conflicts:
            html += f'''
            <div class="conflict-box">
                <strong>{conflict.get('topic', 'Unknown')}</strong>
                <div style="color: var(--muted); font-size: 0.875rem;">
                    Type: {conflict.get('type', 'unknown')} |
                    Sources: {', '.join(conflict.get('sources', []))}
                </div>
            </div>'''
        html += '</section>'

    html += """
    </div>
</body>
</html>"""

    return html


def save_outputs(
    consolidated: Dict[str, Any],
    output_dir: Path,
    formats: List[str],
    base_name: str = "consolidated"
) -> Dict[str, str]:
    """
    Save consolidated output in requested formats.

    Args:
        consolidated: Output from consolidate_responses()
        output_dir: Directory to save files
        formats: List of formats - any of ["json", "markdown", "html"]
        base_name: Base filename without extension

    Returns:
        Dict mapping format to saved file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = {}

    topic = "LLM Consolidation"  # Could extract from consolidated data

    if "json" in formats:
        json_path = output_dir / f"{base_name}.json"
        json_path.write_text(format_json(consolidated), encoding='utf-8')
        saved_files["json"] = str(json_path)

    if "markdown" in formats or "md" in formats:
        md_path = output_dir / f"{base_name}.md"
        md_path.write_text(format_markdown(consolidated, topic), encoding='utf-8')
        saved_files["markdown"] = str(md_path)

    if "html" in formats:
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(format_html(consolidated, topic), encoding='utf-8')
        saved_files["html"] = str(html_path)

    return saved_files
