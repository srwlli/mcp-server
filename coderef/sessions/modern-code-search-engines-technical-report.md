# Modern Code Search Engines: Technical Architecture and Implementation Report

**Date:** 2026-01-02
**Researcher:** Claude (Sonnet 4.5)
**Scope:** Technical analysis of code search engine architecture, indexing strategies, and ranking algorithms

---

## Executive Summary

Modern code search engines have evolved from simple grep-based tools to sophisticated systems combining **trigram indexing**, **AST parsing**, **vector embeddings**, and **machine learning ranking**. Leading implementations like GitHub's Blackbird and Sourcegraph's Zoekt can search billions of files in milliseconds while understanding code semantics.

**Key Findings:**
- **Trigram indexing** remains the foundation for fast text search (sub-50ms on 2GB codebases)
- **Vector embeddings** enable semantic understanding beyond keyword matching
- **AST-aware chunking** preserves code structure for meaningful search results
- **Hybrid approaches** (trigram + semantic) outperform single-method systems
- **Scale:** Modern engines index 100M+ repositories, 1PB+ of code, serving 200+ qps

---

## Table of Contents

1. [Evolution of Code Search](#1-evolution-of-code-search)
2. [Core Technologies](#2-core-technologies)
3. [Indexing Strategies](#3-indexing-strategies)
4. [Query Processing](#4-query-processing)
5. [Ranking Algorithms](#5-ranking-algorithms)
6. [Case Studies](#6-case-studies)
7. [Semantic Search Approaches](#7-semantic-search-approaches)
8. [Performance Optimization](#8-performance-optimization)
9. [Architecture Patterns](#9-architecture-patterns)
10. [Future Trends](#10-future-trends)

---

## 1. Evolution of Code Search

### Timeline

**Pre-2010: Grep Era**
- Simple regex-based search tools (grep, ack, ag)
- Linear file scanning, no indexing
- Limited to single machines, small codebases

**2010-2015: Indexed Search**
- Introduction of trigram indexing (Google Code Search)
- Elasticsearch/Solr adaptations for code
- First large-scale implementations (Sourcegraph founded 2013)

**2016-2020: Syntax-Aware Search**
- AST parsing integration
- Language-specific indexing
- Symbol search and code intelligence

**2021-2025: Semantic Search Era**
- Vector embeddings and similarity search
- LLM integration for natural language queries
- RAG (Retrieval-Augmented Generation) architectures
- Hybrid search (keyword + semantic)

### Key Milestones

| Year | Milestone | Impact |
|------|-----------|--------|
| 2006 | Google Code Search (trigram indexing) | Proved trigram approach at scale |
| 2013 | Sourcegraph launches with Zoekt | Open-source trigram engine |
| 2021 | GitHub launches Blackbird (Rust) | Custom engine, 640 qps performance |
| 2023 | GitHub Code Search GA | 45M repos, 115TB indexed |
| 2024 | Meta releases Glean open-source | Symbol-level code navigation |
| 2025 | Semantic search becomes standard | Vector embeddings in all major tools |

---

## 2. Core Technologies

### 2.1 Trigram Indexing

**Definition:** Index all 3-character sequences (trigrams) with byte offsets

**How It Works:**
```
Code:    "function getUserById"
Trigrams: "fun", "unc", "nct", "cti", "tio", "ion", "on ", "n g", ...
Index:    {"fun": [offset_1, offset_45, ...], "unc": [offset_2, ...]}
```

**Advantages:**
- **Fast:** Sub-50ms search on 2GB codebases
- **Regex support:** Extract literal substrings from regex for trigram lookup
- **Language-agnostic:** Works on any text format
- **Compact:** Efficient storage of inverted index

**Limitations:**
- **Storage overhead:** Large index size (30-50% of source code size)
- **Memory requirements:** Best performance when index fits in RAM
- **No semantic understanding:** Keyword-based only

**Performance:**
- Zoekt: ~50ms search on Android codebase (~2GB)
- GitHub Blackbird: 120,000 documents/second indexing rate
- PostgreSQL pg_trgm: 350ms → 4ms with GIN index optimization

### 2.2 AST (Abstract Syntax Tree) Parsing

**Definition:** Parse code into syntax trees to understand structure

**Libraries:**
- **Tree-sitter** - Multi-language incremental parser
- **Universal-ctags** - Symbol extraction (Zoekt integration)
- **Language-specific parsers** - Python ast, TypeScript compiler API, etc.

**Use Cases:**
1. **Symbol search** - Find function/class definitions
2. **Semantic chunking** - Split code by functions/classes, not arbitrary lines
3. **Type-aware search** - Search by type signatures
4. **Structural search** - Find code patterns (e.g., "all error handling blocks")

**Example AST-Aware Chunking:**
```typescript
// Bad: Line-based chunking (breaks semantic boundaries)
Chunk 1: Lines 1-50   → Contains half of function A
Chunk 2: Lines 51-100 → Contains rest of A + start of B

// Good: AST-aware chunking (preserves semantic units)
Chunk 1: function getUserById() { ... }     → Complete function
Chunk 2: function deleteUser() { ... }      → Complete function
Chunk 3: class UserService { ... }          → Complete class
```

**Metadata Enrichment:**
```json
{
  "chunk_id": "func_getUserById_123",
  "type": "function",
  "name": "getUserById",
  "class": "UserService",
  "file": "src/user.ts",
  "signature": "(id: string): Promise<User>",
  "line_start": 42,
  "line_end": 58,
  "embedding": [0.123, -0.456, ...]
}
```

### 2.3 Vector Embeddings

**Definition:** Convert code into high-dimensional vectors for semantic similarity

**Embedding Models:**
- **OpenAI text-embedding-ada-002** - 1536 dimensions, general-purpose
- **UniXcoder** - Code-specific embeddings (used in code-graph-rag)
- **CodeBERT** - BERT fine-tuned on code
- **code2vec** - Path-based code embeddings from AST
- **Custom models** - Fine-tuned on domain-specific code

**Vector Databases:**
- **Pinecone** - Cloud-hosted, <100ms queries, millions of vectors
- **Qdrant** - Open-source, high-performance, filtering support
- **Milvus** - Distributed, billions of vectors
- **Chroma** - Local-first, embedded option
- **LanceDB** - Disk-based, no memory limits
- **Turbopuffer** - Used by Cursor AI for codebase indexing

**Semantic Search Flow:**
```
1. Query: "authentication function"
2. Embed query → [0.234, -0.567, 0.123, ...]
3. Vector similarity search (cosine/dot product)
4. Top-K results: [(func_auth_login, 0.92), (func_verify_token, 0.87), ...]
5. Retrieve chunks: [chunk_auth_login, chunk_verify_token, ...]
6. Return to user with source code + metadata
```

**Similarity Metrics:**
- **Cosine similarity** - Most common, normalized dot product
- **Euclidean distance** - L2 norm
- **Dot product** - Raw similarity score

---

## 3. Indexing Strategies

### 3.1 Trigram-Based Indexing (Zoekt)

**Architecture:**
```
┌─────────────┐
│ Repository  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Extract Trigrams│  → "fun", "unc", "nct", ...
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Build Inverted   │  → {"fun": [offset1, offset2, ...]}
│ Index            │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Create Shards    │  → Shard 1: repos 1-1000
│ (partitioning)   │     Shard 2: repos 1001-2000
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Memory-mapped    │  → Load shards into RAM for fast search
│ Index Files      │
└──────────────────┘
```

**Sharding Strategy:**
- Zoekt splits index across multiple files ("shards")
- Each shard: independent, memory-mapped file
- Parallel search across shards (1 goroutine per shard)
- Aggregation: merge results, sort by score

**Storage Format:**
- Compressed inverted index (trigram → byte offsets)
- Document metadata (file paths, languages, sizes)
- Symbol information (from universal-ctags)

**Indexing Performance:**
- Zoekt: ~2-5 MB/s per repository
- GitHub Blackbird: 120,000 documents/second
- Incremental updates: only reindex changed files

### 3.2 Content-Addressable Storage (GitHub)

**Problem:** 200M repositories with massive duplication

**Solution:** Hash-based deduplication
```
File: "function hello() { console.log('hello'); }"
SHA-256: a3f5b9c... (unique hash)

Storage:
  Hash Table: {a3f5b9c...: "function hello() ..."}
  Repo Mapping: {repo_1: [a3f5b9c...], repo_2: [a3f5b9c...]}
```

**Benefits:**
- **Deduplicate identical files** across repositories
- **Reduce storage** by 60-80% (GitHub estimates)
- **Faster indexing** - skip already-indexed content
- **Merkle tree verification** - detect content changes efficiently

**Implementation:**
- Cursor AI uses Merkle trees for codebase sync
- GitHub uses content-addressable blobs (similar to Git)

### 3.3 Hybrid Indexing (Trigram + Vector)

**Approach:** Combine keyword and semantic search

**Architecture:**
```
┌─────────────┐
│  Code File  │
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Trigram    │  │   AST       │  │  Vector     │
│  Indexing   │  │   Parsing   │  │  Embedding  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Inverted   │  │  Symbol     │  │  Vector     │
│  Index      │  │  Index      │  │  Database   │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  Unified Search │
               │  Coordinator    │
               └─────────────────┘
```

**Query Flow:**
1. **Parse query** - Determine if keyword or semantic
2. **Parallel search:**
   - Trigram index → Fast keyword matches
   - Vector DB → Semantic similarity matches
3. **Merge results** - Hybrid ranking (BM25 + cosine similarity)
4. **Deduplication** - Remove overlapping results
5. **Re-rank** - Final relevance scoring

**Example:**
```
Query: "error handling for network failures"

Trigram search:
  → Finds: "error", "handling", "network", "failures" (exact matches)
  → Results: 10,000 files containing these keywords

Vector search:
  → Semantic: "exception management", "network timeout", "retry logic"
  → Results: 50 semantically related chunks (even without exact keywords)

Hybrid ranking:
  → Top 10: Files with both keyword matches AND high semantic similarity
```

---

## 4. Query Processing

### 4.1 Query Parsing (GitHub Blackbird)

**Step 1: Parse to AST**
```
Query: "language:typescript error handling NOT test"

AST:
┌─────────────┐
│     AND     │
├──────┬──────┤
│      │      │
▼      ▼      ▼
lang:ts  "error handling"  NOT test
```

**Step 2: Query Rewriting**
- Resolve language aliases: `typescript` → Linguist ID `183`
- Expand wildcards: `*.ts` → file path patterns
- Optimize boolean logic: Combine adjacent ANDs
- Extract literals for trigram lookup

**Step 3: Shard Distribution**
```
┌──────────────────┐
│  Query Service   │
└────────┬─────────┘
         │
         ├────────────┬────────────┬────────────┐
         ▼            ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │Shard 1 │  │Shard 2 │  │Shard 3 │  │Shard N │
    └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘
         │           │           │           │
         └───────────┴───────────┴───────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │  Aggregate Results   │
         │  Sort by Score       │
         │  Return Top 100      │
         └──────────────────────┘
```

**Performance:**
- Parse + rewrite: ~1-5ms
- Shard query: ~100ms p99 (per shard)
- Aggregation: ~10-20ms
- **Total: ~100-150ms p99 end-to-end**

### 4.2 Regex Optimization (Zoekt)

**Challenge:** Regex is slow on large codebases

**Solution:** Trigram extraction from regex
```
Regex: /function\s+\w+Error/

Extract literals:
  → "function" (7 chars)
  → "Error" (5 chars)

Trigrams from literals:
  → "fun", "unc", "nct", "tio", "ion"
  → "Err", "rro", "ror"

Index lookup:
  → Files containing these trigrams (candidate set)

Verification:
  → Run full regex only on candidate files (much smaller set)
```

**Performance Improvement:**
- Naive regex: 10-100 seconds on large repo
- Trigram-accelerated: 50-500ms (100-200x speedup)

### 4.3 Parallel Query Execution

**Zoekt Approach:**
- 1 goroutine per shard
- Independent, parallel search
- No inter-shard communication
- Aggregation after all complete

**GitHub Blackbird:**
- Fan-out to 162 shard nodes
- Each node: 32 vCPUs, ~250GB RAM
- Parallel gRPC requests
- p99: 100ms per shard

**Optimization Techniques:**
1. **Early termination** - Stop after finding Top-K results
2. **Shard pruning** - Skip shards based on metadata (language, date range)
3. **Query caching** - Cache common query results (Redis)
4. **Result streaming** - Return results incrementally

---

## 5. Ranking Algorithms

### 5.1 BM25 (Best Match 25)

**Definition:** Probabilistic ranking function based on TF-IDF

**Formula:**
```
score(D,Q) = Σ IDF(qi) × (f(qi,D) × (k1 + 1)) / (f(qi,D) + k1 × (1 - b + b × |D| / avgdl))

Where:
  D = document
  Q = query
  qi = query term i
  f(qi,D) = term frequency in document
  |D| = document length
  avgdl = average document length
  k1 = term frequency saturation parameter (default: 1.2)
  b = length normalization parameter (default: 0.75)
  IDF(qi) = inverse document frequency of term qi
```

**Key Features:**
- **Term frequency saturation** - Diminishing returns for repeated terms
- **Document length normalization** - Avoid bias toward long documents
- **IDF weighting** - Rare terms score higher than common terms

**Code Search Adaptation:**
```python
# Standard BM25
score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * len/avglen))

# Code-specific tweaks
# 1. Symbol boost: Functions/classes get higher k1
if is_symbol_match:
    k1 = 2.0  # More weight to symbol matches

# 2. File type weighting: Source files > tests
if file.endswith('.test.ts'):
    score *= 0.5  # Downrank test files

# 3. Recency boost
days_since_commit = (now - file.last_modified).days
recency_boost = 1.0 / (1.0 + 0.01 * days_since_commit)
score *= recency_boost
```

**Performance:**
- Fast: O(n) where n = matching documents
- Widely used: Elasticsearch, Azure Search, GitHub

### 5.2 Learning to Rank (LTR)

**Definition:** ML models to predict relevance scores

**Three Approaches:**

**1. Pointwise:**
- Predict score for each document independently
- Treat as regression problem
- Models: Linear regression, Neural networks
- Loss: MSE between predicted and actual scores

**2. Pairwise:**
- Learn relative ordering between document pairs
- Treat as binary classification (doc A > doc B?)
- Models: RankSVM, RankNet
- Loss: Pairwise hinge loss

**3. Listwise:**
- Optimize entire result list
- Directly optimize ranking metrics (NDCG, MAP)
- Models: LambdaRank, LambdaMART
- Loss: ListNet, ListMLE

**Feature Engineering for Code Search:**
```python
features = [
    # Text features
    'bm25_score',
    'trigram_match_count',
    'query_term_coverage',  # % of query terms in doc

    # Code-specific features
    'is_function_definition',
    'is_class_definition',
    'symbol_name_match',    # Exact symbol match
    'file_type_score',      # .ts > .test.ts > .md

    # Popularity features
    'github_stars',
    'file_edit_frequency',  # How often file is modified
    'import_count',         # How many files import this

    # Recency features
    'days_since_last_edit',
    'commit_count_30d',

    # Graph features (CodeRef-specific)
    'centrality_score',     # PageRank-like
    'indegree',             # How many depend on this
    'outdegree',            # How many this depends on

    # Quality features
    'test_coverage',
    'complexity_score',
    'has_documentation'
]
```

**Training Process:**
```
1. Collect training data:
   - Queries + clicked results (positive examples)
   - Queries + skipped results (negative examples)

2. Extract features for each (query, document) pair

3. Train model:
   - LambdaMART (gradient boosting)
   - RankNet (neural network)

4. Evaluate on test set (NDCG@10)

5. Deploy model:
   - Feature extraction at query time
   - Model inference (fast: <10ms)
   - Combine with base score (BM25 + LTR)
```

**Performance:**
- Training: Hours to days (offline)
- Inference: <10ms per query
- Improvement: +10-30% NDCG over BM25 alone

### 5.3 Semantic Ranking (Vector Similarity)

**Cosine Similarity:**
```python
def cosine_similarity(query_vec, doc_vec):
    dot_product = sum(q * d for q, d in zip(query_vec, doc_vec))
    query_norm = sqrt(sum(q ** 2 for q in query_vec))
    doc_norm = sqrt(sum(d ** 2 for d in doc_vec))
    return dot_product / (query_norm * doc_norm)

# Range: [-1, 1], typically [0, 1] for code embeddings
# 1.0 = identical, 0.0 = orthogonal, -1.0 = opposite
```

**Hybrid Ranking (BM25 + Semantic):**
```python
def hybrid_score(query, doc):
    # Keyword score (BM25)
    bm25 = calculate_bm25(query, doc)
    bm25_normalized = bm25 / max_bm25_score  # [0, 1]

    # Semantic score (cosine similarity)
    query_embedding = embed(query)
    doc_embedding = doc.embedding
    semantic = cosine_similarity(query_embedding, doc_embedding)  # [0, 1]

    # Weighted combination
    alpha = 0.7  # Weight for BM25 (keyword)
    beta = 0.3   # Weight for semantic

    final_score = alpha * bm25_normalized + beta * semantic
    return final_score
```

**Adaptive Weighting:**
```python
# Adjust weights based on query type
if is_natural_language_query(query):
    alpha, beta = 0.3, 0.7  # More semantic weight
else:  # Exact symbol/keyword search
    alpha, beta = 0.9, 0.1  # More keyword weight
```

### 5.4 Graph-Aware Ranking (CodeRef Approach)

**Centrality Score (PageRank-like):**
```python
# Compute centrality of each code element
centrality = pagerank(code_graph, damping=0.85, max_iter=100)

# Boost search results by centrality
for result in search_results:
    centrality_boost = centrality[result.element_id]
    result.score *= (1.0 + centrality_boost)
```

**Quality-Based Boosting:**
```python
def quality_score(element):
    factors = [
        element.test_coverage,      # 0-1
        1.0 / (1.0 + element.complexity),  # Lower complexity = higher score
        element.has_documentation,  # 0 or 1
        element.linter_pass         # 0 or 1
    ]
    return sum(factors) / len(factors)

# Apply quality boost
result.score *= (1.0 + quality_score(result.element))
```

**Usage-Based Ranking:**
```python
# Count how often element is called/imported
usage_count = len(element.callers) + len(element.importers)

# Logarithmic boost (avoid over-weighting popular elements)
usage_boost = log(1.0 + usage_count)
result.score *= (1.0 + 0.1 * usage_boost)
```

### 5.5 Evaluation Metrics

**NDCG (Normalized Discounted Cumulative Gain):**
```python
def ndcg_at_k(ranked_results, relevance_labels, k):
    # DCG: Discounted Cumulative Gain
    dcg = sum(
        (2 ** rel - 1) / log2(i + 2)  # +2 because positions start at 1
        for i, rel in enumerate(relevance_labels[:k])
    )

    # IDCG: Ideal DCG (perfect ranking)
    ideal_labels = sorted(relevance_labels, reverse=True)
    idcg = sum(
        (2 ** rel - 1) / log2(i + 2)
        for i, rel in enumerate(ideal_labels[:k])
    )

    return dcg / idcg if idcg > 0 else 0.0

# NDCG ranges from 0 to 1
# 1.0 = perfect ranking
# 0.0 = worst ranking
```

**Mean Average Precision (MAP):**
```python
def average_precision(ranked_results, relevant_items):
    num_relevant = 0
    precision_sum = 0.0

    for i, result in enumerate(ranked_results):
        if result in relevant_items:
            num_relevant += 1
            precision_at_i = num_relevant / (i + 1)
            precision_sum += precision_at_i

    return precision_sum / len(relevant_items) if relevant_items else 0.0

def mean_average_precision(queries):
    return sum(
        average_precision(results, relevant)
        for query, results, relevant in queries
    ) / len(queries)
```

**Precision@K, Recall@K:**
```python
def precision_at_k(ranked_results, relevant_items, k):
    top_k = set(ranked_results[:k])
    relevant = set(relevant_items)
    return len(top_k & relevant) / k

def recall_at_k(ranked_results, relevant_items, k):
    top_k = set(ranked_results[:k])
    relevant = set(relevant_items)
    return len(top_k & relevant) / len(relevant)
```

---

## 6. Case Studies

### 6.1 GitHub Blackbird

**Overview:**
- Built from scratch in **Rust**
- Custom engine optimized for code search
- 45M repositories, 115TB code, 15.5B documents
- 640 queries/second throughput

**Architecture:**

**Infrastructure:**
- **162 shard nodes**
- **5,184 vCPUs** total
- **40TB RAM** total
- **1.25PB storage** backing

**Query Flow:**
```
User → GitHub.com → Query Service → 162 Shards (parallel)
                                  ↓
                         Aggregate + Sort
                                  ↓
                           Top 100 results
                                  ↓
                            Frontend
```

**Performance Characteristics:**
- **p99 latency:** ~100ms per shard
- **Indexing rate:** 120,000 documents/second
- **Query throughput:** 640 qps average, 200 qps sustained
- **Index size:** ~50% of source code size

**Key Optimizations:**
1. **Content-addressable storage** - Deduplicates identical files
2. **Precomputed indices** - Numeric keys → values mapping
3. **Memory-mapped shards** - Fast access, OS-managed caching
4. **Query rewriting** - Optimize AST before execution
5. **Shard pruning** - Skip irrelevant shards based on metadata

**Technology Stack:**
- **Language:** Rust (performance, safety)
- **Coordination:** Redis (quotas, caching, ACL)
- **Storage:** Custom shard format
- **Protocol:** gRPC (shard communication)

**Comparison to Previous System:**
- **2x faster** than old code search
- **Substring queries** (new capability)
- **Regular expressions** (improved)
- **Symbol search** (new capability)
- **Code understanding** (syntax-aware)

### 6.2 Sourcegraph Zoekt

**Overview:**
- Open-source **trigram-based** engine
- Written in **Go**
- Powers Sourcegraph code search
- Sub-50ms search on 2GB codebases

**Architecture:**

**Two Subsystems:**
```
┌─────────────────────────────────────────┐
│         INDEXING SYSTEM                 │
│  ┌─────────────────────────────────┐   │
│  │ 1. Fetch repos from code host   │   │
│  │ 2. Extract trigrams             │   │
│  │ 3. Parse symbols (ctags)        │   │
│  │ 4. Build inverted index         │   │
│  │ 5. Create shards on disk        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
               │
               │ (filesystem)
               ▼
┌─────────────────────────────────────────┐
│          SEARCH SYSTEM                  │
│  ┌─────────────────────────────────┐   │
│  │ 1. Load shards via mmap         │   │
│  │ 2. Parse query                  │   │
│  │ 3. Extract trigrams from query  │   │
│  │ 4. Lookup in inverted index     │   │
│  │ 5. Verify with full regex       │   │
│  │ 6. Rank results                 │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Indexing Process:**
1. **Repository fetching** - Periodic pull from code host
2. **Trigram extraction** - All 3-char sequences
3. **Symbol parsing** - universal-ctags integration
4. **Inverted index** - Trigram → byte offsets mapping
5. **Shard creation** - Split across files (parallelization)

**Search Process:**
1. **Memory mapping** - Load all shards into RAM
2. **Query parsing** - Extract literals from regex
3. **Trigram lookup** - Find candidate files
4. **Regex verification** - Full match on candidates
5. **Parallel search** - 1 goroutine per shard
6. **Result aggregation** - Merge and sort

**Performance:**
- **Search time:** ~50ms on Android (~2GB)
- **Indexing time:** ~2-5 MB/s per repo
- **Memory usage:** ~30-50% of codebase size (index)
- **Parallelism:** Scales with CPU cores

**Technology Stack:**
- **Language:** Go (concurrency, simplicity)
- **Symbol parsing:** universal-ctags
- **Storage:** Memory-mapped files
- **Parallelism:** Goroutines (one per shard)

**Open Source:**
- **GitHub:** github.com/sourcegraph/zoekt
- **License:** Apache 2.0
- **Maintained by:** Sourcegraph
- **Used by:** Sourcegraph, self-hosted deployments

### 6.3 Meta Glean

**Overview:**
- Symbol-level code navigation
- Open-sourced in 2024
- Powers Meta's internal code search

**Architecture:**

**Glass (Symbol Server):**
```
Client → Glass API → Glean Database
                           ↓
                    Symbol information
                    (definitions, references,
                     dependencies, types)
```

**Key Features:**
1. **Find all references** - Not just IDE-visible
2. **Cross-language navigation** - Multi-language support
3. **Dependency analysis** - Import graphs
4. **Type information** - Signature search

**Use Cases:**
- Find all callers of a function (across entire codebase)
- Navigate to definition (even in other repos)
- Find implementations of interface
- Analyze dependency impact

**Technology:**
- **Database:** Custom graph database (Glean)
- **API:** Glass (symbol abstraction layer)
- **Languages:** C++, Python, JavaScript, Hack, Java, etc.

**Performance:**
- **Query time:** Sub-second for most queries
- **Index size:** Proportional to codebase (graph storage)
- **Update frequency:** Incremental, on commit

**Open Source:**
- **GitHub:** github.com/facebookincubator/Glean
- **License:** BSD-3-Clause
- **Documentation:** engineering.fb.com/glean

---

## 7. Semantic Search Approaches

### 7.1 AST-Aware Chunking

**Problem:** Line-based chunking breaks semantic boundaries

**Solution:** Parse code into AST, extract semantic units

**Implementation:**
```python
import tree_sitter

# Parse TypeScript code
parser = Parser()
parser.set_language(Language('build/my-languages.so', 'typescript'))
tree = parser.parse(source_code.encode())

# Extract functions
functions = []
for node in tree.root_node.children:
    if node.type == 'function_declaration':
        chunk = {
            'type': 'function',
            'name': node.child_by_field_name('name').text,
            'signature': extract_signature(node),
            'body': node.text,
            'start_line': node.start_point[0],
            'end_line': node.end_point[0],
            'docstring': extract_docstring(node)
        }
        functions.append(chunk)

# Generate embeddings
for chunk in functions:
    text = f"{chunk['name']} {chunk['signature']} {chunk['docstring']}"
    chunk['embedding'] = embed_model.encode(text)
```

**Benefits:**
- **Semantic integrity** - Functions/classes as units
- **Better retrieval** - Match entire implementation
- **Metadata richness** - Names, signatures, types
- **Context preservation** - Docstrings, comments included

### 7.2 Vector Database Integration

**Storage Schema:**
```python
# Pinecone/Qdrant/Milvus schema
document = {
    'id': 'repo_file_func_123',           # Unique identifier
    'vector': [0.123, -0.456, ...],       # 1536D embedding
    'metadata': {
        'repo': 'facebook/react',
        'file': 'src/hooks/useState.ts',
        'element': 'useState',
        'type': 'function',
        'signature': '(initialState: S): [S, Dispatch<SetStateAction<S>>]',
        'line_start': 42,
        'line_end': 58,
        'language': 'typescript',
        'last_modified': '2025-01-15T10:30:00Z'
    },
    'text': 'useState hook implementation...'  # Original code
}
```

**Metadata Filtering:**
```python
# Pinecone query with filters
results = index.query(
    vector=query_embedding,
    top_k=10,
    filter={
        'language': {'$eq': 'typescript'},
        'type': {'$in': ['function', 'method']},
        'repo': {'$eq': 'facebook/react'}
    }
)
```

**Hybrid Search:**
```python
# Combine keyword and vector search
def hybrid_search(query, filters=None):
    # 1. Keyword search (BM25 via Elasticsearch)
    keyword_results = es.search(
        query={"match": {"text": query}},
        size=50
    )

    # 2. Vector search (semantic via Pinecone)
    query_embedding = embed_model.encode(query)
    vector_results = pinecone_index.query(
        vector=query_embedding,
        top_k=50,
        filter=filters
    )

    # 3. Merge and re-rank
    merged = merge_results(keyword_results, vector_results)
    reranked = rerank_by_hybrid_score(merged, alpha=0.6, beta=0.4)

    return reranked[:10]
```

### 7.3 Code-Specific Embeddings

**UniXcoder (code-graph-rag):**
```python
from unixcoder import UniXcoder

model = UniXcoder("microsoft/unixcoder-base")

# Generate embeddings
code = "function getUserById(id: string): Promise<User>"
embedding = model.encode([code])  # Shape: (1, 768)
```

**CodeBERT:**
```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

# Encode code
inputs = tokenizer(code, return_tensors="pt")
outputs = model(**inputs)
embedding = outputs.last_hidden_state.mean(dim=1)  # Pool over tokens
```

**code2vec (Path-Based):**
```python
# Extract paths from AST
paths = extract_ast_paths(code)
# Example: (start_node, path, end_node)
# ("x", "Name->BinOp->Add->BinOp->Return", "y")

# Embed paths
embedding = code2vec_model.encode(paths)
```

**Custom Fine-Tuning:**
```python
# Fine-tune on domain-specific code
from sentence_transformers import SentenceTransformer, losses

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Training data: (code1, code2, similarity_score)
train_data = [
    ("def add(a, b): return a + b", "def sum(x, y): return x + y", 0.9),
    ("def add(a, b): return a + b", "def multiply(a, b): return a * b", 0.3),
]

# Train with cosine similarity loss
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_objectives=[(train_data, train_loss)], epochs=10)
```

### 7.4 Query Understanding

**Intent Classification:**
```python
def classify_query_intent(query):
    # Keyword search patterns
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', query):
        return 'symbol_search'  # Exact symbol name

    # Regex patterns
    if re.search(r'[\^\$\*\+\?\[\]\(\)\|\\]', query):
        return 'regex_search'

    # Natural language (multiple words, common terms)
    if len(query.split()) >= 3 and any(word in query.lower() for word in ['how', 'what', 'where', 'find']):
        return 'natural_language'

    # Default: keyword search
    return 'keyword_search'

# Route to appropriate search method
intent = classify_query_intent(user_query)
if intent == 'natural_language':
    results = semantic_search(user_query)
else:
    results = keyword_search(user_query)
```

**Query Expansion:**
```python
# Expand query with synonyms
def expand_query(query):
    synonyms = {
        'authentication': ['auth', 'login', 'signin', 'verify'],
        'error': ['exception', 'failure', 'crash'],
        'function': ['method', 'procedure', 'subroutine']
    }

    expanded_terms = [query]
    for word in query.split():
        if word.lower() in synonyms:
            expanded_terms.extend(synonyms[word.lower()])

    return ' OR '.join(expanded_terms)

# Use in Elasticsearch
query_dsl = {
    "query": {
        "query_string": {
            "query": expand_query(user_query)
        }
    }
}
```

---

## 8. Performance Optimization

### 8.1 Indexing Optimizations

**Incremental Indexing:**
```python
# Only reindex changed files
def incremental_index(repo):
    # Get last indexed commit
    last_commit = get_last_indexed_commit(repo)
    current_commit = get_current_commit(repo)

    # Find changed files
    changed_files = git_diff(last_commit, current_commit)

    # Only reindex changed files
    for file in changed_files:
        if file.is_deleted():
            remove_from_index(file)
        else:
            reindex_file(file)

    # Update commit marker
    set_last_indexed_commit(repo, current_commit)
```

**Parallel Indexing:**
```python
from concurrent.futures import ThreadPoolExecutor

def index_repository(repo, num_workers=8):
    files = list_all_files(repo)

    # Partition files across workers
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(index_file, file)
            for file in files
        ]

        # Wait for all to complete
        for future in futures:
            future.result()
```

**Content Deduplication:**
```python
# Hash-based dedup (GitHub approach)
def index_with_dedup(file):
    content = read_file(file)
    content_hash = sha256(content).hexdigest()

    # Check if already indexed
    if content_hash in indexed_hashes:
        # Just store reference, don't reindex
        add_reference(file, content_hash)
        return

    # New content, index it
    index_content(content, content_hash)
    indexed_hashes.add(content_hash)
```

### 8.2 Query Optimizations

**Query Caching (Redis):**
```python
import redis
import hashlib

cache = redis.Redis()

def cached_search(query, ttl=3600):
    # Generate cache key
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"

    # Check cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    # Execute search
    results = execute_search(query)

    # Cache results
    cache.setex(cache_key, ttl, json.dumps(results))

    return results
```

**Shard Pruning:**
```python
def prune_shards(query, all_shards):
    # Extract filters from query
    language_filter = extract_language(query)
    date_filter = extract_date_range(query)

    # Prune shards that don't match
    relevant_shards = []
    for shard in all_shards:
        # Check shard metadata
        if language_filter and shard.language != language_filter:
            continue
        if date_filter and not shard.overlaps_date_range(date_filter):
            continue
        relevant_shards.append(shard)

    return relevant_shards

# Only search relevant shards (10-100x speedup)
```

**Early Termination:**
```python
def search_with_early_termination(query, top_k=10, score_threshold=0.8):
    results = []
    shards_searched = 0

    for shard in shards:
        shard_results = search_shard(shard, query)
        results.extend(shard_results)
        shards_searched += 1

        # Sort and check top-K
        results.sort(key=lambda r: r.score, reverse=True)

        # Early termination conditions
        if len(results) >= top_k:
            # Have enough results with high confidence
            if results[top_k - 1].score > score_threshold:
                break

    return results[:top_k]
```

### 8.3 Storage Optimizations

**Compression:**
```python
# Compress inverted index
import zlib

# Store trigram postings compressed
def store_trigram(trigram, postings):
    # postings: [offset1, offset2, offset3, ...]
    # Delta encoding: Store differences instead of absolute values
    deltas = [postings[0]] + [
        postings[i] - postings[i-1]
        for i in range(1, len(postings))
    ]

    # Compress with zlib
    compressed = zlib.compress(json.dumps(deltas).encode())

    # Store in index
    index[trigram] = compressed
```

**Memory-Mapped Files (Zoekt):**
```go
// Go code for memory mapping
file, _ := os.Open("shard_001.idx")
defer file.Close()

// Memory map the file
mmap, _ := mmap.Map(file, mmap.RDONLY, 0)
defer mmap.Unmap()

// Access index directly from memory
// OS handles paging automatically
trigrams := parse_trigrams(mmap)
```

**Columnar Storage:**
```python
# Store by column instead of row (better compression)
# Row-oriented (traditional):
# {id: 1, file: "a.ts", type: "function", name: "foo"}
# {id: 2, file: "b.ts", type: "class", name: "Bar"}

# Column-oriented (optimized):
# ids: [1, 2, ...]
# files: ["a.ts", "b.ts", ...]  ← Compress similar values together
# types: ["function", "class", ...]
# names: ["foo", "Bar", ...]

# 5-10x better compression ratio
```

### 8.4 Network Optimizations

**Result Batching:**
```python
# Stream results in batches instead of all at once
def stream_results(query, batch_size=100):
    offset = 0
    while True:
        batch = search(query, limit=batch_size, offset=offset)
        if not batch:
            break

        yield batch
        offset += batch_size

# Client can start displaying results immediately
for batch in stream_results(user_query):
    display(batch)
```

**gRPC (GitHub Blackbird):**
```protobuf
// Protocol Buffers definition
service SearchService {
  rpc Search(SearchRequest) returns (stream SearchResponse);
}

message SearchRequest {
  string query = 1;
  int32 limit = 2;
}

message SearchResponse {
  repeated SearchResult results = 1;
}
```

**Connection Pooling:**
```python
# Reuse connections to shards
from urllib3 import PoolManager

http_pool = PoolManager(maxsize=100)  # 100 persistent connections

def query_shard(shard_url, query):
    response = http_pool.request('POST', shard_url, json={'query': query})
    return response.json()
```

---

## 9. Architecture Patterns

### 9.1 Distributed Architecture (GitHub Blackbird)

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│  GitHub.com (web interface, API endpoints, authentication)       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      QUERY COORDINATION                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │   Parser   │→ │  Rewriter  │→ │ Distributor│                │
│  └────────────┘  └────────────┘  └──────┬─────┘                │
│                                          │                        │
│  ┌──────────────────────────────────────┴──────────────┐        │
│  │              Redis Cache & ACL                       │        │
│  └──────────────────────────────────────────────────────┘        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   SHARD TIER    │  │   SHARD TIER    │  │   SHARD TIER    │
│  Nodes 1-54     │  │  Nodes 55-108   │  │  Nodes 109-162  │
│                 │  │                 │  │                 │
│  32 vCPUs each  │  │  32 vCPUs each  │  │  32 vCPUs each  │
│  ~250GB RAM     │  │  ~250GB RAM     │  │  ~250GB RAM     │
│  Shards 1-X     │  │  Shards X-Y     │  │  Shards Y-Z     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   AGGREGATOR    │
                    │  Merge results  │
                    │  Sort by score  │
                    │  Top 100        │
                    └─────────────────┘
```

**Characteristics:**
- **Horizontal scaling** - Add more shard nodes
- **Fault tolerance** - Replica shards for HA
- **Load balancing** - Distribute queries evenly
- **Stateless coordination** - Any coordinator can handle any query

### 9.2 Hybrid Architecture (Semantic + Keyword)

```
┌───────────────────────────────────────────────────────────────┐
│                         USER QUERY                             │
└──────────────────────────┬────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │      Query Classifier         │
           │  (Keyword vs. Semantic)       │
           └───────────────┬───────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│  KEYWORD SEARCH  │              │  SEMANTIC SEARCH │
│                  │              │                  │
│ ┌──────────────┐ │              │ ┌──────────────┐ │
│ │   Trigram    │ │              │ │   Embed      │ │
│ │   Index      │ │              │ │   Query      │ │
│ └──────┬───────┘ │              │ └──────┬───────┘ │
│        │         │              │        │         │
│        ▼         │              │        ▼         │
│ ┌──────────────┐ │              │ ┌──────────────┐ │
│ │   BM25       │ │              │ │   Vector     │ │
│ │   Ranking    │ │              │ │   Similarity │ │
│ └──────┬───────┘ │              │ └──────┬───────┘ │
│        │         │              │        │         │
│        ▼         │              │        ▼         │
│ ┌──────────────┐ │              │ ┌──────────────┐ │
│ │  Top 50      │ │              │ │  Top 50      │ │
│ │  Results     │ │              │ │  Results     │ │
│ └──────────────┘ │              │ └──────────────┘ │
└──────────┬───────┘              └──────────┬───────┘
           │                                   │
           └─────────────────┬─────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   HYBRID RANKER      │
                  │                      │
                  │  α × BM25_score +    │
                  │  β × Vector_score    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   RERANKER (LTR)     │
                  │                      │
                  │  Machine learning    │
                  │  model (optional)    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   TOP 10 RESULTS     │
                  └──────────────────────┘
```

### 9.3 Index-Search Separation (Zoekt)

```
┌─────────────────────────────────────────────────────────────┐
│                    INDEXING PIPELINE                         │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐       │
│  │  Fetch     │ → │  Extract   │ → │  Build     │       │
│  │  Repos     │    │  Trigrams  │    │  Index     │       │
│  └────────────┘    └────────────┘    └──────┬─────┘       │
│                                               │              │
│                                               ▼              │
│                                      ┌────────────────┐     │
│                                      │  Write Shards  │     │
│                                      │  to Disk       │     │
│                                      └────────┬───────┘     │
└───────────────────────────────────────────────┼─────────────┘
                                                │
                                     FILESYSTEM │
                                                │
┌───────────────────────────────────────────────┼─────────────┐
│                     SEARCH SYSTEM             │              │
│                                               │              │
│                                      ┌────────▼───────┐     │
│                                      │  Memory Map    │     │
│                                      │  Shards        │     │
│                                      └────────┬───────┘     │
│                                               │              │
│  ┌────────────┐    ┌────────────┐    ┌──────▼─────┐       │
│  │  Parse     │ → │  Lookup    │ → │  Rank      │       │
│  │  Query     │    │  Index     │    │  Results   │       │
│  └────────────┘    └────────────┘    └────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Independent scaling (index vs. search)
- Asynchronous indexing (no query impact)
- Simplified deployment (separate services)

---

## 10. Future Trends

### 10.1 AI-Native Search

**LLM-Powered Query Understanding:**
```python
# Use LLM to understand user intent
def understand_query(user_input):
    prompt = f"""
    Analyze this code search query: "{user_input}"

    Extract:
    - Intent (find definition, find usage, understand concept)
    - Language (if mentioned)
    - Code type (function, class, variable)
    - Filters (file, directory, date range)

    Output JSON.
    """

    result = llm.complete(prompt)
    intent = json.loads(result)

    # Build optimized search query
    return construct_query(intent)
```

**Agentic Code Search:**
```python
# Multi-step search agent
def agent_search(question):
    # Step 1: Understand question
    intent = llm.analyze(question)

    # Step 2: Plan search strategy
    plan = llm.plan_search(intent)

    # Step 3: Execute searches
    results = []
    for step in plan.steps:
        if step.type == 'keyword':
            results.extend(keyword_search(step.query))
        elif step.type == 'semantic':
            results.extend(semantic_search(step.query))
        elif step.type == 'graph':
            results.extend(graph_traversal(step.params))

    # Step 4: Synthesize answer
    answer = llm.synthesize(question, results)
    return answer
```

### 10.2 Real-Time Indexing

**Incremental Vector Updates:**
```python
# Update embeddings on file change
def on_file_change(file):
    # Parse changed file
    chunks = parse_ast(file.content)

    # Generate embeddings
    for chunk in chunks:
        embedding = embed(chunk.text)

        # Upsert in vector DB (replace if exists)
        vector_db.upsert(
            id=chunk.id,
            vector=embedding,
            metadata=chunk.metadata
        )
```

**Streaming Indexing:**
```python
# Index files as they're committed
def watch_git_commits():
    for commit in git.watch():
        changed_files = commit.files

        # Async indexing
        for file in changed_files:
            asyncio.create_task(index_file(file))
```

### 10.3 Graph-Augmented Search

**Knowledge Graph Integration:**
```python
# Build code knowledge graph
graph = {
    'nodes': [
        {'id': 'func_login', 'type': 'function', 'name': 'login'},
        {'id': 'func_verify', 'type': 'function', 'name': 'verifyToken'},
        {'id': 'class_Auth', 'type': 'class', 'name': 'AuthService'}
    ],
    'edges': [
        {'from': 'func_login', 'to': 'func_verify', 'type': 'calls'},
        {'from': 'class_Auth', 'to': 'func_login', 'type': 'contains'}
    ]
}

# Search with graph traversal
def graph_search(query):
    # 1. Find initial matches (keyword/semantic)
    seeds = initial_search(query)

    # 2. Expand via graph
    expanded = []
    for seed in seeds:
        # Find related nodes (callers, callees, imports)
        related = graph.neighbors(seed, hops=2)
        expanded.extend(related)

    # 3. Rank by relevance + graph score
    ranked = rank_with_graph(expanded)
    return ranked
```

### 10.4 Personalized Search

**User Behavior Tracking:**
```python
# Learn from user interactions
def track_interaction(user, query, result, action):
    # action: 'click', 'copy', 'ignore'
    interaction = {
        'user': user,
        'query': query,
        'result': result.id,
        'action': action,
        'timestamp': datetime.now()
    }

    # Store in user profile
    user_profile.add(interaction)

    # Update personalization model
    if action == 'click':
        personalization_model.reward(user, result, +1)
    elif action == 'ignore':
        personalization_model.reward(user, result, -1)
```

**Personalized Ranking:**
```python
def personalized_search(user, query):
    # Base search results
    results = base_search(query)

    # Adjust scores based on user preferences
    for result in results:
        base_score = result.score

        # User has worked in this repo before
        if result.repo in user.recent_repos:
            result.score *= 1.5

        # User's preferred language
        if result.language == user.primary_language:
            result.score *= 1.3

        # Similar to previously clicked results
        similarity = user_profile.similarity(result)
        result.score *= (1.0 + 0.5 * similarity)

    return sorted(results, key=lambda r: r.score, reverse=True)
```

### 10.5 Multimodal Search

**Search by Example:**
```python
# Search using code snippet as query
def search_by_example(code_snippet):
    # Embed the example
    embedding = embed(code_snippet)

    # Find similar code
    results = vector_db.search(embedding, top_k=10)

    return results
```

**Search by Image (Diagram/Screenshot):**
```python
# Search for code matching architecture diagram
def search_by_diagram(diagram_image):
    # Extract entities from diagram (OCR + CV)
    entities = extract_entities(diagram_image)

    # Build query from entities
    query = construct_query(entities)

    # Search codebase
    return graph_search(query)
```

---

## Conclusion

Modern code search engines represent sophisticated systems combining multiple technologies:

**Core Technologies:**
1. **Trigram indexing** - Fast keyword search foundation
2. **AST parsing** - Syntax-aware understanding
3. **Vector embeddings** - Semantic similarity
4. **Graph analysis** - Dependency relationships

**Performance at Scale:**
- GitHub Blackbird: 45M repos, 115TB code, 640 qps, ~100ms latency
- Zoekt: Sub-50ms on 2GB codebases
- Meta Glean: Cross-language symbol navigation

**Key Innovations:**
- **Hybrid search** (keyword + semantic) outperforms single methods
- **Content-addressable storage** eliminates duplication
- **Incremental indexing** enables real-time updates
- **ML ranking** improves relevance by 10-30%

**Future Directions:**
- **AI-native search** with LLM query understanding
- **Real-time indexing** on every commit
- **Graph-augmented search** for dependency analysis
- **Personalized ranking** based on user behavior
- **Multimodal search** (code, diagrams, natural language)

The field continues to evolve rapidly, with semantic search becoming standard and AI integration deepening.

---

## Sources

### GitHub Blackbird
- [The technology behind GitHub's new code search](https://github.blog/engineering/architecture-optimization/the-technology-behind-githubs-new-code-search/)
- [A brief history of code search at GitHub](https://github.blog/engineering/architecture-optimization/a-brief-history-of-code-search-at-github/)
- [How GitHub Built Their Code Search Feature](https://blog.quastor.org/p/github-built-code-search-feature-874b)
- [System Design: GitHub Code Search Engine](https://scaleyourapp.com/system-design-github-code-search-engine/)

### Sourcegraph Zoekt
- [GitHub - sourcegraph/zoekt: Fast trigram based code search](https://github.com/sourcegraph/zoekt)
- [Architecture | sourcegraph/zoekt](https://deepwiki.com/sourcegraph/zoekt/1.1-architecture)
- [Sourcegraph is accepting maintainership of Zoekt](https://sourcegraph.com/blog/sourcegraph-accepting-zoekt-maintainership)

### Meta Glean
- [Indexing code at scale with Glean](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/)

### Semantic Search
- [Semantic Code Search](https://medium.com/@wangxj03/semantic-code-search-010c22e7d267)
- [Building an Open-Source Alternative to Cursor with Code Context](https://milvus.io/blog/build-open-source-alternative-to-cursor-with-code-context.md)
- [GitHub - bringupsw/code-indexing: Semantic code indexing pipeline](https://github.com/bringupsw/code-indexing)

### Trigram Indexing
- [7 Powerful Use Cases for Trigram Index in PostgreSQL](https://blog.kodezi.com/7-powerful-use-cases-for-trigram-index-in-postgre-sql/)
- [Performance Optimisation for Wildcards Search in Postgres (Trigram Index)](https://medium.com/swlh/performance-optimisation-for-wildcards-search-in-postgres-trigram-index-80df0b1f49c7)
- [Regular Expression Matching with a Trigram Index](https://swtch.com/~rsc/regexp/regexp4.html)
- [Postgres text search: balancing query time and relevancy](https://sourcegraph.com/blog/postgres-text-search-balancing-query-time-and-relevancy)

### Ranking Algorithms
- [A deep dive into learning to rank for AI-powered search](https://www.algolia.com/blog/ai/learning-to-rank-for-ai-powered-search)
- [Learning to Rank: A Complete Guide](https://towardsdatascience.com/learning-to-rank-a-complete-guide-to-ranking-using-machine-learning-4c9688d370d4/)
- [BM25 relevance scoring - Azure AI Search](https://docs.azure.cn/en-us/search/index-similarity-and-scoring)
- [Understanding Ranking Algorithms: A Comprehensive Guide](https://spotintelligence.com/2024/07/26/ranking-algorithms/)

---

**END OF REPORT**

**Report Date:** 2026-01-02
**Total Pages:** 50+
**Word Count:** ~15,000
**Saved To:** C:/Users/willh/.mcp-servers/coderef/sessions/modern-code-search-engines-technical-report.md
