usr := $(shell id -u):$(shell id -g)
version := $(shell sed -rn "s/^VERSION = '(.*)'$$/\1/p" setup.py)

version:
	@echo $(version)

distribute: build test docs
	@-rm dist/*
	@docker-compose run --rm -u $(usr) periodtask python3 setup.py sdist
	@docker-compose run --rm -u $(usr) periodtask twine upload dist/*
	@git tag $(version)
	@git push --tags

build:
	@docker-compose build

.PHONY: test
test:
	@docker-compose run --rm -u $(usr) periodtask coverage run --source periodtask -m unittest -f
	@docker-compose run --rm -u $(usr) periodtask coverage report
	@docker-compose run --rm -u $(usr) periodtask coverage html

.PHONY: docs
docs:
	@docker-compose run --rm -u $(usr) periodtask sphinx-build -b html docs/source docs/build
