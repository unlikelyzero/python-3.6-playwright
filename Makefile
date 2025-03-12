.PHONY: all setup clean test install-py36 install-py39 install-deps test-local test-remote test-debug help check-python-versions playwright-up playwright-down

# Python paths - using pyenv
PYTHON36 := $(shell which python3.6)
PYTHON39 := $(shell which python3.9)
VENV36 = python-3.6-venv
VENV39 = playwright-venv

# Test configuration
TEST_FILE = tests/test_subprocess_python36.py
TEST_FILTER ?= ""
PLAYWRIGHT_WS_ENDPOINT ?= ws://localhost:3000
TEST_RESULTS_DIR = test-results

help:
	@echo "Available commands:"
	@echo "  make setup         - Create virtual environments and install dependencies"
	@echo "  make clean        - Remove virtual environments and cache files"
	@echo "  make test-local   - Run tests with local browser"
	@echo "  make test-remote  - Run tests against Playwright container"
	@echo "  make test-debug   - Run tests with debugging options"
	@echo "  make install-deps - Install dependencies in both virtual environments"
	@echo "  make playwright-up   - Start Playwright container"
	@echo "  make playwright-down - Stop Playwright container"
	@echo ""
	@echo "To run specific tests, use TEST_FILTER:"
	@echo "  make test-local TEST_FILTER=test_basic_navigation"
	@echo "  make test-remote TEST_FILTER=test_basic_navigation"

all: setup test-local

setup: check-python-versions install-py36 install-py39
	mkdir -p $(TEST_RESULTS_DIR)

clean:
	rm -rf $(VENV36) $(VENV39)
	rm -rf __pycache__ .pytest_cache
	rm -rf $(TEST_RESULTS_DIR)/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install-py36:
	@if [ -z "$(PYTHON36)" ]; then \
		echo "Python 3.6 not found. Please install it with: pyenv install 3.6.15"; \
		exit 1; \
	fi
	@echo "Creating Python 3.6 virtual environment using $(PYTHON36)"
	"$(PYTHON36)" -m venv "$(VENV36)"
	. "$(VENV36)/bin/activate" && \
		pip install --upgrade pip && \
		pip install -r requirements.txt

install-py39:
	@if [ -z "$(PYTHON39)" ]; then \
		echo "Python 3.9 not found. Please install it with: pyenv install 3.9.21"; \
		exit 1; \
	fi
	@echo "Creating Python 3.9 virtual environment using $(PYTHON39)"
	"$(PYTHON39)" -m venv "$(VENV39)"
	. "$(VENV39)/bin/activate" && \
		pip install --upgrade pip && \
		pip install -r requirements-playwright.txt && \
		playwright install chromium

install-deps: install-py36 install-py39

test-local:
	. "$(VENV39)/bin/activate" && \
		pytest $(TEST_FILE) -v $(if $(TEST_FILTER),-k $(TEST_FILTER),)

test-remote:
	. "$(VENV39)/bin/activate" && \
		pytest $(TEST_FILE) -v \
		--junitxml=$(TEST_RESULTS_DIR)/junit.xml \
		--html=$(TEST_RESULTS_DIR)/report.html \
		--self-contained-html \
		$(if $(TEST_FILTER),-k $(TEST_FILTER),)

test-debug:
	. "$(VENV39)/bin/activate" && \
		pytest $(TEST_FILE) -v --headed --slowmo 1000 $(if $(TEST_FILTER),-k $(TEST_FILTER),)

playwright-up:
	docker-compose up -d playwright

playwright-down:
	docker-compose down

# Check if required Python versions are installed
check-python-versions:
	@echo "Checking Python versions..."
	@if [ -z "$(PYTHON36)" ]; then \
		echo "Python 3.6 not found. Please install it with: pyenv install 3.6.15"; \
		echo "Then run: pyenv global \$$(pyenv global) 3.6.15"; \
		exit 1; \
	fi
	@if [ -z "$(PYTHON39)" ]; then \
		echo "Python 3.9 not found. Please install it with: pyenv install 3.9.21"; \
		echo "Then run: pyenv global \$$(pyenv global) 3.9.21"; \
		exit 1; \
	fi
	@echo "Found Python 3.6 at: $(PYTHON36)"
	@echo "Found Python 3.9 at: $(PYTHON39)"
	@echo "Python versions OK" 