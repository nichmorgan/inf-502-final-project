from datetime import datetime, timedelta
import logging
from github import Github
from app.use_cases.ports.repo_port import RepoPort

__all__ = ["GithubGateway"]

logger = logging.getLogger(__name__)


class GithubGateway(RepoPort):
    def __init__(self, *, client: Github, owner: str, repo: str) -> None:
        super().__init__(owner=owner, repo=repo)
        self.__repo = client.get_repo(f"{owner}/{repo}", lazy=False)
        self.__oldest_pr_cache = None  # Cache for oldest PR date

    def get_open_pull_requests_count(self) -> int:
        return self.__repo.get_pulls(state="open").totalCount

    def get_closed_pull_requests_count(self) -> int:
        return self.__repo.get_pulls(state="closed").totalCount

    def get_users_count(self) -> int:
        return self.__repo.get_contributors().totalCount

    def get_oldest_pull_request_date(self) -> datetime | None:
        if self.__oldest_pr_cache is not None:
            return self.__oldest_pr_cache

        response = self.__repo.get_pulls(sort="created", direction="asc")
        if pr_list := response.get_page(0):
            self.__oldest_pr_cache = pr_list[0].created_at
            return self.__oldest_pr_cache
        return None

    def get_timeseries_open_pull_requests(self) -> dict[datetime, int]:
        """Get timeseries of open PRs by sampling creation dates."""
        logger.info(f"[{self._owner}/{self._repo}] Starting open PRs timeseries")
        timeseries = {}
        MAX_PRS = 100  # Limit to most recent 100 PRs for faster loading

        # Get date range - limit to last year for performance
        end_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
        start_date = end_date - timedelta(days=365)

        logger.info(f"[{self._owner}/{self._repo}] Getting oldest PR date...")
        oldest_pr = self.get_oldest_pull_request_date()
        if oldest_pr:
            # Remove timezone info for comparison
            oldest_pr = oldest_pr.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            start_date = max(start_date, oldest_pr)
        logger.info(
            f"[{self._owner}/{self._repo}] Date range: {start_date} to {end_date}"
        )

        # Fetch limited number of PRs
        logger.info(f"[{self._owner}/{self._repo}] Fetching up to {MAX_PRS} PRs...")
        all_prs = self.__repo.get_pulls(state="all", sort="created", direction="desc")
        pr_list = list(all_prs[:MAX_PRS])
        logger.info(f"[{self._owner}/{self._repo}] Fetched {len(pr_list)} PRs")

        if not pr_list:
            logger.info(f"[{self._owner}/{self._repo}] No PRs found")
            return timeseries

        # Reverse to chronological order
        pr_list.reverse()

        # Build timeseries
        logger.info(f"[{self._owner}/{self._repo}] Building timeseries...")
        current_date = start_date
        pr_index = 0
        open_count = 0

        while current_date <= end_date:
            # Add PRs created on or before current_date
            while pr_index < len(pr_list):
                pr_created = pr_list[pr_index].created_at.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=None
                )
                if pr_created <= current_date:
                    open_count += 1
                    pr_index += 1
                else:
                    break

            # Subtract PRs closed before current_date
            closed_on_date = sum(
                1
                for pr in pr_list[:pr_index]
                if pr.closed_at
                and pr.closed_at.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=None
                )
                <= current_date
            )

            timeseries[current_date] = max(0, open_count - closed_on_date)
            current_date += timedelta(days=7)  # Weekly sampling

        logger.info(
            f"[{self._owner}/{self._repo}] Open PRs timeseries completed with {len(timeseries)} data points"
        )
        return timeseries

    def get_timeseries_closed_pull_requests(self) -> dict[datetime, int]:
        """Get timeseries of closed PRs by counting closures over time."""
        logger.info(f"[{self._owner}/{self._repo}] Starting closed PRs timeseries")
        timeseries = {}
        MAX_PRS = 100  # Limit to most recent 100 closed PRs for faster loading

        # Get date range - limit to last year for performance
        end_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
        start_date = end_date - timedelta(days=365)

        logger.info(f"[{self._owner}/{self._repo}] Getting oldest PR date...")
        oldest_pr = self.get_oldest_pull_request_date()
        if oldest_pr:
            # Remove timezone info for comparison
            oldest_pr = oldest_pr.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            start_date = max(start_date, oldest_pr)
        logger.info(
            f"[{self._owner}/{self._repo}] Date range: {start_date} to {end_date}"
        )

        # Fetch limited number of closed PRs
        logger.info(
            f"[{self._owner}/{self._repo}] Fetching up to {MAX_PRS} closed PRs..."
        )
        closed_prs = self.__repo.get_pulls(
            state="closed", sort="updated", direction="desc"
        )
        pr_list = [pr for pr in list(closed_prs[:MAX_PRS]) if pr.closed_at]
        logger.info(f"[{self._owner}/{self._repo}] Fetched {len(pr_list)} closed PRs")

        if not pr_list:
            logger.info(f"[{self._owner}/{self._repo}] No closed PRs found")
            return timeseries

        # Sort by closed date
        pr_list.sort(key=lambda pr: pr.closed_at)

        # Build timeseries
        logger.info(f"[{self._owner}/{self._repo}] Building timeseries...")
        current_date = start_date
        pr_index = 0
        cumulative_count = 0

        while current_date <= end_date:
            # Count PRs closed on or before current_date
            while pr_index < len(pr_list):
                pr_closed = pr_list[pr_index].closed_at.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=None
                )
                if pr_closed <= current_date:
                    cumulative_count += 1
                    pr_index += 1
                else:
                    break

            timeseries[current_date] = cumulative_count
            current_date += timedelta(days=7)  # Weekly sampling

        logger.info(
            f"[{self._owner}/{self._repo}] Closed PRs timeseries completed with {len(timeseries)} data points"
        )
        return timeseries

    def get_timeseries_users(self) -> dict[datetime, int]:
        """Get timeseries of contributors by tracking first contribution dates."""
        logger.info(f"[{self._owner}/{self._repo}] Starting contributors timeseries")
        timeseries = {}
        MAX_COMMITS = 200  # Limit to most recent 200 commits for faster loading

        # Get date range - limit to last year for performance
        end_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
        start_date = end_date - timedelta(days=365)

        logger.info(f"[{self._owner}/{self._repo}] Getting oldest PR date...")
        oldest_pr = self.get_oldest_pull_request_date()
        if oldest_pr:
            # Remove timezone info for comparison
            oldest_pr = oldest_pr.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            start_date = max(start_date, oldest_pr)
        logger.info(
            f"[{self._owner}/{self._repo}] Date range: {start_date} to {end_date}"
        )

        # Get contributors from recent commits only
        logger.info(
            f"[{self._owner}/{self._repo}] Fetching up to {MAX_COMMITS} commits..."
        )
        contributors = {}
        commit_count = 0

        for commit in self.__repo.get_commits():
            if commit_count >= MAX_COMMITS:
                break

            if commit.author and commit.author.login:
                user = commit.author.login
                commit_date = commit.commit.author.date.replace(
                    hour=0, minute=0, second=0, microsecond=0, tzinfo=None
                )

                # Only track contributions within our date range
                if commit_date >= start_date:
                    if user not in contributors or commit_date < contributors[user]:
                        contributors[user] = commit_date

            commit_count += 1

        logger.info(
            f"[{self._owner}/{self._repo}] Processed {commit_count} commits, found {len(contributors)} unique contributors"
        )

        if not contributors:
            logger.info(f"[{self._owner}/{self._repo}] No contributors found")
            return timeseries

        # Build timeseries
        logger.info(f"[{self._owner}/{self._repo}] Building timeseries...")
        contributor_list = sorted(contributors.items(), key=lambda x: x[1])
        current_date = start_date
        user_index = 0
        cumulative_count = 0

        while current_date <= end_date:
            while (
                user_index < len(contributor_list)
                and contributor_list[user_index][1] <= current_date
            ):
                cumulative_count += 1
                user_index += 1

            timeseries[current_date] = cumulative_count
            current_date += timedelta(days=7)  # Weekly sampling

        logger.info(
            f"[{self._owner}/{self._repo}] Contributors timeseries completed with {len(timeseries)} data points"
        )
        return timeseries
