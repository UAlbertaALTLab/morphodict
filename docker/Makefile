# Sets up everything for running in Docker
#  - run (default):
#  		builds and starts the Docker container using docker-compose
#  - unit-file:
#  		copies the systemd unit file to the right location;
#  		make require sudeo
#  - debug-context:
#  		runs a temporary Docker container to inspect the context
#  		(what is copied to the Docker VM to build the image)

SYSTEMD_SERVICE = docker-compose-itwewina

.PHONY: run
run: db.sqlite3 nodesource.gpg.key /etc/systemd/service/docker-compose@.service
	docker-compose up --build

.PHONY: unit-file
unit-file: $(SYSTEMD_SERVICE).service
	cp $< /etc/systemd/service/$(SYSTEMD_SERVICE).service

.PHONY: debug-context
debug-context:
	printf 'FROM scratch\nCOPY . /' | DOCKER_BUILDKIT=1 docker build -f- -o context .


############################## Concrete targets ##############################

db.sqlite3:
	-echo '#' Creating an empty SQLite3 database: $@
	sqlite3 $@ 'VACUUM'


# Key used to verify Nodesource packages on apt.
nodesource.gpg.key:
	curl -sSL -O https://deb.nodesource.com/gpgkey/nodesource.gpg.key
