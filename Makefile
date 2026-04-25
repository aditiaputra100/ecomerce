PYTHON := uv
NPM := npm

.PHONY: install dev test build

install:
	$(PYTHON) sync
	$(NPM) install

dev:
	npx concurrently --kill-others-on-fail --names backend,frontend "uv run python main.py" "npm run dev"

test:
	$(PYTHON) run pytest test/backend

build:
	$(NPM) run build
