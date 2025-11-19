from nicegui import ui
from app.containers import Container
from app.infrastructure.web.pages.comparison_page import create_comparison_page


def main() -> None:
    """Main entry point for the application."""
    # Initialize container
    container = Container()
    container.wire(modules=["app.infrastructure.web.pages.comparison_page"])

    # Create the comparison page
    create_comparison_page()

    # Run the application
    ui.run(title="Repository Comparison", port=8080)


if __name__ in {"__main__", "__mp_main__"}:
    main()
