.PHONY: all
all: db.sqlite3 nodesource.gpg.key
	docker-compose up --build

db.sqlite3:
	-echo '#' Creating an empty SQLite3 database: $@
	sqlite3 $@ 'VACUUM'

nodesource.gpg.key:
	curl -sSL -O https://deb.nodesource.com/gpgkey/nodesource.gpg.key 
