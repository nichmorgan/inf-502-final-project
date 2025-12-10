from dependency_injector.wiring import Provide, inject
from nicegui import run, ui

from app.containers import Container
from app.use_cases import GetRepoInfoByIdUseCase


@ui.refreshable
@inject
async def repos_graph_component(
    repo_info_ids: list[int],
    *,
    get_repo_info_by_id: GetRepoInfoByIdUseCase = Provide[
        Container.get_repo_info_by_id_use_case
    ],
):

    if not repo_info_ids:
        ui.label(
            "No repositories added yet. Add repositories using the form above."
        ).classes("text-gray-500 text-center w-full")
        return

    info_list = await run.cpu_bound(get_repo_info_by_id.execute_sync, repo_info_ids)

    config_map = {
        "open_prs_count": {
            "icon": "mdi:source-pull",
            "color": "blue",
            "title": "Open PRs",
        },
        "closed_prs_count": {
            "icon": "mdi:source-merge",
            "color": "green",
            "title": "Closed PRs",
        },
        "days_since_oldest_pr": {
            "icon": "mdi:calendar-clock",
            "color": "orange",
            "title": "Days Since Oldest PR",
        },
        "users_count": {
            "icon": "mdi:account-multiple",
            "color": "purple",
            "title": "Users",
        },
    }

    return ui.highchart(
        {
            "title": False,
            "chart": {"type": "bar"},
            "xAxis": {
                "categories": [info.full_name for info in info_list],
            },
            "series": [
                {
                    "name": config["title"],
                    "data": [getattr(info, key) or 0 for info in info_list],
                    "color": config["color"],
                }
                for key, config in config_map.items()
            ],
        }
    ).classes("w-full h-96 mt-4")
