# Schema Documentation

## Database Tables

### FoundationGenerator

*File: `generators\foundation_generator.py`*


### HandoffGenerator

*File: `generators\handoff_generator.py`*


### QuickrefGenerator

*File: `generators\quickref_generator.py`*


### User

*File: `tests\integration\test_coderef_foundation_docs.py`*

| Column | Definition |
|--------|------------|
| id | Integer, primary_key=True |
| name | String(100 |
| email | String(255 |

### User

*File: `tests\unit\generators\test_coderef_foundation_generator.py`*

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

*File: `tests\unit\generators\test_coderef_foundation_generator.py`*

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

*File: `tests\unit\generators\test_coderef_foundation_generator.py`*

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

*File: `tests\unit\generators\test_coderef_foundation_generator.py`*

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


*Generated: 2025-12-15T15:05:23.285498*