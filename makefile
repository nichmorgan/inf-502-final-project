fmt:
	uv run black app tests

web:
	uv run python -m app.infrastructure.web.main

test:
	uv run pytest --cov

.PHONY: fmt web test