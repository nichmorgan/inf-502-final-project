# GitHub Repository Analyzer

A Python application for analyzing GitHub repositories. Retrieves pull request and contributor statistics via the GitHub API.

## Setup

1. Install [uv](https://github.com/astral-sh/uv) if you haven't already

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file in the project root (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Add your GitHub Personal Access Token to `.env`:
   - Get a token at https://github.com/settings/tokens
   - Required permissions: `public_repo` (or `repo` for private repos)
   - This is **required** to avoid GitHub API rate limits

## Usage

The project includes a Makefile with common commands:

- `make web` - Start the web application
- `make test` - Run tests with coverage
- `make fmt` - Format code with Black

### Running directly

```bash
# Start web app
uv run python -m app.infrastructure.web.main

# Run tests
uv run pytest --cov

# Format code
uv run black app tests
```

## Data Retrieved

The application fetches the following metrics from GitHub repositories:

- **Pull Request Statistics**:
  - Open PR count
  - Closed PR count
  - Time-series data (historical PR trends)
  - Oldest PR date

- **Contributor Statistics**:
  - Total contributor count
  - Time-series data (contributor growth over time)

**Note**: Initial data fetching can take several minutes as the application extracts **1 year of historical data** from GitHub. Subsequent requests are served from cache (see Caching section below).

## Caching

To reduce GitHub API calls and improve performance, the application uses a **pickle file cache** with TTL (Time-To-Live):

- **Cache Location**: `.storage/repo_info.pickle` (configurable via `STORAGE_FOLDER` in `.env`)
- **TTL**: 24 hours (86400 seconds) by default (configurable via `CACHE_TTL_SECONDS` in `.env`)
- **Behavior**: Repository data is cached and reused within the TTL window. After expiration, fresh data is fetched from GitHub.

This significantly reduces API rate limit consumption for frequently accessed repositories.

## Architecture

Built with Clean Architecture principles.

## Presentation

This project was created for INF-502 Final Project. The presentation slides are available in the [`docs/`](docs/) directory. See [docs/README.md](docs/README.md) for the full table of contents.
