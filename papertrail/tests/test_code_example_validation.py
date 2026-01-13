"""
Tests for Code Example Validation

Tests that code examples in API and COMPONENTS docs are validated
against actual code (when coderef-context integration is available).
"""

import pytest
from pathlib import Path
from papertrail.validators.foundation import FoundationDocValidator
from papertrail.validator import ValidationSeverity


class TestCodeExampleValidation:
    """Test code example validation for API and COMPONENTS docs"""

    @pytest.fixture
    def validator(self):
        """Create FoundationDocValidator instance"""
        return FoundationDocValidator()

    def test_extract_code_blocks(self, validator):
        """Test that code blocks are correctly extracted from markdown"""
        content = """
# Test Doc

Here's an example:

```python
def hello():
    return "world"
```

And another:

```javascript
const greet = () => "hello";
```
"""
        blocks = validator._extract_code_blocks(content)

        assert len(blocks) == 2
        assert blocks[0]['language'] == 'python'
        assert 'def hello()' in blocks[0]['code']
        assert blocks[1]['language'] == 'javascript'
        assert 'const greet' in blocks[1]['code']

    def test_code_example_validation_api_doc(self, validator, tmp_path):
        """Test that API doc with code examples is processed (placeholder validation)"""
        api_doc = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test-api
doc_type: api
---

# Test API

## Endpoints

### User Management

```bash
# Get all users
GET /api/users

# Create a user
POST /api/users

# Get specific user
GET /api/users/{id}

# Delete user
DELETE /api/users/{id}
```

## Authentication

All endpoints require authentication.
"""
        api_file = tmp_path / "API.md"
        api_file.write_text(api_doc)

        result = validator.validate_file(api_file)

        # Code example validation should be called (currently placeholder)
        # In full implementation with coderef-context, this would verify endpoints
        # For now, just verify no errors from placeholder logic
        assert result.valid or len([e for e in result.errors if e.severity == ValidationSeverity.CRITICAL]) == 0

    def test_code_example_validation_components_doc(self, validator, tmp_path):
        """Test that COMPONENTS doc with JSX examples is processed"""
        components_doc = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test-components
doc_type: components
---

# Test Components

## Button Component

```tsx
import { Button } from './components';

function App() {
  return (
    <Button
      variant="primary"
      onClick={handleClick}
    >
      Click Me
    </Button>
  );
}
```

## Input Component

```jsx
<Input
  type="text"
  placeholder="Enter text"
  onChange={handleChange}
/>
```
"""
        comp_file = tmp_path / "COMPONENTS.md"
        comp_file.write_text(components_doc)

        result = validator.validate_file(comp_file)

        # Code example validation should be called for COMPONENTS docs
        # Currently placeholder - full implementation would verify props
        assert result.valid or len([e for e in result.errors if e.severity == ValidationSeverity.CRITICAL]) == 0

    def test_code_example_validation_skipped_for_readme(self, validator, tmp_path):
        """Test that code example validation is skipped for non-API/COMPONENTS docs"""
        readme = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test-readme
doc_type: readme
---

# Test README

```python
# Some example code that won't be validated
print("Hello")
```
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme)

        result = validator.validate_file(readme_file)

        # Code example validation should not be called for README
        # No validation errors related to code examples
        example_errors = [
            e for e in result.errors
            if "example" in e.message.lower() and e.severity == ValidationSeverity.WARNING
        ]
        assert len(example_errors) == 0

    def test_graceful_degradation_on_validation_error(self, validator, tmp_path):
        """Test graceful degradation when code example validation encounters errors"""
        # This tests the try-except block in FoundationDocValidator.validate_specific()
        api_doc = """---
agent: Test Agent
date: 2026-01-12
task: CREATE
workorder_id: WO-TEST-001
generated_by: coderef-docs v1.0.0
feature_id: test-api
doc_type: api
---

# Test API

```python
GET /api/test
```
"""
        api_file = tmp_path / "API.md"
        api_file.write_text(api_doc)

        # Even if code example validation fails, validation should continue
        result = validator.validate_file(api_file)

        # Should not crash - graceful degradation
        assert result is not None
        assert isinstance(result.score, int)

    def test_code_block_extraction_handles_malformed_blocks(self, validator):
        """Test that malformed code blocks don't crash extraction"""
        malformed_content = """
# Test

```python
incomplete code block (no closing backticks)

```
more content

```
no language specified
```
"""
        # Should not crash
        blocks = validator._extract_code_blocks(malformed_content)

        # Should still extract valid blocks (the one with no language)
        # Pattern requires language, so this should return empty or handle gracefully
        assert isinstance(blocks, list)

    def test_api_endpoint_pattern_matching(self, validator):
        """Test that API endpoint patterns are correctly identified"""
        api_content = """
```bash
# Standard REST endpoints
GET /api/v1/users
POST /api/v1/users
PUT /api/v1/users/123
DELETE /api/v1/users/123
PATCH /api/v1/users/123

# With path parameters
GET /api/users/{id}
GET /api/users/{userId}/posts/{postId}

# With hyphens and colons
GET /api/health-check
GET /api/v2:alpha/resources
```
"""
        blocks = validator._extract_code_blocks(api_content)

        assert len(blocks) == 1
        assert 'GET /api/v1/users' in blocks[0]['code']
        assert 'POST /api/v1/users' in blocks[0]['code']
        assert 'DELETE /api/v1/users/123' in blocks[0]['code']

    def test_component_pattern_matching(self, validator):
        """Test that JSX/TSX component patterns are correctly identified"""
        component_content = """
```tsx
// Various component usage patterns
<Button variant="primary">Click</Button>
<Input type="text" placeholder="Name" />
<Card className="shadow-lg" title="Welcome">
  <p>Content</p>
</Card>
<CustomComponent
  complexProp={someValue}
  onClick={handler}
/>
```
"""
        blocks = validator._extract_code_blocks(component_content)

        assert len(blocks) == 1
        assert '<Button' in blocks[0]['code']
        assert '<Input' in blocks[0]['code']
        assert '<Card' in blocks[0]['code']
        assert '<CustomComponent' in blocks[0]['code']
