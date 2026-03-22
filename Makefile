.PHONY: build up down logs clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/chroma_data
	rm -rf backend/__pycache__
	rm -rf backend/services/__pycache__
	rm -rf backend/api/__pycache__
