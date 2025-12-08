from nicegui import ui
from app.domain.entities.repo import RepoTimeseriesEntity

__all__ = ["repos_timeseries_component"]


@ui.refreshable
def repos_timeseries_component(
    timeseries_list: list[RepoTimeseriesEntity],
) -> None:
    """Component to display timeseries graphs for multiple repositories."""

    if not timeseries_list:
        ui.label("No repositories added yet. Add repositories using the form above.").classes(
            "text-gray-500 text-center w-full"
        )
        return

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
    timeseries_list: list[RepoTimeseriesEntity],
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
