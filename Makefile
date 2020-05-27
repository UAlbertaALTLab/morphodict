VOLUMENAME = creedictionary
CONTAINERNAME = creedictionary
IMAGENAME = creedictionary:latest

dockerimage: docker/requirements.txt collectstatic bundle
	docker build -t creedictionary:latest -f docker/Dockerfile .

run: dockerimage run-quick

volume:
	docker volume create $(VOLUMENAME)

migrate-in-volume:
	docker run -it --rm \
		--mount source=$(VOLUMENAME),target=/data \
		$(IMAGENAME) migrate

run-quick:
	docker run -it \
		--name $(CONTAINERNAME) \
		--mount source=$(VOLUMENAME),target=/data \
		-p 8000:8000 -p 8001:8001 --rm $(IMAGENAME)

# Attach to an already running container for debugging purpose
shell:
	docker exec -it $(CONTAINERNAME) /bin/bash

# This container overwrites `manage.py runserver` entrypoint and cmd defined in dockerfile and runs bash shell instead
# Can be used in local development to investigate configuration issues
debug-container:
	docker run -it \
	  --name $(CONTAINERNAME) \
	  --entrypoint '/bin/sh' \
	  --mount source=$(VOLUMENAME),target=/data \
	  -p 8000:8000 -p 8001:8001 --rm $(IMAGENAME)

# Exclude the editable install of this package, because:
#  - the editable install is only useful for running tests,
#  - we want to install Python dependencies BEFORE copying over the code
#  (our code changes more often than dependencies)
docker/requirements.txt: Pipfile.lock
	pipenv lock -r | grep -v -- '^-e' > $@

bundle:
	npm run build

collectstatic: bundle
	pipenv run /usr/bin/env DEBUG=False python3 CreeDictionary/manage.py collectstatic --no-input -v 3

.PHONY: dockerimage bundle collectstatic shell run run-quick volume migrate-in-volume
