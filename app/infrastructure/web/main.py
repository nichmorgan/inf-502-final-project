from nicegui import ui
from app.containers import Container


def main() -> None:
    """Main entry point for the application."""
    # Initialize container
    container = Container()
    container.wire(
        modules=["app.infrastructure.web.pages.comparison"],
        warn_unresolved=True,
    )

    from app.infrastructure.web.pages import comparison_page

    # Run the application
    ui.run(
        root=comparison_page,
        title="Repository Comparison",
        port=5000,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
