# 📋 Universal Inventory Manifest Creation Process

## **Process Overview**

This is a universal, project-agnostic methodology for creating comprehensive project inventory manifests. The process can be applied to any software project regardless of language, framework, or architecture.

---

## **Phase 1: Project Discovery & Structure Analysis**

### **Step 1: Project Structure Discovery**
```bash
# Universal directory exploration
list_dir(target_directory="project-root")
list_dir(target_directory="project-root/src")           # Source code
list_dir(target_directory="project-root/tests")         # Test files
list_dir(target_directory="project-root/docs")          # Documentation
list_dir(target_directory="project-root/config")        # Configuration
list_dir(target_directory="project-root/scripts")       # Build/utility scripts
list_dir(target_directory="project-root/assets")        # Static assets
```

### **Step 2: File Metadata Collection**
```bash
# Universal file metadata gathering
Get-ChildItem -Recurse -File | Where-Object {
    $_.Extension -match '\.(py|js|ts|java|go|rs|cpp|c|h|md|json|xml|yml|yaml|toml|ini|cfg|sh|bat|ps1|sql|html|css|scss|vue|jsx|tsx)$'
} | Select-Object FullName, Length, LastWriteTime
```

### **Step 3: Core File Analysis**
- Read project configuration files (package.json, pyproject.toml, Cargo.toml, pom.xml, etc.)
- Identify main entry points and build scripts
- Analyze project structure and dependencies
- Determine project type and technology stack

### **Step 4: Initial Manifest Creation**
- Create `inventory_manifest.json` in project's inventory directory
- Organize files into universal categories
- Include size, line counts, roles, and descriptions

---

## **Phase 2: Universal Metadata Enhancement**

### **Step 1: Universal Categorization**
Apply universal 6-category taxonomy to each file:
- **`core`**: Essential application components (main files, entry points)
- **`source`**: Source code files (business logic, utilities, modules)  
- **`template`**: Templates, schemas, and configuration templates
- **`config`**: Configuration and setup files
- **`test`**: Test suite and testing infrastructure
- **`docs`**: Documentation and guides

### **Step 2: Status Assessment**
Evaluate each file's current state:
- **`active`**: Currently maintained and used
- **`deprecated`**: Historical/archived files
- **`refactor-needed`**: Files requiring refactoring
- **`experimental`**: Work-in-progress or experimental features

### **Step 3: Universal Risk Level Calculation**
```python
def calculate_risk_level(file_size, complexity, sensitivity, file_type):
    # Size-based risk
    size_risk = "high" if file_size > 50000 else "medium" if file_size > 10000 else "low"
    
    # Complexity-based risk
    complexity_risk = "high" if complexity == "high" else "medium" if complexity == "medium" else "low"
    
    # Security sensitivity
    security_risk = "high" if sensitivity == "security" else "low"
    
    # File type risk
    type_risk = "high" if file_type in ["config", "security", "auth"] else "low"
    
    # Return highest risk level
    risks = [size_risk, complexity_risk, security_risk, type_risk]
    return "high" if "high" in risks else "medium" if "medium" in risks else "low"
```

### **Step 4: Universal Tag Generation**
Create descriptive tags based on file characteristics:
- **Functional tags**: `["entrypoint", "handler", "service", "utility"]`
- **Technical tags**: `["validation", "security", "database", "api"]`
- **Process tags**: `["build", "deploy", "test", "lint"]`
- **Framework tags**: `["react", "vue", "express", "django", "spring"]`

### **Step 5: Dependency Mapping**
- Analyze import/require statements
- Document internal and external dependencies
- Create dependency graphs for critical files
- Identify circular dependencies

### **Step 6: Contextual Notes**
- Add one-sentence descriptions for each file
- Include priority indicators and maintenance notes
- Document refactor candidates and security considerations
- Note framework-specific patterns

---

## **Phase 3: Universal Health Score Calculation**

### **Step 1: Data Analysis**
- Process inventory manifest data programmatically
- Calculate project health metrics
- Identify patterns and anomalies
- Assess code quality indicators

### **Step 2: Universal Health Score Calculation**
```python
def calculate_health_score(project_data):
    base_score = 10.0
    
    # File size distribution
    large_files = count_files_larger_than(50000)
    if large_files > 5:
        base_score -= 0.3
    
    # Test coverage
    test_ratio = test_files / total_files
    if test_ratio < 0.1:
        base_score -= 0.4
    elif test_ratio < 0.2:
        base_score -= 0.2
    
    # Documentation coverage
    doc_ratio = doc_files / total_files
    if doc_ratio < 0.2:
        base_score -= 0.3
    elif doc_ratio < 0.4:
        base_score -= 0.1
    
    # Deprecated files
    deprecated_ratio = deprecated_files / total_files
    if deprecated_ratio > 0.3:
        base_score -= 0.2
    
    # Security-sensitive files
    security_files = count_security_sensitive_files()
    if security_files == 0:
        base_score -= 0.2
    
    return min(10.0, max(0.0, base_score))
```

### **Step 3: Universal Risk Assessment**
- **High Risk**: Large files, security-sensitive, complex logic
- **Medium Risk**: Moderate complexity, configuration files
- **Low Risk**: Small files, documentation, simple utilities

---

## **Universal File Structure & Locations**

### **Standardized Folder Structure:**
```
project-root/
├── inventory/                    # Universal inventory location
│   └── inventory_manifest.json   # Enhanced manifest with metadata
├── src/                         # Source code
├── tests/                       # Test files
├── docs/                        # Documentation
├── config/                      # Configuration files
├── scripts/                     # Build/utility scripts
└── assets/                      # Static assets
```

### **Universal File Locations:**
- **`inventory/inventory_manifest.json`** - Enhanced manifest with metadata

---

## **Universal Technical Implementation**

### **Tools Used (Project Agnostic):**
1. **`list_dir`**: Directory structure exploration
2. **`read_file`**: File content analysis
3. **`run_terminal_cmd`**: System metadata collection
4. **`write`**: File creation and updates
5. **`todo_write`**: Task tracking and progress management

### **Universal Data Structures:**
```json
{
  "project": {
    "name": "project-name",
    "version": "1.0.0",
    "description": "Project description",
    "type": "Web App|API|Library|CLI|Desktop App",
    "language": "Python|JavaScript|TypeScript|Java|Go|Rust|C++|C#",
    "framework": "React|Vue|Angular|Express|Django|Spring|Actix|etc",
    "total_files": 0,
    "total_size_bytes": 0
  },
  "files": {
    "filename.ext": {
      "category": "core|source|template|config|test|docs",
      "status": "active|deprecated|refactor-needed|experimental",
      "risk_level": "low|medium|high",
      "tags": ["tag1", "tag2", "tag3"],
      "dependencies": ["dep1", "dep2"],
      "notes": "Contextual description",
      "size_bytes": 0,
      "lines_of_code": 0,
      "role": "Functional role description",
      "file_type": "source|config|test|doc|asset|script",
      "framework": "framework-name",
      "last_modified": "ISO-timestamp"
    }
  },
  "summary": {
    "total_files": 0,
    "categories": {
      "core": 0,
      "source": 0,
      "template": 0,
      "config": 0,
      "test": 0,
      "docs": 0
    },
    "status": {
      "active": 0,
      "deprecated": 0
    },
    "risk_levels": {
      "low": 0,
      "medium": 0,
      "high": 0
    },
    "largest_files": [],
    "most_critical_files": [],
    "refactor_candidates": [],
    "security_sensitive_files": []
  }
}
```

### **Universal Analysis Algorithms:**
- **File categorization**: Rule-based classification with framework detection
- **Risk assessment**: Multi-factor scoring (size + complexity + sensitivity + type)
- **Health scoring**: Weighted deduction system with project-type awareness
- **Dependency analysis**: Language-specific import/require parsing

---

## **Universal Quality Assurance Process**

### **Validation Steps:**
1. **Cross-reference verification**: Compare multiple data sources
2. **Completeness check**: Ensure all files are cataloged
3. **Consistency validation**: Verify category assignments
4. **Accuracy verification**: Confirm file sizes and metadata
5. **Framework detection**: Validate framework-specific patterns

### **Error Correction:**
- Fix categorization inconsistencies
- Correct dependency mappings
- Update risk assessments based on additional analysis
- Refine health score calculations
- Validate framework-specific metadata

---

## **Universal Output Artifacts**

1. **`inventory/inventory_manifest.json`** (Enhanced manifest)
   - Complete file inventory with enhanced metadata
   - Universal categorization system
   - Risk assessments and dependency mappings
   - Framework-specific metadata

---

## **Universal Process Efficiency Metrics**

- **Total Analysis Time**: ~20-40 minutes (project size dependent)
- **Files Processed**: Variable (typically 50-500 files)
- **Data Points Collected**: ~10-20 per file
- **Manifest Generated**: 1 comprehensive JSON document
- **Accuracy Rate**: 95-98% (validated against source files)

---

## **Standardized Universal Workflow**

### **Step 1: Create Universal Inventory Manifest**
```bash
# 1. Explore project structure
list_dir(target_directory="project-root")
list_dir(target_directory="project-root/src")
list_dir(target_directory="project-root/tests")
list_dir(target_directory="project-root/docs")

# 2. Collect file metadata
Get-ChildItem -Recurse -File | Select-Object FullName, Length, LastWriteTime

# 3. Analyze core files
read_file("package.json", "pyproject.toml", "Cargo.toml", "pom.xml", "main-entry-points")

# 4. Detect project type and framework
detect_project_type()
detect_framework()

# 5. Create enhanced manifest
write("inventory/inventory_manifest.json", enhanced_manifest_data)
```

### **Step 2: Universal Quality Assurance**
```bash
# 1. Validate completeness
verify_all_files_cataloged()

# 2. Check accuracy
cross_reference_metadata()

# 3. Confirm consistency
validate_categorization()
validate_framework_detection()
```

---

## **Framework-Specific Adaptations**

### **JavaScript/TypeScript Projects:**
- Detect React, Vue, Angular, Node.js patterns
- Analyze package.json dependencies
- Identify build tools (Webpack, Vite, Rollup)
- Check for TypeScript configuration

### **Python Projects:**
- Detect Django, Flask, FastAPI patterns
- Analyze requirements.txt or pyproject.toml
- Identify virtual environment usage
- Check for testing frameworks (pytest, unittest)

### **Java Projects:**
- Detect Spring, Maven, Gradle patterns
- Analyze pom.xml or build.gradle
- Identify testing frameworks (JUnit, TestNG)
- Check for build tools and dependencies

### **Go Projects:**
- Detect Gin, Echo, Fiber patterns
- Analyze go.mod dependencies
- Identify testing patterns
- Check for build and deployment configs

### **Rust Projects:**
- Detect Actix, Rocket, Warp patterns
- Analyze Cargo.toml dependencies
- Identify testing patterns
- Check for build and deployment configs

---

## **Next Steps**

After creating the inventory manifest, proceed to:
**`inventory_report_creation.md`** - For generating comprehensive project analysis reports

---

**Process Generated by:** Universal Project Inventory Analysis System  
**Version:** 1.0.0  
**Compatibility:** All programming languages and frameworks  
**Location:** `inventory/` (project root)  
**Status:** Universal ✅
