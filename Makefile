.PHONY: create-environment 

create-environment:
	conda env create -f ./call-analyzer-api/env.yml

remove-environment:
	conda env remove --name call-analyzer -y

install-dependencies:
	uv pip install './call-analyzer-api[local]'


	