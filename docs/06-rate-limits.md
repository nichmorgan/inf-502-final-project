[← Previous: Data Collection](05-data-collection.md) | [Next: Storage & Caching →](07-storage-caching.md)

---

# GitHub API Rate Limits Challenge

## The Problem: 429 Too Many Requests ❌

Initial implementation without authentication:
- Hit rate limit during time-series data collection
- Multiple pagination requests required
- Application became unusable

## Rate Limit Comparison

| Request Type | Unauthenticated | Authenticated (Token) | Improvement |
|--------------|-----------------|----------------------|-------------|
| **REST API** | 60/hour         | 5,000/hour          | **83x** 🚀  |
| **Per-minute** | ~1/min        | ~83/min             | - |

*Source: [GitHub REST API Rate Limits Documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)*

## The Solution: Personal Access Token ✅

```bash
# .env configuration
GITHUB_TOKEN=ghp_your_token_here
```

**Result**: Smooth data collection even with extensive time-series pagination

## Additional Optimizations

### Data Sampling Strategy
- **Time-series sampling**: Fetch data at intervals rather than every single point
- **Aggregation**: Group data by week/month to reduce granularity
- **Smart pagination**: Only fetch necessary pages, avoid over-fetching

### Caching & Storage
- **Caching strategy** reduces redundant API calls
- **TTL-based invalidation** keeps data fresh
- **Batch processing** minimizes request count

---

[↑ Back to Top](#github-api-rate-limits-challenge)
