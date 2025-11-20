from dependency_injector.wiring import inject, Provide
from nicegui import ui
from typing import Annotated
from fastapi import Depends
from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.containers import Container
from app.use_cases.get_repo_summary import GetRepoSummaryUseCase

__all__ = ["comparison_page"]


@ui.page("/")
@inject
def comparison_page(
    use_case: Annotated[
        GetRepoSummaryUseCase, Depends(Provide[Container.get_repo_summary_use_case])
    ],
    gateway_selector: Annotated[
        RepoGatewaySelector, Depends(Provide[Container.repo_gateway_selector])
    ],
) -> None:
    """Create and render the repository comparison page."""

    # State
    repos: list[dict] = []

    def render_table() -> None:
        """Render the comparison table."""
        table_container.clear()

        with table_container:
            if not repos:
                ui.label(
                    "No repositories added yet. Add repositories using the form above."
                ).classes("text-gray-500")
                return

            # Create table columns
            columns = [
                {
                    "name": "provider",
                    "label": "Provider",
                    "field": "provider",
                    "align": "left",
                },
                {"name": "owner", "label": "Owner", "field": "owner", "align": "left"},
                {
                    "name": "repo",
                    "label": "Repository",
                    "field": "repo",
                    "align": "left",
                },
                {
                    "name": "open_prs",
                    "label": "Open PRs",
                    "field": "open_prs",
                    "align": "center",
                },
                {
                    "name": "closed_prs",
                    "label": "Closed PRs",
                    "field": "closed_prs",
                    "align": "center",
                },
                {
                    "name": "oldest_pr",
                    "label": "Oldest PR Date",
                    "field": "oldest_pr",
                    "align": "center",
                },
                {
                    "name": "users",
                    "label": "Contributors",
                    "field": "users",
                    "align": "center",
                },
                {
                    "name": "actions",
                    "label": "Actions",
                    "field": "actions",
                    "align": "center",
                },
            ]

            # Create table rows
            rows = [
                {
                    "provider": repo["provider"],
                    "owner": repo["owner"],
                    "repo": repo["repo"],
                    "open_prs": repo["open_prs"],
                    "closed_prs": repo["closed_prs"],
                    "oldest_pr": repo["oldest_pr"],
                    "users": repo["users"],
                    "actions": repo["id"],
                }
                for repo in repos
            ]

            # Create table
            table = ui.table(columns=columns, rows=rows, row_key="actions").classes(
                "w-full"
            )

            # Add action button slot
            table.add_slot(
                "body-cell-actions",
                r"""
                <q-td :props="props">
                    <q-btn
                        flat
                        dense
                        round
                        icon="delete"
                        color="negative"
                        @click="$parent.$emit('remove', props.row.actions)"
                    />
                </q-td>
                """,
            )

            # Handle remove events
            table.on("remove", lambda e: remove_repo(e.args))

    def add_repo(provider: str, owner: str, repo: str) -> None:
        """Add a repository to the comparison table."""
        nonlocal repos

        if not provider or not owner or not repo:
            ui.notify("Please fill in all fields", type="warning")
            return

        # Check if repo already exists
        repo_id = f"{provider}/{owner}/{repo}"
        if any(r["id"] == repo_id for r in repos):
            ui.notify("Repository already added", type="warning")
            return

        try:
            # Fetch repo summary
            summary = use_case.execute(provider, owner, repo)

            # Add to list
            repos.append(
                {
                    "id": repo_id,
                    "provider": provider.upper(),
                    "owner": owner,
                    "repo": repo,
                    "open_prs": summary.pull_requests.open_count,
                    "closed_prs": summary.pull_requests.closed_count,
                    "oldest_pr": (
                        summary.pull_requests.oldest_date.strftime("%Y-%m-%d")
                        if summary.pull_requests.oldest_date
                        else "N/A"
                    ),
                    "users": summary.users.count,
                }
            )

            # Update table
            render_table()
            ui.notify(f"Added {repo_id}", type="positive")

        except ValueError as e:
            if "Unsupported URL" in str(e):
                ui.notify(f"Provider '{provider}' is not supported", type="negative")
            else:
                ui.notify(f"Error: {str(e)}", type="negative")
        except Exception as e:
            ui.notify(f"Error fetching repository data: {str(e)}", type="negative")

    def remove_repo(repo_id: str) -> None:
        """Remove a repository from the comparison."""
        nonlocal repos

        repos = [r for r in repos if r["id"] != repo_id]
        render_table()
        ui.notify(f"Removed {repo_id}", type="info")

    # Render UI
    ui.label("Repository Comparison").classes("text-3xl font-bold mb-4")

    # Input form
    with ui.card().classes("w-full mb-6"):
        ui.label("Add Repository").classes("text-xl font-semibold mb-2")

        with ui.row().classes("w-full gap-4"):
            provider_select = ui.select(
                label="Provider",
                options=gateway_selector.providers,
                value=(
                    gateway_selector.providers[0]
                    if gateway_selector.providers
                    else None
                ),
            ).classes("flex-1")

            owner_input = ui.input(label="Owner", placeholder="e.g., torvalds").classes(
                "flex-1"
            )
            repo_input = ui.input(
                label="Repository", placeholder="e.g., linux"
            ).classes("flex-1")

            ui.button(
                "Add Repository",
                on_click=lambda: add_repo(
                    provider_select.value or "",
                    owner_input.value.strip(),
                    repo_input.value.strip(),
                ),
            ).props("color=primary")

    # Comparison table
    with ui.card().classes("w-full"):
        ui.label("Comparison Table").classes("text-xl font-semibold mb-4")
        # Create table container (empty but existing)
        table_container = ui.column().classes("w-full")
        with table_container:
            ui.label(
                "No repositories added yet. Add repositories using the form above."
            ).classes("text-gray-500")
