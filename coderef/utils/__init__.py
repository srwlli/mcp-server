"""
coderef.utils - Wrapper utilities for .coderef/ integration

Provides simple Python functions for calling parse_coderef_data.py scripts.
"""

from .coderef_wrapper import (
    preprocess_index,
    generate_foundation_docs,
    read_coderef_output,
    check_coderef_available
)

__all__ = [
    'preprocess_index',
    'generate_foundation_docs',
    'read_coderef_output',
    'check_coderef_available'
]
