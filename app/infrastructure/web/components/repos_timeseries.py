from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from nicegui import run, ui

from app.containers import Container
from app.domain import entities
from app.use_cases.get_repo_info_by_id import GetRepoInfoByIdUseCase


@ui.refreshable
@inject
async def repos_timeseries_component(
    info_ids: list[int],
    *,
    get_repo_info_by_id: Annotated[
        GetRepoInfoByIdUseCase, Depends(Provide[Container.get_repo_info_by_id_use_case])
    ],
) -> None:
    """Component to display timeseries graphs for multiple repositories."""

    if not info_ids:
        ui.label(
            "No repositories added yet. Add repositories using the form above."
        ).classes("text-gray-500 text-center w-full")
        return

    timeseries_list = await run.cpu_bound(get_repo_info_by_id.execute_sync, info_ids)

    with ui.column().classes("w-full gap-4"):
        # Open PRs Timeseries
        _create_timeseries_chart(
            timeseries_list,
            metric_key="open_prs",
            title="Open Pull Requests Over Time",
            y_axis_title="Open PRs",
        )

        # Closed PRs Timeseries
        _create_timeseries_chart(
            timeseries_list,
            metric_key="closed_prs",
            title="Closed Pull Requests Over Time",
            y_axis_title="Closed PRs",
        )

        # Contributors Timeseries
        _create_timeseries_chart(
            timeseries_list,
            metric_key="users",
            title="Contributors Over Time",
            y_axis_title="Contributors",
        )


def _create_timeseries_chart(
    timeseries_list: list[entities.RepoInfoEntity],
    metric_key: str,
    title: str,
    y_axis_title: str,
) -> None:
    """Helper to create a single timeseries chart."""

    series = []
    for ts_data in timeseries_list:
        metric_data = getattr(ts_data, metric_key)

        # Convert TimeseriesDataPoint to chart data format
        data = [[point.date, point.value] for point in metric_data]

        series.append(
            {
                "name": ts_data.full_name,
                "data": data,
            }
        )

    ui.highchart(
        {
            "title": {"text": title},
            "chart": {"type": "line"},
            "xAxis": {
                "type": "datetime",
                "title": {"text": "Date"},
            },
            "yAxis": {
                "title": {"text": y_axis_title},
            },
            "series": series,
            "tooltip": {
                "shared": True,
                "crosshairs": True,
            },
            "legend": {
                "enabled": True,
            },
        }
    ).classes("w-full h-96")
