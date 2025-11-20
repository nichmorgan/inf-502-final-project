from nicegui import ui, events

from app.domain.entities.repo import RepoSummaryEntity

__all__ = ["repos_table_component"]


def repo_info_to_raw_table(info_list: list[RepoSummaryEntity]):
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

    rows = [
        {
            **info.model_dump(exclude={"id"}),
            "actions": info.id,
        }
        for info in info_list
    ]

    return columns, rows


@ui.refreshable
def repos_table_component(
    repos: list[RepoSummaryEntity] = [],
    *,
    title: str = "Comparison Table",
    empty_message: str = "No repositories added yet. Add repositories using the form above.",
    on_remove: events.Handler[events.GenericEventArguments] | None = None,
):
    with ui.card().classes("w-full"):
        ui.label(title).classes("text-xl font-semibold mb-4")
        with ui.column().classes("w-full"):
            if not repos:
                ui.label(empty_message).classes("text-gray-500")
                return

            columns, rows = repo_info_to_raw_table(repos)
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
