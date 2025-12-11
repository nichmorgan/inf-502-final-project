[← Previous: Storage & Caching](07-storage-caching.md) | [Next: Analysis →](09-analysis.md)

---

# Data Processing Challenges

## Challenge 1: Data Transformation 🔄

### The Problem
- **API returns**: Dictionary of dates → counts `{date: count, ...}`
- **Charts need**: List of data points with interpolated values
- **Missing dates**: Need to be filled for smooth visualization

### The Solution: `fill_timeseries` Function

```python
def fill_timeseries(ts_dict: dict) -> list[entities.TimeseriesDataPoint]:
    """Transform dictionary into time-series data points"""
    if not ts_dict:
        return []

    # Sort dates chronologically
    sorted_dates = sorted(ts_dict.keys())
    result = []
    last_value = 0

    # Fill in data points, keeping last value for missing dates
    for date in sorted_dates:
        value = ts_dict.get(date, last_value)
        result.append(entities.TimeseriesDataPoint(date=date, value=value))
        last_value = value

    return result
```

**Location**: `app/use_cases/get_repo_info_by_source.py`

This transformation ensures smooth, continuous time-series visualization

---

## Challenge 2: UI Freezing ❄️

### The Problem
- Fetching data from GitHub API takes time (30-60 seconds)
- Multiple API operations: PRs, contributors, time-series
- Heavy computation blocks UI thread
- Poor user experience: frozen interface, no feedback

### The Solution: NiceGUI Background Processing

NiceGUI provides `run.cpu_bound` and `run.io_bound` for background tasks:

```python
from nicegui import run

# In web component
async def fetch_repository_data():
    # Run I/O-bound operation (API call) in background thread
    new_info = await run.io_bound(
        get_repo_info_use_case.execute_sync,
        source
    )

    # UI stays responsive during fetch
    ui.notify("Repository added successfully!")
    return new_info
```

**Location**: `app/infrastructure/web/pages/comparison.py`

**Result**: UI remains responsive, loading indicators work, user can interact with page

---

## Cache Reduces API Rate Limit Pressure

```python
async def execute(self, source: dto.RepoSourceEntity) -> entities.RepoInfoEntity:
    # Check cache first (fast!)
    if db_item := await self.__get_from_db(source):
        return db_item  # No API call needed

    # Only call API if cache miss or expired
    gateway_item = await self.__get_from_gateway(source)
    # ... store in cache
```

**Benefits**:
- ✅ First fetch: Slow but responsive UI
- ✅ Subsequent fetches: Instant (from cache)
- ✅ API rate limit: 83x fewer requests

---

[↑ Back to Top](#data-processing-challenges)
