VOLUMENAME = creedictionary
CONTAINERNAME = creedictionary
IMAGENAME = creedictionary:latest

dockerimage: docker/requirements.txt docker/CreeDictionary.tar.gz
	cd docker/ && docker build -t creedictionary:latest .

run: dockerimage run-quick

create-volume:
	docker volume create $(VOLUMENAME)

migrate-in-volume:
	docker run -it --rm \
		--mount source=$(VOLUMENAME),target=/data \
		$(IMAGENAME) migrate

run-quick:
	docker run -it \
		--name $(CONTAINERNAME) \
		--mount source=$(VOLUMENAME),target=/data \
		-p 8000:8000 --rm $(IMAGENAME)

shell:
	docker exec -it $(CONTAINERNAME) /bin/bash

# Exclude the editable install of this package, because:
#  - the editable install is only useful for running tests,
#  - we want to install Python dependencies BEFORE copying over the code
#  (our code changes more often than dependencies)
docker/requirements.txt: Pipfile.lock
	pipenv lock -r | grep -v -- '^-e' > $@

docker/CreeDictionary.tar.gz: collectstatic bundle
	tar czvf $@ CreeDictionary

bundle:
	npm run build

collectstatic: bundle
	pipenv run /usr/bin/env DEBUG=False python3 CreeDictionary/manage.py collectstatic --no-input -v 3

.PHONY: dockerimage bundle collectstatic shell run run-quick create-volume migrate-in-volume
