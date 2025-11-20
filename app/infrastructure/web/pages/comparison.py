from dependency_injector.wiring import inject, Provide
from nicegui import ui, events
from typing import Annotated
from fastapi import Depends
from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.containers import Container
from app.domain.entities.repo import RepoSourceEntity, RepoSummaryEntity
from app.infrastructure.web.components.repos_table import repos_table_component
from app.use_cases.get_repo_summary import GetRepoSummaryUseCase

__all__ = ["comparison_page"]


@ui.page("/")
@inject
async def comparison_page(
    use_case: Annotated[
        GetRepoSummaryUseCase, Depends(Provide[Container.get_repo_summary_use_case])
    ],
    gateway_selector: Annotated[
        RepoGatewaySelector, Depends(Provide[Container.repo_gateway_selector])
    ],
) -> None:
    """Create and render the repository comparison page."""

    async def add_source(event: events.ClickEventArguments) -> None:
        """Add a repository to the comparison table."""
        nonlocal repos_info

        source = RepoSourceEntity(
            provider=provider_select.value or "",
            owner=owner_input.value.strip(),
            repo=repo_input.value.strip(),
        )

        if source.id in repos_info:
            ui.notify("Repository already added", type="warning")
            return

        try:
            # Fetch repo summary
            summary = use_case.execute(source)

            # Add to list
            repos_info[source.id] = summary
            await repos_table_component.refresh(repos_info.values())

            ui.notify(f"Added {source.id}", type="positive")

        except ValueError as e:
            if "Unsupported URL" in str(e):
                ui.notify(
                    f"Provider '{source.provider}' is not supported", type="negative"
                )
            else:
                ui.notify(f"Error: {str(e)}", type="negative")
        except Exception as e:
            ui.notify(f"Error fetching repository data: {str(e)}", type="negative")

    async def remove_source(event: events.GenericEventArguments) -> None:
        """Remove a repository from the comparison."""
        nonlocal repos_info

        repo_id = event.args

        del repos_info[repo_id]
        await repos_table_component.refresh(repos_info.values())

    # State
    repos_info: dict[str, RepoSummaryEntity] = {}

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

            ui.button("Add Repository", on_click=add_source).props("color=primary")

    repos_table_component(on_remove=remove_source)
