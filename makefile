fmt:
	uv run black app tests

web:
	uv run python -m app.infrastructure.web.main

.PHONY: fmt web