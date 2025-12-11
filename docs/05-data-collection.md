[← Previous: Architecture](04-architecture.md) | [Next: Rate Limits →](06-rate-limits.md)

---

# Data Collection

## PyGithub Library
- Official Python SDK for GitHub REST API
- Type-safe, Pythonic interface
- Handles pagination automatically

## Data Collected
| Metric | Description |
|--------|-------------|
| **Pull Requests (Current)** | Current open/closed counts |
| **Pull Requests (Historical)** | Time-series over 1 year (sampled) |
| **Contributors (Current)** | Total unique contributors |
| **Contributors (Historical)** | Growth time-series over 1 year (sampled) |
| **Oldest PR Date** | Date of first pull request |
| **Repository Info** | Owner, name, metadata |

## Time-Series Constraints

### Date Range
- **Window**: 1 year from current date
- **Sampling**: Weekly intervals (7 days)

### Sampling Limits (Performance Optimization)
| Metric | Data Fetched |
|--------|--------------|
| **Open PRs** | All PRs within 1-year window |
| **Closed PRs** | 100 most recent closed PRs |
| **Contributors** | 200 most recent commits |

**Rationale**: Balance between meaningful trends and API efficiency

**Example**: For large projects (20,000+ PRs), closed PR trend is based on sample of 100 most recent closures

---

## Gateway Pattern Implementation

Complete RepoPort interface defines all required methods:

```python
class RepoPort(ABC):
    @abstractmethod
    async def get_open_pull_requests_count(
        self, *, owner: str, repo: str
    ) -> int:
        """Fetch current open PR count"""
        pass

    @abstractmethod
    async def get_closed_pull_requests_count(
        self, *, owner: str, repo: str
    ) -> int:
        """Fetch current closed PR count"""
        pass

    @abstractmethod
    async def get_users_count(self, *, owner: str, repo: str) -> int:
        """Fetch total contributors"""
        pass

    @abstractmethod
    async def get_oldest_pull_request_date(
        self, *, owner: str, repo: str
    ) -> datetime | None:
        """Fetch oldest PR date"""
        pass

    @abstractmethod
    async def get_timeseries_open_pull_requests(
        self, *, owner: str, repo: str
    ) -> dict[datetime, int]:
        """Returns 1-year history of open PRs"""
        pass

    # ... + closed PRs and users time-series methods
```

**Location**: `app/domain/ports/repo_port.py`

**Abstraction enables** easy addition of GitLab, Bitbucket, etc.

---

[↑ Back to Top](#data-collection)