all: requirements.txt
	docker build .

debug-context:
	printf 'FROM scratch\nCOPY . /' | DOCKER_BUILDKIT=1 docker build -f- -o context .

requirements.txt:
	pipfile2req > $@

