include .env

FLAGS=

lint:
	# poetry run mypy --install-types
	poetry run black .
	poetry run isort .
	poetry run mypy . --disallow-untyped-defs
	poetry run flake8 .

run:
	poetry run python -m cityfind

redis_start:
	docker-compose -f docker-compose.yml up -d redis

redis_stop:
	docker-compose -f docker-compose.yml stop redis
