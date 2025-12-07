"""
Consolidation Engine - Merge and synthesize multiple LLM responses.

Part of the llm-workflow feature (WO-LLM-WORKFLOW-001).
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict


def normalize_severity(severity: str) -> str:
    """Normalize severity values to standard levels."""
    severity = severity.lower().strip()
    if severity in ['critical', 'crit']:
        return 'critical'
    elif severity in ['high', 'hi']:
        return 'high'
    elif severity in ['medium', 'med', 'moderate']:
        return 'medium'
    elif severity in ['low', 'lo', 'minor']:
        return 'low'
    return severity


def calculate_finding_hash(finding: Dict[str, Any]) -> str:
    """Generate a hash key for deduplication based on finding content."""
    category = finding.get('category', '').lower().strip()
    description = finding.get('description', '').lower().strip()
    # Use first 50 chars of description to allow for slight variations
    desc_key = description[:50] if len(description) > 50 else description
    return f"{category}:{desc_key}"


def merge_findings(parsed_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge findings from multiple LLM responses.

    Returns dict with:
    - all_findings: deduplicated list with source attribution
    - by_category: findings grouped by category
    - by_severity: findings grouped by severity
    - unique_insights: findings only mentioned by one LLM
    - source_counts: how many findings each source contributed
    """
    findings_map = defaultdict(lambda: {'sources': set(), 'data': None})
    source_counts = defaultdict(int)

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})
        findings = data.get('findings', [])

        for finding in findings:
            finding_hash = calculate_finding_hash(finding)
            findings_map[finding_hash]['sources'].add(source)
            findings_map[finding_hash]['data'] = finding
            source_counts[source] += 1

    # Convert to list with source attribution
    all_findings = []
    unique_insights = []
    by_category = defaultdict(list)
    by_severity = defaultdict(list)

    for finding_hash, info in findings_map.items():
        sources = list(info['sources'])
        finding = info['data'].copy()
        finding['sources'] = sources
        finding['is_unique'] = len(sources) == 1

        # Normalize severity
        if 'severity' in finding:
            finding['severity'] = normalize_severity(finding['severity'])

        all_findings.append(finding)

        # Track unique insights
        if len(sources) == 1:
            unique_insights.append({
                'finding': finding,
                'source': sources[0]
            })

        # Group by category
        category = finding.get('category', 'uncategorized')
        by_category[category].append(finding)

        # Group by severity
        severity = finding.get('severity', 'unknown')
        by_severity[severity].append(finding)

    return {
        'all_findings': all_findings,
        'by_category': dict(by_category),
        'by_severity': dict(by_severity),
        'unique_insights': unique_insights,
        'source_counts': dict(source_counts),
        'total_count': len(all_findings)
    }


def merge_recommendations(parsed_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge recommendations from multiple LLM responses.

    Returns dict with:
    - all_recommendations: deduplicated list with source attribution
    - by_priority: recommendations grouped by priority
    - unique_recommendations: recommendations only from one LLM
    """
    rec_map = defaultdict(lambda: {'sources': set(), 'data': None})

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})
        recommendations = data.get('recommendations', [])

        for rec in recommendations:
            # Use description for dedup (first 60 chars)
            desc = rec.get('description', '').lower().strip()[:60]
            rec_hash = desc

            rec_map[rec_hash]['sources'].add(source)
            rec_map[rec_hash]['data'] = rec

    all_recs = []
    unique_recs = []
    by_priority = defaultdict(list)

    for rec_hash, info in rec_map.items():
        sources = list(info['sources'])
        rec = info['data'].copy()
        rec['sources'] = sources
        rec['is_unique'] = len(sources) == 1
        rec['agreement_count'] = len(sources)

        all_recs.append(rec)

        if len(sources) == 1:
            unique_recs.append({
                'recommendation': rec,
                'source': sources[0]
            })

        priority = rec.get('priority', 'medium')
        by_priority[priority].append(rec)

    # Sort by agreement count (more sources = higher confidence)
    all_recs.sort(key=lambda x: (-x['agreement_count'], x.get('priority', 'medium')))

    return {
        'all_recommendations': all_recs,
        'by_priority': dict(by_priority),
        'unique_recommendations': unique_recs,
        'total_count': len(all_recs)
    }


def merge_risks(parsed_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge risks from multiple LLM responses.

    Returns dict with:
    - all_risks: deduplicated list with source attribution
    - by_severity: risks grouped by severity
    """
    risk_map = defaultdict(lambda: {'sources': set(), 'data': None})

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})
        risks = data.get('risks', [])

        for risk in risks:
            desc = risk.get('description', '').lower().strip()[:60]
            risk_hash = desc

            risk_map[risk_hash]['sources'].add(source)
            risk_map[risk_hash]['data'] = risk

    all_risks = []
    by_severity = defaultdict(list)

    for risk_hash, info in risk_map.items():
        sources = list(info['sources'])
        risk = info['data'].copy()
        risk['sources'] = sources
        risk['agreement_count'] = len(sources)

        # Normalize severity
        if 'severity' in risk:
            risk['severity'] = normalize_severity(risk['severity'])

        all_risks.append(risk)

        severity = risk.get('severity', 'unknown')
        by_severity[severity].append(risk)

    # Sort by agreement and severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    all_risks.sort(key=lambda x: (
        severity_order.get(x.get('severity', 'medium'), 2),
        -x['agreement_count']
    ))

    return {
        'all_risks': all_risks,
        'by_severity': dict(by_severity),
        'total_count': len(all_risks)
    }


def aggregate_metrics(parsed_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate metrics from multiple LLM responses.

    Returns:
    - average_confidence: mean confidence across all LLMs
    - coverage_consensus: most common coverage level
    - combined_summary_stats: summed stats
    - per_source_metrics: individual LLM metrics
    """
    confidences = []
    coverages = []
    combined_stats = {
        'critical_count': 0,
        'high_count': 0,
        'medium_count': 0,
        'low_count': 0
    }
    per_source = {}
    all_priorities = []

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})
        metrics = data.get('metrics', {})

        if metrics:
            # Collect confidence
            confidence = metrics.get('confidence')
            if confidence is not None:
                try:
                    confidences.append(float(confidence))
                except (ValueError, TypeError):
                    pass

            # Collect coverage
            coverage = metrics.get('coverage')
            if coverage:
                coverages.append(coverage)

            # Aggregate stats
            stats = metrics.get('summary_stats', {})
            for key in combined_stats:
                try:
                    combined_stats[key] += int(stats.get(key, 0))
                except (ValueError, TypeError):
                    pass

            # Collect priorities
            priorities = metrics.get('top_priorities', [])
            all_priorities.extend(priorities)

            per_source[source] = metrics

    # Calculate averages and consensus
    avg_confidence = sum(confidences) / len(confidences) if confidences else None

    # Find most common coverage
    coverage_consensus = None
    if coverages:
        from collections import Counter
        coverage_counts = Counter(coverages)
        coverage_consensus = coverage_counts.most_common(1)[0][0]

    return {
        'average_confidence': round(avg_confidence, 1) if avg_confidence else None,
        'coverage_consensus': coverage_consensus,
        'combined_summary_stats': combined_stats,
        'per_source_metrics': per_source,
        'all_top_priorities': all_priorities
    }


def merge_ranked_actions(parsed_responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge and re-rank actions from multiple LLM responses.

    Actions mentioned by multiple LLMs get higher rank.
    """
    action_map = defaultdict(lambda: {'sources': set(), 'data': None, 'ranks': []})

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})
        actions = data.get('ranked_actions', [])

        for action in actions:
            # Use action description for dedup
            action_text = action.get('action', '').lower().strip()[:60]

            action_map[action_text]['sources'].add(source)
            action_map[action_text]['data'] = action
            action_map[action_text]['ranks'].append(action.get('rank', 99))

    # Build consolidated list
    consolidated = []
    for action_text, info in action_map.items():
        action = info['data'].copy()
        action['sources'] = list(info['sources'])
        action['agreement_count'] = len(info['sources'])
        action['avg_rank'] = sum(info['ranks']) / len(info['ranks'])
        consolidated.append(action)

    # Sort by agreement count (desc) then average rank (asc)
    consolidated.sort(key=lambda x: (-x['agreement_count'], x['avg_rank']))

    # Assign new consolidated ranks
    for i, action in enumerate(consolidated, 1):
        action['consolidated_rank'] = i

    return consolidated


def detect_conflicts(parsed_responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect conflicting recommendations between LLMs.

    Returns list of conflicts that need human decision.
    """
    conflicts = []

    # Look for contradictory recommendations
    # This is a simplified heuristic - real conflicts are hard to detect

    rec_by_topic = defaultdict(list)

    for response in parsed_responses:
        source = response.get('source', 'unknown')
        data = response.get('data', {})

        for rec in data.get('recommendations', []):
            # Extract topic (first few words)
            desc = rec.get('description', '')
            words = desc.split()[:3]
            topic = ' '.join(words).lower()

            rec_by_topic[topic].append({
                'source': source,
                'full_rec': rec
            })

    # Check for topics with different priorities
    for topic, recs in rec_by_topic.items():
        if len(recs) >= 2:
            priorities = set(r['full_rec'].get('priority', 'medium') for r in recs)
            if len(priorities) > 1:
                conflicts.append({
                    'topic': topic,
                    'type': 'priority_disagreement',
                    'sources': [r['source'] for r in recs],
                    'recommendations': [r['full_rec'] for r in recs]
                })

    return conflicts


def consolidate_responses(parsed_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main consolidation function - merges all aspects of LLM responses.

    Args:
        parsed_responses: List from parse_llm_responses, each with 'source' and 'data'

    Returns:
        Consolidated output with all insights merged
    """
    sources = [r.get('source', 'unknown') for r in parsed_responses]

    # Merge all components
    findings_result = merge_findings(parsed_responses)
    recommendations_result = merge_recommendations(parsed_responses)
    risks_result = merge_risks(parsed_responses)
    metrics_result = aggregate_metrics(parsed_responses)
    ranked_actions = merge_ranked_actions(parsed_responses)
    conflicts = detect_conflicts(parsed_responses)

    return {
        'metadata': {
            'sources': sources,
            'source_count': len(sources),
            'consolidated_at': datetime.now().isoformat(),
            'version': '1.0.0'
        },
        'findings': findings_result,
        'recommendations': recommendations_result,
        'risks': risks_result,
        'metrics': metrics_result,
        'ranked_actions': ranked_actions,
        'conflicts': conflicts,
        'summary': {
            'total_findings': findings_result['total_count'],
            'unique_insights': len(findings_result['unique_insights']),
            'total_recommendations': recommendations_result['total_count'],
            'total_risks': risks_result['total_count'],
            'conflicts_found': len(conflicts),
            'avg_confidence': metrics_result['average_confidence']
        }
    }
