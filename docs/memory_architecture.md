# Memory System Architecture

## Overview

The Odoo AI Configurator uses a dual-memory system for intelligent learning and context persistence:

1. **Lessons Learned** (SQLite) - Error tracking and solution database
2. **RAG Memory** (ChromaDB) - Vector database for semantic context search

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Base Agent                              │
│  ┌────────────────────────────────────────────────┐     │
│  │  Memory Systems                                 │     │
│  │  ├─ Lessons Learned (SQLite)                   │     │
│  │  └─ RAG Memory (ChromaDB)                      │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Company  │  │ Module   │  │ Product  │
│ Agent    │  │ Agent    │  │ Agent    │
└──────────┘  └──────────┘  └──────────┘
     │             │             │
     ▼             ▼             ▼
┌──────────────────────────────────────┐
│     Memory Storage                    │
│  ┌─────────────────────────────────┐ │
│  │  lessons.db (SQLite)            │ │
│  │  ├─ errors                      │ │
│  │  ├─ solutions                   │ │
│  │  └─ metadata                    │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │  rag/ (ChromaDB)                │ │
│  │  ├─ embeddings                  │ │
│  │  ├─ documents                   │ │
│  │  └─ metadata                    │ │
│  └─────────────────────────────────┘ │
└──────────────────────────────────────┘
```

---

## 1. Lessons Learned Database (SQLite)

### Purpose
Store errors and solutions for each agent to learn from past mistakes.

### Schema

```sql
CREATE TABLE lessons_learned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,           -- e.g., "ModuleAgent"
    error_type TEXT NOT NULL,           -- e.g., "IndexError"
    error_message TEXT,                 -- Full error message
    context TEXT,                       -- What was being done
    solution TEXT,                      -- How it was solved
    success BOOLEAN DEFAULT 0,          -- 0=error, 1=solution
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                       -- JSON metadata
);

CREATE INDEX idx_agent_error ON lessons_learned(agent_name, error_type);
CREATE INDEX idx_success ON lessons_learned(success, agent_name);
```

### Data Flow

```
1. Agent encounters error
   ↓
2. record_error(agent_name, error_type, error_msg, context)
   ↓
3. Stored in lessons.db
   ↓
4. Next time similar error occurs
   ↓
5. get_solutions(agent_name, error_type)
   ↓
6. Returns known solutions
```

### Example Data

```json
{
  "id": 1,
  "agent_name": "ModuleAgent",
  "error_type": "IndexError",
  "error_message": "tuple index out of range",
  "context": "Installing stock module on Odoo 16",
  "solution": null,
  "success": false,
  "timestamp": "2026-01-13T22:00:00"
}

{
  "id": 2,
  "agent_name": "ModuleAgent",
  "error_type": "IndexError",
  "error_message": null,
  "context": "Odoo 16 has compatibility issues",
  "solution": "Update to Odoo 17",
  "success": true,
  "timestamp": "2026-01-13T22:05:00"
}
```

### API Methods

```python
class LessonsLearned:
    def record_error(agent_name, error_type, error_msg, context)
    def record_solution(agent_name, error_type, solution, context)
    def get_solutions(agent_name, error_type, limit=5)
    def has_seen_error(agent_name, error_type)
    def get_error_count(agent_name, error_type)
    def get_all_lessons(agent_name=None, success_only=True)
    def get_stats()
```

---

## 2. RAG Memory System (ChromaDB)

### Purpose
Store and retrieve context using semantic search with vector embeddings.

### Architecture

```
Text Input
    ↓
Sentence Transformer (all-MiniLM-L6-v2)
    ↓
384-dimensional vector embedding
    ↓
ChromaDB Collection
    ↓
Similarity Search
    ↓
Relevant Context
```

### Collection Schema

```python
Collection: "odoo_context"
├── Documents: Text content
├── Embeddings: 384-dim vectors
├── Metadatas: {
│     "agent_name": str,
│     "action": str,
│     "result": str,
│     "timestamp": str
│   }
└── IDs: Unique identifiers
```

### Data Flow

```
1. Agent performs action
   ↓
2. store(action, params, result, context, agent_name)
   ↓
3. Text → Embedding (via sentence-transformers)
   ↓
4. Stored in ChromaDB with metadata
   ↓
5. Later: search(query)
   ↓
6. Query → Embedding
   ↓
7. Cosine similarity search
   ↓
8. Returns top N relevant documents
```

### Example Storage

```python
# Document
"""
Agent: CompanyAgent
Action: configure_company
Context: Configured Bearings Inc with full company details
Parameters: {"name": "Bearings Inc", "email": "info@bearings.com"}
Result: success
"""

# Metadata
{
    "agent_name": "CompanyAgent",
    "action": "configure_company",
    "result": "success",
    "timestamp": "2026-01-13T22:00:00"
}

# Embedding
[0.023, -0.145, 0.089, ..., 0.234]  # 384 dimensions
```

### API Methods

```python
class RAGMemory:
    def store(action, params, result, context, agent_name, metadata)
    def search(query, n_results=5, agent_name=None)
    def get_recent(agent_name=None, limit=10)
    def get_stats()
```

---

## Per-Agent Memory

### Each Agent Has:

1. **Own Lessons Learned**
   - Filtered by `agent_name`
   - Only sees its own errors/solutions
   - Can share knowledge across projects

2. **Own RAG Context**
   - Filtered by `agent_name`
   - Only searches its own actions
   - Maintains agent-specific history

### Example: ModuleAgent

```python
class ModuleAgent(OdooAgent):
    def __init__(self, connector):
        super().__init__(connector)
        # Inherits:
        # - self.lessons (LessonsLearned)
        # - self.rag (RAGMemory)
    
    def execute(self, params):
        # 1. Check for known errors
        if self.lessons.has_seen_error("ModuleAgent", "IndexError"):
            solutions = self.lessons.get_solutions("ModuleAgent", "IndexError")
            self.log(f"Found {len(solutions)} known solutions")
        
        # 2. Search for relevant context
        context = self.rag.search(
            f"Installing modules {params['modules']}",
            agent_name="ModuleAgent"
        )
        
        # 3. Execute action
        try:
            result = self._install_modules(params)
            
            # 4. Store success in RAG
            self.rag.store(
                action="install_modules",
                params=params,
                result="success",
                context=f"Installed {len(result['installed'])} modules",
                agent_name="ModuleAgent"
            )
            
        except Exception as e:
            # 5. Record error in lessons
            self.lessons.record_error(
                agent_name="ModuleAgent",
                error_type=type(e).__name__,
                error_msg=str(e),
                context=str(params)
            )
```

---

## Storage Locations

```
odoo-ai-configurator/
└── memory/
    ├── lessons.db              # SQLite database
    │   └── lessons_learned     # Single table, all agents
    │
    └── rag/                    # ChromaDB directory
        ├── chroma.sqlite3      # ChromaDB metadata
        └── [uuid]/             # Vector storage
            ├── data_level0.bin
            ├── header.bin
            ├── index_metadata.pickle
            └── length.bin
```

---

## Memory Lifecycle

### 1. Initialization

```python
# When agent is created
agent = ModuleAgent(connector)
# Automatically initializes:
# - lessons = LessonsLearned()  → Opens/creates lessons.db
# - rag = RAGMemory()           → Opens/creates ChromaDB collection
```

### 2. During Execution

```python
# Before action
solutions = agent.get_known_solutions("IndexError")
context = agent.search_context("installing modules")

# After action (success)
agent.store_context(action, params, "success", context)

# After action (error)
agent.record_error(error_type, error_msg, context)
```

### 3. Persistence

- **Lessons Learned**: Persisted immediately to SQLite
- **RAG Memory**: Persisted immediately to ChromaDB
- **Survives**: Process restarts, system reboots
- **Shared**: Across all sessions and projects

---

## Query Examples

### Lessons Learned Queries

```python
# Get all solutions for a specific error
solutions = lessons.get_solutions("ModuleAgent", "IndexError")
# Returns: [{"solution": "Update to Odoo 17", "context": "...", ...}]

# Check if error seen before
has_seen = lessons.has_seen_error("ModuleAgent", "IndexError")
# Returns: True

# Get statistics
stats = lessons.get_stats()
# Returns: {
#   "total_entries": 10,
#   "solutions": 5,
#   "errors": 5,
#   "unique_agents": 3,
#   "unique_error_types": 4
# }
```

### RAG Memory Queries

```python
# Semantic search
results = rag.search("Bearings Inc company configuration")
# Returns: [
#   {
#     "document": "Agent: CompanyAgent\nAction: configure_company...",
#     "metadata": {"agent_name": "CompanyAgent", ...},
#     "distance": 0.234
#   }
# ]

# Get recent actions
recent = rag.get_recent(agent_name="ModuleAgent", limit=5)
# Returns: Last 5 actions by ModuleAgent
```

---

## Performance Characteristics

### Lessons Learned (SQLite)
- **Write**: O(1) - Instant
- **Read**: O(log n) - Indexed queries
- **Storage**: ~1KB per entry
- **Scalability**: Millions of entries

### RAG Memory (ChromaDB)
- **Write**: O(d) - d = embedding dimension (384)
- **Read**: O(n) - Linear scan (optimized with HNSW)
- **Storage**: ~2KB per document
- **Scalability**: Hundreds of thousands of documents

---

## Dependencies

```txt
# Lessons Learned
# No dependencies - uses Python stdlib sqlite3

# RAG Memory
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

---

## Configuration

### Default Paths

```python
# Lessons Learned
lessons_db_path = "memory/lessons.db"

# RAG Memory
rag_persist_dir = "memory/rag/"
```

### Custom Paths

```python
# Custom lessons database
lessons = LessonsLearned(db_path="/custom/path/lessons.db")

# Custom RAG directory
rag = RAGMemory(persist_directory="/custom/path/rag")
```

---

## Best Practices

### 1. Error Recording
```python
# ✅ Good - Specific error type
agent.record_error("IndexError", "tuple index out of range", "Installing stock")

# ❌ Bad - Generic error type
agent.record_error("Error", "Something failed", "Doing stuff")
```

### 2. Solution Recording
```python
# ✅ Good - Actionable solution
agent.record_solution("IndexError", "Update to Odoo 17", "Odoo 16 incompatible")

# ❌ Bad - Vague solution
agent.record_solution("Error", "Fix it", "It was broken")
```

### 3. Context Storage
```python
# ✅ Good - Descriptive context
agent.store_context(
    action="configure_company",
    params={"name": "Bearings Inc"},
    result="success",
    context="Configured Bearings Inc with full company details including email, phone, address"
)

# ❌ Bad - Minimal context
agent.store_context("config", {}, "ok", "did it")
```

---

## Maintenance

### Cleanup Old Entries

```python
# Lessons Learned
# Manual cleanup via SQL
conn = sqlite3.connect("memory/lessons.db")
conn.execute("DELETE FROM lessons_learned WHERE timestamp < ?", (cutoff_date,))

# RAG Memory
# ChromaDB handles cleanup automatically
# Or delete collection and recreate:
client.delete_collection("odoo_context")
```

### Backup

```bash
# Lessons Learned
cp memory/lessons.db memory/lessons.db.backup

# RAG Memory
tar -czf rag_backup.tar.gz memory/rag/
```

---

## Future Enhancements

1. **Cross-Agent Learning**: Share solutions between agents
2. **Confidence Scores**: Rate solution effectiveness
3. **Automatic Cleanup**: Remove outdated entries
4. **Analytics Dashboard**: Visualize learning patterns
5. **Export/Import**: Share knowledge between deployments
