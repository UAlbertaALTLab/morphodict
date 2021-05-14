# Sets up everything for running in Docker
#
# ## Commands ##
#
#  make production [default]
#  		builds and starts the Docker container using docker-compose
#  		creates any necessary files for building the image/running the
#  		container
#  make staging
#  		builds and starts the Docker container using docker-compose for
#  		testing the production build elsewhere.
#  make unit-file
#  		copies the systemd unit file to the right location;
#  		requires sudo
#  make debug-context
#  		runs a temporary Docker container to inspect the context
#  		(what is copied to the Docker VM to build the image)

SYSTEMD_SERVICE = docker-compose-itwewina

.PHONY: production
production: db.sqlite3 .env
	docker-compose up --build --remove-orphans

.PHONY: staging
staging: .env ../src/CreeDictionary/test_db.sqlite3
	ln -f ../src/CreeDictionary/test_db.sqlite3 ./db.sqlite3
	docker-compose up --build --remove-orphans

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
	touch $@

# Contains configuration, like the SECRET_KEY
#
# N.B., the image build will create an .env to run management commands, but it
# will be shadowed by the Docker mount command (i.e., ignored) when the
# container is run in production.
#
# Required during **container runtime**
.env:
	-echo '#' Creating an empty .env file
	touch $@

../src/CreeDictionary/test_db.sqlite3:
	@echo '# Creating the test database by running the unit tests'
	cd .. && pipenv run pytest
