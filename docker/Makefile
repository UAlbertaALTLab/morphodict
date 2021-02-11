# Sets up everything for running in Docker
#  - run (default):
#  		builds and starts the Docker container using docker-compose
#  - debug-context:
#  		runs a temporary Docker container to inspect the context
#  		(what is copied to the Docker VM to build the image)

.PHONY: run
run: db.sqlite3 nodesource.gpg.key
	docker-compose up --build

.PHONY: debug-context
debug-context:
	printf 'FROM scratch\nCOPY . /' | DOCKER_BUILDKIT=1 docker build -f- -o context .


############################## Concrete targets ##############################

db.sqlite3:
	-echo '#' Creating an empty SQLite3 database: $@
	sqlite3 $@ 'VACUUM'

/etc/systemd/service/docker-compose@.service: docker-compose@.service
	sudo cp $< $@

# Key used to verify Nodesource packages on apt.
nodesource.gpg.key:
	curl -sSL -O https://deb.nodesource.com/gpgkey/nodesource.gpg.key
