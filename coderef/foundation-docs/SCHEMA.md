# Schema Documentation

## Database Tables

### PersonaBehavior

*File: `personas-mcp\src\models.py`*


### PersonaDefinition

*File: `personas-mcp\src\models.py`*


### PersonaState

*File: `personas-mcp\src\models.py`*


### TaskExecutionStatus

*File: `personas-mcp\src\models.py`*


### TaskProgress

*File: `personas-mcp\src\models.py`*


### TodoMetadata

*File: `personas-mcp\src\models.py`*


### CustomPersonaInput

*File: `personas-mcp\src\models.py`*


### FoundationGenerator

*File: `docs-mcp\generators\foundation_generator.py`*


### HandoffGenerator

*File: `docs-mcp\generators\handoff_generator.py`*


### QuickrefGenerator

*File: `docs-mcp\generators\quickref_generator.py`*


### User

*File: `docs-mcp\tests\integration\test_coderef_foundation_docs.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| name | String(100 |
| email | String(255 |

### User

*File: `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| email | String(255 |
| name | String(100 |
| created_at | DateTime |
| is_active | Boolean, default=True |
| id | Integer, primary_key=True |
| title | String(200 |
| content | String |
| author_id | Integer, ForeignKey("users.id" |
| id | Integer, primary_key=True |
| text | String(500 |
| post_id | Integer, ForeignKey("posts.id" |

### User

*File: `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| email | String(255 |
| name | String(100 |
| created_at | DateTime |
| is_active | Boolean, default=True |
| id | Integer, primary_key=True |
| title | String(200 |
| content | String |
| author_id | Integer, ForeignKey("users.id" |
| id | Integer, primary_key=True |
| text | String(500 |
| post_id | Integer, ForeignKey("posts.id" |

### Post

*File: `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| email | String(255 |
| name | String(100 |
| created_at | DateTime |
| is_active | Boolean, default=True |
| id | Integer, primary_key=True |
| title | String(200 |
| content | String |
| author_id | Integer, ForeignKey("users.id" |
| id | Integer, primary_key=True |
| text | String(500 |
| post_id | Integer, ForeignKey("posts.id" |

### Comment

*File: `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| email | String(255 |
| name | String(100 |
| created_at | DateTime |
| is_active | Boolean, default=True |
| id | Integer, primary_key=True |
| title | String(200 |
| content | String |
| author_id | Integer, ForeignKey("users.id" |
| id | Integer, primary_key=True |
| text | String(500 |
| post_id | Integer, ForeignKey("posts.id" |

### MetadataValue

*File: `coderef-mcp\coderef\models.py`*


### ElementMetadata

*File: `coderef-mcp\coderef\models.py`*


### Relationship

*File: `coderef-mcp\coderef\models.py`*


### CodeRef2Element

*File: `coderef-mcp\coderef\models.py`*


### QueryFilter

*File: `coderef-mcp\coderef\models.py`*



*Generated: 2025-12-18T00:34:05.556973*