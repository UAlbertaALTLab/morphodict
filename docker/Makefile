# Sets up everything for running in Docker
#
# ## Commands ##
#
#  make run [default]
#  		builds and starts the Docker container using docker-compose
#  		creates any necessary files for building the image/running the
#  		container
#  make unit-file
#  		copies the systemd unit file to the right location;
#  		make require sudo
#  make debug-context
#  		runs a temporary Docker container to inspect the context
#  		(what is copied to the Docker VM to build the image)

SYSTEMD_SERVICE = docker-compose-itwewina

.PHONY: run
run: db.sqlite3 nodesource.gpg.key .env
	docker-compose up --build

.PHONY: unit-file
unit-file: $(SYSTEMD_SERVICE).service
	cp $< /etc/systemd/service/$(SYSTEMD_SERVICE).service

.PHONY: debug-context
debug-context:
	printf 'FROM scratch\nCOPY . /' | DOCKER_BUILDKIT=1 docker build -f- -o context .


############################## Concrete targets ##############################

# The database file.
# If not created before `docker-compose up` is run, then Docker will create a
# **directory** and not an empty file ¯\_(ツ)_/¯
#
# Required during **container runtime**
db.sqlite3:
	-echo '#' Creating an empty SQLite3 database: $@
	sqlite3 $@ 'VACUUM'

# Contains configuration, like the SECRET_KEY
#
# N.B., the image build will create an .env to run management commands, but it
# will be shadowed by the Docker mount command (i.e., ignored) when the
# container is run in production.
#
# Required during **container runtime**
.env:
	-echo '#' Creating a .env file with a secret key
	printf "SECRET_KEY=" > $@
	python3 -c "import secrets; print(secrets.token_hex())" >> $@

# Key used to verify Nodesource packages on apt.
#
# Required during **image build**
nodesource.gpg.key:
	curl -sSL -O https://deb.nodesource.com/gpgkey/nodesource.gpg.key
