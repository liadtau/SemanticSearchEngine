.PHONY: build up down logs restart clean ps backend-shell llm-shell chroma-shell frontend-shell

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

ps:
	docker compose ps

clean: down
	docker compose rm -f
	docker volume rm semanticsearchengine_chroma_data semanticsearchengine_llm_cache || true
	rm -rf backend/__pycache__
	rm -rf backend/services/__pycache__
	rm -rf backend/api/__pycache__
	rm -rf llm-inference/__pycache__

backend-shell:
	docker compose exec -it backend /bin/bash

llm-shell:
	docker compose exec -it llm /bin/bash

chroma-shell:
	docker compose exec -it chroma /bin/bash

frontend-shell:
	docker compose exec -it frontend /bin/sh
