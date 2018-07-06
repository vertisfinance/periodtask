usr := $(shell id -u):$(shell id -g)

distribute: v := $(shell cat VERSION)
distribute:
	@docker-compose build
	@-rm dist/*
	@docker-compose run --rm -u $(usr) periodtask python3 setup.py sdist
	@docker-compose run --rm -u $(usr) periodtask twine upload dist/*
	@git tag $(v)
	@git push --tags

test:
	@docker-compose run --rm -u $(usr) periodtask coverage run --source periodtask -m unittest
	@docker-compose run --rm -u $(usr) periodtask coverage report
	@docker-compose run --rm -u $(usr) periodtask coverage html

.PHONY: docs
docs:
	@docker-compose run --rm -u $(usr) periodtask sphinx-build -b html docs/source docs/build
