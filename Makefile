.PHONY: up down build test seed

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

test:
	cd backend && python -m pytest tests/ -v

seed:
	cd backend && python -m app.seed
