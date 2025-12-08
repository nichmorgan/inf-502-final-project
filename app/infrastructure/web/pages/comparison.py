from dependency_injector.wiring import inject, Provide
from nicegui import ui, events, run
from typing import Annotated
from fastapi import Depends
from app.containers import Container
from app.domain.entities.repo import RepoSourceEntity
from app.domain.enums import RepoProvider
from app.infrastructure.web.components.repos_graph import repos_graph_component
from app.infrastructure.web.components.repos_table import repos_table_component
from app.infrastructure.web.components.repos_timeseries import (
    repos_timeseries_component,
)
from app.use_cases.get_repo_summary import GetRepoSummaryUseCase
from app.use_cases.get_repo_timeseries import GetRepoTimeseriesUseCase

__all__ = ["comparison_page"]


@ui.page("/")
@inject
async def comparison_page(
    summary_use_case: Annotated[
        GetRepoSummaryUseCase, Depends(Provide[Container.get_repo_summary_use_case])
    ],
    timeseries_use_case: Annotated[
        GetRepoTimeseriesUseCase,
        Depends(Provide[Container.get_repo_timeseries_use_case]),
    ],
) -> None:
    """Create and render the repository comparison page."""

    # Initialize state
    state = {
        "repos_info": {},
        "repos_timeseries": {},
        "is_loading_source": False,
    }

    available_providers = list(RepoProvider)

    async def add_source(event: events.ClickEventArguments) -> None:
        """Add a repository to the comparison table."""
        state["is_loading_source"] = True

        source = RepoSourceEntity(
            provider=provider_select.value or "",
            owner=owner_input.value.strip(),
            repo=repo_input.value.strip(),
        )

        if source.id in state["repos_info"]:
            ui.notify("Repository already added", type="warning")
        else:
            try:
                summary = await run.cpu_bound(summary_use_case.execute, source)
                state["repos_info"][source.id] = summary

                timeseries = await run.cpu_bound(timeseries_use_case.execute, source)
                state["repos_timeseries"][source.id] = timeseries

                await repos_table_component.refresh(state["repos_info"].values())
                await repos_graph_component.refresh(state["repos_info"].values())
                await repos_timeseries_component.refresh(
                    state["repos_timeseries"].values()
                )

                ui.notify(f"Added {source.id}", type="positive")

            except ValueError as e:
                if "Unsupported URL" in str(e):
                    ui.notify(
                        f"Provider '{source.provider}' is not supported",
                        type="negative",
                    )
                else:
                    ui.notify(f"Error: {str(e)}", type="negative")
            except Exception as e:
                ui.notify(f"Error fetching repository data: {str(e)}", type="negative")

        state["is_loading_source"] = False

    async def remove_source(event: events.GenericEventArguments) -> None:
        """Remove a repository from the comparison."""
        repo_id = event.args
        del state["repos_info"][repo_id]
        del state["repos_timeseries"][repo_id]

        await repos_table_component.refresh(state["repos_info"].values())
        await repos_graph_component.refresh(state["repos_info"].values())
        await repos_timeseries_component.refresh(state["repos_timeseries"].values())

    # Page header
    ui.label("Repository Comparison").classes("text-3xl font-bold mb-4")

    # Input form
    with ui.card().classes("w-full mb-6"):
        ui.label("Add Repository").classes("text-xl font-semibold mb-2")

        with ui.row().classes("w-full gap-4"):
            provider_select = (
                ui.select(
                    label="Provider",
                    options=available_providers,
                    value=(available_providers[0] if available_providers else None),
                )
                .classes("flex-1")
                .mark("provider_select")
            )

            owner_input = (
                ui.input(label="Owner", placeholder="e.g., torvalds")
                .classes("flex-1")
                .mark("owner_input")
            )

            repo_input = (
                ui.input(label="Repository", placeholder="e.g., linux")
                .classes("flex-1")
                .mark("repo_input")
            )

            ui.button("Add Repository", on_click=add_source).props(
                "color=primary"
            ).bind_enabled_from(
                state, "is_loading_source", lambda v: not v
            ).bind_visibility_from(
                state, "is_loading_source", lambda v: not v
            ).mark(
                "add_repository_button"
            )

            ui.spinner().classes("ml-2").bind_visibility_from(
                state, "is_loading_source"
            )

    # Tabs for different views
    with ui.tabs().classes("w-full") as tabs:
        summary_tab = ui.tab("Summary")
        timeseries_tab = ui.tab("Timeseries")

    with ui.tab_panels(tabs, value=summary_tab).classes("w-full"):
        # Summary Tab
        with ui.tab_panel(summary_tab):
            repos_graph_component(state["repos_info"].values())
            repos_table_component(on_remove=remove_source)

        # Timeseries Tab
        with ui.tab_panel(timeseries_tab):
            repos_timeseries_component(state["repos_timeseries"].values())
