"""Client modules for inter-service communication."""

from .docs_client import DocsClient, get_docs_client, DocsServiceConfig

__all__ = [
    "DocsClient",
    "get_docs_client",
    "DocsServiceConfig",
]
