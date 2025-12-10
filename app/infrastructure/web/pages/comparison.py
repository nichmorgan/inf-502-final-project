import asyncio
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from nicegui import app, events, run, ui

from app.containers import Container
from app.domain.dto import RepoSourceEntity
from app.domain.entities import RepoInfoEntity
from app.domain.enums import RepoProvider
from app.infrastructure.web.components import (
    repos_graph_component,
    repos_table_component,
    repos_timeseries_component,
)
from app.use_cases import GetRepoInfoBySourceUseCase


@ui.page("/")
@inject
async def comparison_page(
    get_repo_info_by_source: Annotated[
        GetRepoInfoBySourceUseCase,
        Depends(Provide[Container.get_repo_info_by_source_use_case]),
    ],
) -> None:
    """Create and render the repository comparison page."""

    await ui.context.client.connected()

    # Initialize state
    cache = app.storage.tab
    cache.setdefault("repos", {})
    cache.setdefault("is_loading", False)

    repo_ids = list(cache["repos"].keys())

    available_providers = list(RepoProvider)

    def get_new_repo_info(source: RepoSourceEntity) -> RepoInfoEntity | None:
        if source.full_name in cache["repos"].values():
            ui.notify("Repository is already included")
            return

        info = asyncio.run(get_repo_info_by_source.execute(source))
        if not info.id:
            ui.notify("Id was expected after get new repo info", type="negative")
            return

        return info

    async def add_source(event: events.ClickEventArguments) -> None:
        nonlocal repo_ids

        cache["is_loading"] = True

        source = RepoSourceEntity(
            provider=provider_select.value or "",
            owner=owner_input.value.strip(),
            repo=repo_input.value.strip(),
        )

        if new_info := await run.io_bound(get_new_repo_info, source):
            cache["repos"][new_info.id] = new_info.full_name
            repo_ids = list(cache["repos"].keys())
            await repos_table_component.refresh(repo_ids)
            await repos_graph_component.refresh(repo_ids)
            await repos_timeseries_component.refresh(repo_ids)

        cache["is_loading"] = False

    async def remove_source(event: events.GenericEventArguments) -> None:
        nonlocal repo_ids

        id_to_delete = event.args
        if id_to_delete not in cache["repos"]:
            return

        del cache["repos"][id_to_delete]

        repo_ids = list(cache["repos"].keys())
        await repos_table_component.refresh(repo_ids)
        await repos_graph_component.refresh(repo_ids)
        await repos_timeseries_component.refresh(repo_ids)

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
                cache, "is_loading", lambda v: not v
            ).bind_visibility_from(
                cache, "is_loading", lambda v: not v
            ).mark(
                "add_repository_button"
            )

            ui.spinner().classes("ml-2").bind_visibility_from(cache, "is_loading")

    # Tabs for different views
    with ui.tabs().classes("w-full") as tabs:
        summary_tab = ui.tab("Summary")
        timeseries_tab = ui.tab("Timeseries")

    with ui.tab_panels(tabs, value=summary_tab).classes("w-full"):
        # Summary Tab
        with ui.tab_panel(summary_tab):
            await repos_graph_component(repo_ids)  # type: ignore

        # Timeseries Tab
        with ui.tab_panel(timeseries_tab):
            await repos_timeseries_component(repo_ids)  # type: ignore

    with ui.column().classes("w-full mt-6"):
        await repos_table_component(repo_ids, on_remove=remove_source)  # type: ignore
