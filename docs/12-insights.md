[← Previous: Time Series](11-viz-timeseries.md) | [Next: Testing →](13-testing.md)

---

# Repository Comparison Insights

## Selected Repositories: Python Web Frameworks

Comparing three popular Python web frameworks:
- **Flask** (pallets/flask) - Lightweight micro-framework
- **Django** (django/django) - Full-featured web framework
- **FastAPI** (fastapi/fastapi) - Modern async framework

---

## Summary Metrics Comparison

![Summary Comparison Graph](../.assets/summary-comparison-graph.png)

![Summary Comparison Table](../.assets/summary-comparison-table.png)

| Framework | Open PRs | Closed PRs | Contributors | First PR | Founded |
|-----------|----------|------------|--------------|----------|---------|
| **Flask**  | 8        | 2,724      | 12           | 352 days | 2010 (15 yrs) |
| **Django** | 362      | 19,961     | 54           | 2,408 days | 2005 (20 yrs) |
| **FastAPI**| 154      | 4,801      | 12           | 1,909 days | 2018 (7 yrs) |

*"First PR" reflects GitHub workflow adoption or repo migration dates*

---

## Key Insights

### 🏆 Flask: Exemplary Maintenance
- **Only 8 open PRs** - Outstanding PR management
- **Open PRs remain flat** (~8 consistently) over time
- **2,724 closed PRs** - Highly active despite 15-year maturity
- **Insight**: Mature project with excellent maintenance practices - maintainers keep perfect pace with contributions

### 📈 Django: Large-Scale Enterprise Framework
- **362 open PRs** vs **19,961 closed** - Massive scale
- **Open PRs trending up** (280 → 360) - Stressed maintenance pattern
- **54 contributors** with steady growth - Largest, most active community
- **6.6 years of PR data** available for analysis
- **Insight**: Contributions outpacing review capacity (typical at enterprise scale), but still impressive for a 20-year-old project

### ⚡ FastAPI: Rapidly Improving
- **154 open PRs** declining to ~170 - Healthy improvement trend
- **Open PRs decreasing** over time (was 280, now 170)
- **Recent activity burst** - Spike in closed PRs and new contributors
- **5.2 years of PR history** (since org migration from tiangolo/fastapi)
- **Insight**: Youngest framework showing rapid maturation and strengthening maintenance practices

---

## Temporal Trends Analysis

![Open PRs Over Time](../.assets/timeseries-openedprs-graph.png)

![Closed PRs Over Time](../.assets/timeseries-closedprs-graph.png)

![Contributors Over Time](../.assets/timeseries-contributors-graph.png)

### PR Management Patterns
- **Flask**: Flat open PRs, consistent closure = **Healthiest maintenance**
- **Django**: Rising open PRs = Stressed (understandable at massive scale)
- **FastAPI**: Declining open PRs = **Actively improving maintenance**

### Community Growth
- **Django**: Steady growth, largest community (54 contributors)
- **FastAPI**: Recent surge (growing contributor base)
- **Flask**: Stable, focused team (12 contributors)

### Maintenance vs Project Age
- **Flask (15 yrs)**: Proves age doesn't degrade maintenance quality
- **Django (20 yrs)**: Scale creates challenges even for mature projects
- **FastAPI (7 yrs)**: Youth + modern practices = improving trajectory

---

## Important Learning: Understanding Context

**Critical Insight**: Always understand how a project manages issues before drawing conclusions

### Why Context Matters
- Some projects use **external issue trackers** (not GitHub Issues)
- GitHub metrics may not tell the full story
- Different workflows create different patterns
- Project age and size affect interpretation

### Example: External Issue Tracking
Projects using external platforms (Jira, custom systems) may show:
- Oscillating open PRs without corresponding closes
- Issues marked as invalid or deleted
- Unusual patterns that don't reflect actual project health

**Lesson**: Investigate project workflows before analyzing metrics

---

[↑ Back to Top](#repository-comparison-insights)
