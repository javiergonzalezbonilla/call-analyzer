.PHONY: create-environment remove-environment install-dependencies \
	docker-compose-build docker-compose-up docker-compose-down \
	docker-compose-remove docker-compose-rebuild \
	docker-compose-django-test docker-compose-web-test docker-compose-web-lint \
	docker-compose-django-format-code docker-django-sh \
	down restart up test rebuild attach format logs

create-environment:
	conda env create -f ./call_analyzer_api/env.yml

remove-environment:
	conda env remove --name call-analyzer -y

install-dependencies:
	uv pip install './call_analyzer_api[local]'

docker-compose-build:
	docker-compose -f local.yml build --provenance=false

docker-compose-up:
	docker-compose -f local.yml up -d

docker-compose-down:
	docker-compose -f local.yml down

docker-compose-remove:
	docker-compose -f local.yml rm -s

docker-compose-rebuild: docker-compose-remove
	docker-compose -f local.yml build --provenance=false
	docker-compose -f local.yml up -d

docker-compose-django-test:
	docker exec -it call-analyzer-call_analyzer_django-1 pytest

docker-compose-web-test:
	docker exec -it call-analyzer-call_analyzer_web-1 yarn test

docker-compose-web-lint:
	docker exec -it call-analyzer-call_analyzer_web-1 yarn lint

docker-compose-django-format-code:
	docker exec -it call-analyzer-call_analyzer_django-1 black .

docker-django-sh:
	docker exec -it call-analyzer-call_analyzer_django-1 sh

down: docker-compose-down

restart: docker-compose-down docker-compose-up

up: docker-compose-up

test: docker-compose-django-test 

rebuild: docker-compose-rebuild

format: docker-compose-django-format-code

logs:
	docker logs -f call-analyzer-call_analyzer_django-1
attach: 
	docker attach call-analyzer-call_analyzer_django-1