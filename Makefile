.PHONY: install run clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Sync dependencies from pyproject.toml"
	@echo "  make add PKG=<package>  - Add a new package (e.g., make add PKG=fastapi)"
	@echo "  make run        - Run the application"
	@echo "  make clean      - Clean up cache and temporary files"

install:
	uv sync

add:
	@test -n "$(PKG)" || (echo "Usage: make add PKG=package-name" && exit 1)
	uv add $(PKG)

run:
	uv run python main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
