.PHONY: up down logs psql

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f app

psql:
	docker compose exec -it db psql -U app -d app
