from nicegui import ui
from app.domain.entities.repo import RepoSummaryEntity


@ui.refreshable
def repos_graph_component(info_list: list[RepoSummaryEntity]) -> None:
    config_map = {
        "open_prs": {"icon": "mdi:source-pull", "color": "blue", "title": "Open PRs"},
        "closed_prs": {
            "icon": "mdi:source-merge",
            "color": "green",
            "title": "Closed PRs",
        },
        "days_since_oldest_pr": {
            "icon": "mdi:calendar-clock",
            "color": "orange",
            "title": "Days Since Oldest PR",
        },
        "users": {"icon": "mdi:account-multiple", "color": "purple", "title": "Users"},
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
