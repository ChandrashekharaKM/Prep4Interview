.PHONY: help install dev-install run-api run-frontend run-both redis-start redis-stop docker-up docker-down test lint format clean

help:
	@echo "HR-Copilot Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install              Install dependencies"
	@echo "  make dev-install          Install with dev dependencies"
	@echo ""
	@echo "Running locally:"
	@echo "  make redis-start          Start Redis in Docker"
	@echo "  make redis-stop           Stop Redis container"
	@echo "  make run-api              Run FastAPI server (port 8000)"
	@echo "  make run-frontend         Run Streamlit UI (port 8501)"
	@echo "  make run-both             Run API and Frontend (requires 2 terminals)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up            Start all services with Docker Compose"
	@echo "  make docker-down          Stop all Docker Compose services"
	@echo "  make docker-build         Build Docker images"
	@echo ""
	@echo "Testing & Code Quality:"
	@echo "  make test                 Run pytest"
	@echo "  make test-cov             Run tests with coverage"
	@echo "  make lint                 Run ruff linter"
	@echo "  make format               Format code with black"
	@echo "  make format-check         Check code formatting"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                Remove cache and build artifacts"
	@echo "  make policy-ingest        Ingest HR policies into ChromaDB"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev-install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

run-api:
	uvicorn main:app --reload --port 8000

run-frontend:
	streamlit run frontend/app.py --logger.level=info

run-both:
	@echo "Starting HR-Copilot..."
	@echo "API will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:8501"
	@echo "You need to run this in 2 separate terminals:"
	@echo ""
	@echo "Terminal 1: make run-api"
	@echo "Terminal 2: make run-frontend"

redis-start:
	docker run -d --name hr-copilot-redis -p 6379:6379 redis:7-alpine && \
	echo "Redis started on localhost:6379"

redis-stop:
	docker stop hr-copilot-redis && \
	docker rm hr-copilot-redis && \
	echo "Redis stopped and removed"

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d && \
	echo "Services starting..." && \
	sleep 3 && \
	echo "API: http://localhost:8000" && \
	echo "Frontend: http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=graph --cov=tools --cov=memory --cov=frontend --cov-report=html

lint:
	ruff check .

format:
	black .

format-check:
	black --check .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf htmlcov/ .coverage

policy-ingest:
	@echo "Make sure Redis is running first: make redis-start"
	python tools/policy_qa.py --ingest
