"""
Tests for User-Facing Document Validators

Tests UserFacingDocValidator, UserGuideValidator, and QuickrefValidator
"""

import pytest
from pathlib import Path
from papertrail.validators.user_facing import UserFacingDocValidator, UserGuideValidator, QuickrefValidator
from papertrail.validator import ValidationSeverity


class TestUserFacingDocValidator:
    """Test base user-facing document validator"""

    @pytest.fixture
    def validator(self):
        """Create UserFacingDocValidator instance"""
        return UserFacingDocValidator()

    def test_validate_valid_guide(self, validator, tmp_path):
        """Test validation of valid user guide"""
        guide = """---
agent: Test Agent
date: "2026-01-13"
task: CREATE
audience: developers
doc_type: guide
title: Getting Started Guide
difficulty: beginner
estimated_time: 15 minutes
---

# Getting Started Guide

## Overview

This guide helps you get started.

## Prerequisites

- Python 3.10+
- pip

## Steps

1. Install
2. Configure
3. Run

## Examples

Example usage here.

## Troubleshooting

Common issues and solutions.
"""
        guide_file = tmp_path / "GETTING-STARTED-GUIDE.md"
        guide_file.write_text(guide)

        result = validator.validate_file(guide_file)

        # Should pass validation
        assert result.valid == True
        assert result.score >= 90

    def test_estimated_time_format_validation(self, validator, tmp_path):
        """Test that estimated_time format is validated"""
        doc = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: tutorial
estimated_time: invalid format
---

# Tutorial
"""
        doc_file = tmp_path / "test.md"
        doc_file.write_text(doc)

        result = validator.validate_file(doc_file)

        # Should have warning about estimated_time format
        warnings = [w for w in result.warnings if 'estimated_time' in w.lower()]
        assert len(warnings) > 0

    def test_quickstart_difficulty_warning(self, validator, tmp_path):
        """Test that advanced quickstart gets warning"""
        doc = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: quickstart
difficulty: advanced
---

# Quickstart
"""
        doc_file = tmp_path / "test.md"
        doc_file.write_text(doc)

        result = validator.validate_file(doc_file)

        # Should have warning about quickstart difficulty
        warnings = [w for w in result.warnings if 'quickstart' in w.lower() and 'difficulty' in w.lower()]
        assert len(warnings) > 0


class TestUserGuideValidator:
    """Test user guide validator"""

    @pytest.fixture
    def validator(self):
        """Create UserGuideValidator instance"""
        return UserGuideValidator()

    def test_guide_with_examples_passes(self, validator, tmp_path):
        """Test that guide with Examples section passes"""
        guide = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: guide
---

# User Guide

## Overview
Overview content.

## Prerequisites
Prerequisites list.

## Steps
Step-by-step instructions.

## Examples
Example usage.

## Troubleshooting
Common issues.
"""
        guide_file = tmp_path / "USER-GUIDE.md"
        guide_file.write_text(guide)

        result = validator.validate_file(guide_file)

        # Should not have warning about missing Examples
        example_warnings = [w for w in result.warnings if 'examples' in w.lower()]
        assert len(example_warnings) == 0

    def test_guide_without_examples_warning(self, validator, tmp_path):
        """Test that guide without Examples gets warning"""
        guide = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: guide
---

# User Guide

## Overview
Overview content.

## Steps
Step-by-step instructions.
"""
        guide_file = tmp_path / "USER-GUIDE.md"
        guide_file.write_text(guide)

        result = validator.validate_file(guide_file)

        # Should have warning about missing Examples
        example_warnings = [w for w in result.warnings if 'examples' in w.lower()]
        assert len(example_warnings) > 0

    def test_wrong_doc_type_error(self, validator, tmp_path):
        """Test that wrong doc_type gets MAJOR error"""
        doc = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: tutorial
---

# Guide
"""
        doc_file = tmp_path / "test.md"
        doc_file.write_text(doc)

        result = validator.validate_file(doc_file)

        # Should have MAJOR error for wrong doc_type
        doc_type_errors = [
            e for e in result.errors
            if e.severity == ValidationSeverity.MAJOR and 'doc_type' in e.message.lower()
        ]
        assert len(doc_type_errors) > 0
        assert "'guide'" in doc_type_errors[0].message


class TestQuickrefValidator:
    """Test quickref/quickstart validator"""

    @pytest.fixture
    def validator(self):
        """Create QuickrefValidator instance"""
        return QuickrefValidator()

    def test_quickstart_valid(self, validator, tmp_path):
        """Test valid quickstart document"""
        quickstart = """---
agent: Test Agent
date: "2026-01-13"
task: CREATE
audience: developers
doc_type: quickstart
---

# Quick Start

## Installation

pip install package

## Basic Usage

Basic example here.

## Next Steps

Where to go from here.
"""
        qs_file = tmp_path / "QUICKSTART.md"
        qs_file.write_text(quickstart)

        result = validator.validate_file(qs_file)

        # Should pass
        assert result.valid == True

    def test_reference_valid(self, validator, tmp_path):
        """Test valid reference document"""
        reference = """---
agent: Test Agent
date: "2026-01-13"
task: CREATE
audience: developers
doc_type: reference
---

# API Reference

## Reference

Function reference.

## Parameters

Parameter descriptions.

## Examples

Usage examples.

## See Also

Related docs.
"""
        ref_file = tmp_path / "API-QUICKREF.md"
        ref_file.write_text(reference)

        result = validator.validate_file(ref_file)

        # Should pass
        assert result.valid == True

    def test_wrong_doc_type_error(self, validator, tmp_path):
        """Test that wrong doc_type gets MAJOR error"""
        doc = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: guide
---

# Quickref
"""
        doc_file = tmp_path / "test.md"
        doc_file.write_text(doc)

        result = validator.validate_file(doc_file)

        # Should have MAJOR error for wrong doc_type
        doc_type_errors = [
            e for e in result.errors
            if e.severity == ValidationSeverity.MAJOR and 'doc_type' in e.message.lower()
        ]
        assert len(doc_type_errors) > 0

    def test_quickstart_length_warning(self, validator, tmp_path):
        """Test that long quickstart gets warning"""
        # Create a quickstart with > 500 lines
        long_content = "Line\n" * 600
        quickstart = f"""---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: quickstart
---

# Quick Start

{long_content}
"""
        qs_file = tmp_path / "QUICKSTART.md"
        qs_file.write_text(quickstart)

        result = validator.validate_file(qs_file)

        # Should have warning about length
        length_warnings = [w for w in result.warnings if 'concise' in w.lower() or 'lines' in w.lower()]
        assert len(length_warnings) > 0

    def test_required_sections_validated(self, validator, tmp_path):
        """Test that required sections are validated"""
        quickstart = """---
agent: Test Agent
date: 2026-01-13
task: CREATE
audience: developers
doc_type: quickstart
---

# Incomplete Quickstart

Only has title, missing required sections.
"""
        qs_file = tmp_path / "QUICKSTART.md"
        qs_file.write_text(quickstart)

        result = validator.validate_file(qs_file)

        # Should have errors for missing required sections
        section_errors = [
            e for e in result.errors
            if 'section' in e.message.lower()
        ]
        # Quickstart requires: Quick Start, Installation, Basic Usage, Next Steps
        # We're missing most of them
        assert len(section_errors) > 0
