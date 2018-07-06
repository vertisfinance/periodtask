usr := $(shell id -u):$(shell id -g)

distrbute:
	-rm dist/*
	docker-compose run --rm -u $(usr) periodtask python3 setup.py sdist
	docker-compose run --rm -u $(usr) periodtask twine upload dist/*

test:
	# docker-compose run --rm -u $(usr) periodtask python3 -m unittest
	docker-compose run --rm -u $(usr) periodtask coverage run --source periodtask -m unittest
	docker-compose run --rm -u $(usr) periodtask coverage html

.PHONY: docs
docs:
	docker-compose run --rm -u $(usr) periodtask sphinx-build -b html docs/source docs/build
