"""
LLM Output Parser - Parse and extract JSON from multiple LLM responses.

Part of the llm-workflow feature (WO-LLM-WORKFLOW-001).
"""

import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


# Patterns to detect LLM response boundaries
LLM_PATTERNS = [
    (r'^={3,}\s*(ChatGPT|GPT-4|GPT-4o|OpenAI)\s*={0,}', 'chatgpt'),
    (r'^={3,}\s*(Claude|Anthropic)\s*={0,}', 'claude'),
    (r'^={3,}\s*(Gemini|Google|Bard)\s*={0,}', 'gemini'),
    (r'^(ChatGPT|GPT-4|GPT-4o)\s*(said|response|:)', 'chatgpt'),
    (r'^(Claude)\s*(said|response|:)', 'claude'),
    (r'^(Gemini|Google)\s*(said|response|:)', 'gemini'),
    (r'^From\s+(ChatGPT|GPT-4|Claude|Gemini)', None),  # Dynamic detection
    (r'^###?\s*(ChatGPT|GPT-4|Claude|Gemini)', None),  # Markdown headers
    (r'^\*\*\s*(ChatGPT|GPT-4|Claude|Gemini)\s*\*\*', None),  # Bold markers
]


def detect_llm_source(text: str) -> Optional[str]:
    """Detect which LLM produced this response based on markers."""
    for pattern, source in LLM_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            if source:
                return source
            # Dynamic detection from capture group
            detected = match.group(1).lower()
            if 'gpt' in detected or 'chatgpt' in detected or 'openai' in detected:
                return 'chatgpt'
            elif 'claude' in detected or 'anthropic' in detected:
                return 'claude'
            elif 'gemini' in detected or 'google' in detected or 'bard' in detected:
                return 'gemini'
    return None


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text, handling various formats."""
    # Try to find JSON block in markdown code fence
    json_block_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    # Try to parse the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    return None


def split_responses(content: str) -> List[Dict[str, Any]]:
    """Split a file containing multiple LLM responses into individual responses."""
    responses = []

    # Try to split by common delimiters
    delimiters = [
        r'\n={3,}.*?={0,}\n',  # === ChatGPT ===
        r'\n-{3,}\n',          # ---
        r'\n\*{3,}\n',         # ***
    ]

    # First, try to detect LLM markers and split
    current_source = None
    current_content = []
    lines = content.split('\n')

    for line in lines:
        detected = detect_llm_source(line)
        if detected:
            # Save previous response if exists
            if current_content and current_source:
                responses.append({
                    'source': current_source,
                    'raw_content': '\n'.join(current_content).strip()
                })
            current_source = detected
            current_content = []
        else:
            current_content.append(line)

    # Don't forget the last response
    if current_content:
        if current_source:
            responses.append({
                'source': current_source,
                'raw_content': '\n'.join(current_content).strip()
            })
        elif not responses:
            # No markers found, treat entire content as single response
            responses.append({
                'source': 'unknown',
                'raw_content': content.strip()
            })

    return responses


def parse_llm_responses(file_path: Path) -> Dict[str, Any]:
    """
    Parse a file containing multiple LLM responses.

    Args:
        file_path: Path to file containing LLM responses

    Returns:
        Dict with parsed responses and metadata
    """
    content = file_path.read_text(encoding='utf-8')

    # Split into individual responses
    raw_responses = split_responses(content)

    parsed_responses = []
    parse_errors = []

    for i, response in enumerate(raw_responses):
        source = response['source']
        raw_content = response['raw_content']

        # Try to extract JSON
        json_data = extract_json_from_text(raw_content)

        if json_data:
            parsed_responses.append({
                'source': source,
                'data': json_data,
                'raw_length': len(raw_content)
            })
        else:
            parse_errors.append({
                'source': source,
                'error': 'Failed to extract JSON',
                'preview': raw_content[:200] + '...' if len(raw_content) > 200 else raw_content
            })

    return {
        'file_path': str(file_path),
        'total_responses': len(raw_responses),
        'parsed_count': len(parsed_responses),
        'error_count': len(parse_errors),
        'responses': parsed_responses,
        'errors': parse_errors
    }


def validate_response_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a parsed response matches expected schema.

    Returns dict with is_valid and any missing fields.
    """
    required_fields = ['findings', 'recommendations', 'risks', 'metrics', 'ranked_actions']

    missing = [f for f in required_fields if f not in data]

    return {
        'is_valid': len(missing) == 0,
        'missing_fields': missing,
        'has_findings': 'findings' in data and len(data.get('findings', [])) > 0,
        'has_recommendations': 'recommendations' in data and len(data.get('recommendations', [])) > 0,
        'has_metrics': 'metrics' in data
    }
