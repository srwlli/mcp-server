"""
Papertrail - Universal Documentation Standards for CodeRef Ecosystem

Provides UDS headers/footers, schema validation, health scoring,
and template engine with CodeRef-native extensions.
"""

import os
from setuptools import setup, find_packages

setup(
    name="papertrail",
    version="1.0.0",
    description="Universal Documentation Standards (UDS) for CodeRef Ecosystem",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="CodeRef Ecosystem",
    author_email="noreply@anthropic.com",
    url="https://github.com/coderef/papertrail",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "papertrail": ["schemas/*.json"],
    },
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "jsonschema>=4.0",
        "jinja2>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
