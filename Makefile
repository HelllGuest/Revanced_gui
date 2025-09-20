# ReVanced GUI Makefile

.PHONY: help install install-dev clean test run lint format check-deps

help:
	@echo "Available commands:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install development dependencies"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  test         - Run tests (when available)"
	@echo "  run          - Run the application"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  check-deps   - Check for missing dependencies"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install black flake8 pylint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf logs/

test:
	@echo "Tests not implemented yet"

run:
	python main.py

lint:
	flake8 src/ main.py --max-line-length=100 --ignore=E203,W503

format:
	black src/ main.py --line-length=100

check-deps:
	python -c "import sys; print('Python:', sys.version)"
	python -c "import tkinter; print('tkinter: OK')"
	python -c "try: import psutil; print('psutil: OK'); except: print('psutil: Missing (optional)')"
	python -c "try: import tkinterdnd2; print('tkinterdnd2: OK'); except: print('tkinterdnd2: Missing (optional)')"
	java -version