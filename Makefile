.PHONY: help install test test-metrics test-dq test-synthetic generate-small generate-medium lint

help:
	@echo "Placewise Makefile"
	@echo "  make install           Install Python dependencies"
	@echo "  make test              Run all tests"
	@echo "  make test-metrics      Run metric unit tests only"
	@echo "  make test-dq           Run data quality tests only"
	@echo "  make test-synthetic    Run synthetic data tests only"
	@echo "  make generate-small    Generate small_demo synthetic dataset"
	@echo "  make generate-medium   Generate medium_demo synthetic dataset"
	@echo "  make lint              Run ruff linter"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --tb=short

test-metrics:
	pytest tests/metrics/ -v --tb=short

test-dq:
	pytest tests/data_quality/ -v --tb=short

test-synthetic:
	pytest tests/synthetic/ -v --tb=short

generate-small:
	cd synthetic && python run_generator.py --profile small_demo --output ../data/synthetic --validate

generate-medium:
	cd synthetic && python run_generator.py --profile medium_demo --output ../data/synthetic --validate

lint:
	ruff check synthetic/ tests/
