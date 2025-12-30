"""
Unit tests for UDS health scoring
"""

import pytest
from datetime import datetime, timedelta
from papertrail.health import calculate_health, store_health_score, load_health_score, HealthScorer
import tempfile
from pathlib import Path


class TestHealthScoring:
    """Test health score calculation"""

    def test_perfect_health_score(self):
        """Test health scoring for perfect document (<7 days old, all sections)"""
        document = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{datetime.utcnow().isoformat()}Z'
version: 1.0.0
---

# Purpose
Purpose section

# Overview
Overview section

# What/Why/When
Details

# Examples

```python
code_example()
```

# References
References
"""

        health = calculate_health(document, "architecture")

        # Perfect score breakdown:
        # Traceability: 40 (has workorder_id, feature_id, MCP attribution)
        # Completeness: 30 (all required sections + examples)
        # Freshness: 20 (<7 days)
        # Validation: 10 (passes validation)
        assert health.score == 100
        assert health.traceability == 40
        assert health.completeness == 30
        assert health.freshness == 20
        assert health.validation == 10

    def test_traceability_scoring(self):
        """Test traceability component scoring"""
        # Full traceability
        doc_full = """---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{}'
---

# Purpose
Test
""".format(datetime.utcnow().isoformat() + "Z")

        health = calculate_health(doc_full, "architecture")
        assert health.traceability == 40
        assert health.has_workorder_id
        assert health.has_feature_id
        assert health.has_mcp_attribution

        # Missing workorder_id
        doc_no_wo = """---
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{}'
---

# Purpose
Test
""".format(datetime.utcnow().isoformat() + "Z")

        health = calculate_health(doc_no_wo, "architecture")
        assert health.traceability == 20  # Missing 20 points for workorder_id
        assert not health.has_workorder_id

    def test_freshness_scoring(self):
        """Test freshness component scoring"""
        # Recent document (<7 days)
        recent_date = datetime.utcnow()
        doc_recent = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{recent_date.isoformat()}Z'
---

# Purpose
Test
"""

        health = calculate_health(doc_recent, "architecture")
        assert health.freshness == 20

        # 15 days old (7-30 days)
        old_date = datetime.utcnow() - timedelta(days=15)
        doc_old = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{old_date.isoformat()}Z'
---

# Purpose
Test
"""

        health = calculate_health(doc_old, "architecture")
        assert health.freshness == 10

        # 60 days old (30-90 days)
        older_date = datetime.utcnow() - timedelta(days=60)
        doc_older = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{older_date.isoformat()}Z'
---

# Purpose
Test
"""

        health = calculate_health(doc_older, "architecture")
        assert health.freshness == 5

        # 100 days old (>90 days)
        ancient_date = datetime.utcnow() - timedelta(days=100)
        doc_ancient = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{ancient_date.isoformat()}Z'
---

# Purpose
Test
"""

        health = calculate_health(doc_ancient, "architecture")
        assert health.freshness == 0

    def test_completeness_scoring(self):
        """Test completeness component scoring"""
        # Document with all required sections + examples
        doc_complete = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{datetime.utcnow().isoformat()}Z'
version: 1.0.0
---

# Purpose
Purpose

# Overview
Overview

# What/Why/When
Details

# Examples
Example content

# References
References
"""

        health = calculate_health(doc_complete, "architecture")
        assert health.completeness == 30  # 20 for sections + 10 for examples

        # Document without examples (has Examples section but no code blocks)
        doc_no_examples = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{datetime.utcnow().isoformat()}Z'
version: 1.0.0
---

# Purpose
Purpose

# Overview
Overview

# What/Why/When
Details

# Examples
No code examples provided.

# References
References
"""

        health = calculate_health(doc_no_examples, "architecture")
        assert health.completeness == 30  # 20 for sections + 10 for Examples section (even without code blocks)

    def test_validation_scoring(self):
        """Test validation component scoring"""
        # Valid document
        doc_valid = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{datetime.utcnow().isoformat()}Z'
version: 1.0.0
---

# Purpose
Purpose

# Overview
Overview

# What/Why/When
Details

# Examples
Examples

# References
References
"""

        health = calculate_health(doc_valid, "architecture")
        assert health.validation == 10
        assert health.passes_validation

        # Invalid document (missing sections)
        doc_invalid = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test
timestamp: '{datetime.utcnow().isoformat()}Z'
---

# Purpose
Only purpose
"""

        health = calculate_health(doc_invalid, "architecture")
        assert health.validation == 0  # Doesn't pass validation
        assert not health.passes_validation


class TestHealthScoreStorage:
    """Test health score storage and loading"""

    def test_store_and_load_health_score(self):
        """Test storing and loading health score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_dir = Path(tmpdir)

            # Create health score
            doc = f"""---
workorder_id: WO-TEST-FEATURE-001
generated_by: coderef-docs v1.0.0
feature_id: test-feature
timestamp: '{datetime.utcnow().isoformat()}Z'
---

# Purpose
Test
"""

            health = calculate_health(doc, "architecture")

            # Store health score
            store_health_score("test-feature", "architecture", health, context_dir)

            # Verify file was created
            health_file = context_dir / "test-feature-architecture-health.json"
            assert health_file.exists()

            # Load health score
            loaded_health = load_health_score("test-feature", "architecture", context_dir)

            # Verify loaded score matches original
            assert loaded_health is not None
            assert loaded_health.score == health.score
            assert loaded_health.traceability == health.traceability
            assert loaded_health.completeness == health.completeness
            assert loaded_health.freshness == health.freshness
            assert loaded_health.validation == health.validation

    def test_load_nonexistent_health_score(self):
        """Test loading health score that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            context_dir = Path(tmpdir)

            loaded = load_health_score("nonexistent", "architecture", context_dir)
            assert loaded is None
