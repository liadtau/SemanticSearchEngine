.PHONY: build up down logs clean

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

clean: down
	docker compose rm -f
	docker volume rm semanticsearchengine_chroma_data semanticsearchengine_llm_cache || true
	rm -rf backend/__pycache__
	rm -rf backend/services/__pycache__
	rm -rf backend/api/__pycache__
	rm -rf llm-inference/__pycache__

