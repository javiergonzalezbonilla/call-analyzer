
.PHONY: 
	create-environment 
	remove-environment
	install-dependencies
	docker-compose-build
	docker-compose-up
	docker-compose-down
	docker-compose-remove
	docker-compose-rebuild


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
	docker-compose -f local.yml up
	
