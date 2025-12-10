from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from nicegui import events, run, ui

from app.containers import Container
from app.domain import entities
from app.use_cases.get_repo_info_by_id import GetRepoInfoByIdUseCase


def repo_info_to_raw_table_component(info_list: list[entities.RepoInfoEntity]):
    columns = [
        {
            "name": "provider",
            "label": "Provider",
            "field": "provider",
            "align": "left",
        },
        {
            "name": "owner",
            "label": "Owner",
            "field": "owner",
            "align": "left",
        },
        {
            "name": "repo",
            "label": "Repository",
            "field": "repo",
            "align": "left",
        },
        {
            "name": "open_prs",
            "label": "Open PRs",
            "field": "open_prs_count",
            "align": "center",
        },
        {
            "name": "closed_prs",
            "label": "Closed PRs",
            "field": "closed_prs_count",
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
            "field": "users_count",
            "align": "center",
        },
        {
            "name": "actions",
            "label": "Actions",
            "field": "actions",
            "align": "center",
        },
    ]

    include_fields = {
        "provider",
        "owner",
        "repo",
        "open_prs_count",
        "closed_prs_count",
    }

    rows = [
        {
            **info.model_dump(include=include_fields),
            "oldest_pr": (
                f"{info.days_since_oldest_pr } days"
                if info.days_since_oldest_pr is not None
                else "N/A"
            ),
            "actions": info.id,
        }
        for info in info_list
    ]

    return columns, rows


@ui.refreshable
@inject
async def repos_table_component(
    source_ids: list[int],
    *,
    get_repo_info_by_id: Annotated[
        GetRepoInfoByIdUseCase, Depends(Provide[Container.get_repo_info_by_id_use_case])
    ],
    title: str = "Comparison Table",
    empty_message: str = "No repositories added yet. Add repositories using the form above.",
    on_remove: events.Handler[events.GenericEventArguments] | None = None,
):
    repos = (
        await run.cpu_bound(get_repo_info_by_id.execute_sync, source_ids)
        if source_ids
        else []
    )

    with ui.card().classes("w-full"):
        ui.label(title).classes("text-xl font-semibold mb-4")
        with ui.column().classes("w-full"):
            if not repos:
                ui.label(empty_message).classes("text-gray-500")
                return

            columns, rows = repo_info_to_raw_table_component(repos)
            table = (
                ui.table(columns=columns, rows=rows, row_key="actions")
                .classes("w-full")
                .on("remove", on_remove)
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
