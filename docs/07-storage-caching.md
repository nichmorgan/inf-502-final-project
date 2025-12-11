[← Previous: Rate Limits](06-rate-limits.md) | [Next: Data Processing →](08-data-processing.md)

---

# Data Storage & Caching Strategy

## Pickle File Storage with TTL

```
.storage/
└── repo_info.pickle
    ├── Repository data
    ├── Timestamp (created_at)
    └── TTL: 24 hours (default)
```

## How It Works

```mermaid
sequenceDiagram
    participant UI as Web Interface
    participant UC as Use Case
    participant Cache as Pickle Storage
    participant API as GitHub API

    UI->>UC: Request repo data
    UC->>Cache: Check cache
    alt Cache hit & fresh
        Cache-->>UC: Return cached data
        UC-->>UI: Display data ⚡
    else Cache miss or expired
        UC->>API: Fetch from GitHub
        API-->>UC: Raw data
        UC->>Cache: Store with TTL
        Cache-->>UC: Confirm
        UC-->>UI: Display data 🐌
    end
```

## Configuration

```bash
# .env
STORAGE_FOLDER=.storage/
CACHE_TTL_SECONDS=86400  # 24 hours
```

## Benefits
✅ **Performance**: Subsequent requests = instant  
✅ **API Efficiency**: 83x fewer requests after initial fetch  
✅ **User Experience**: No waiting for cached data  
✅ **Configurable**: Adjust TTL based on needs  

---

[↑ Back to Top](#data-storage--caching-strategy)