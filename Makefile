	
docker: docker/requirements.txt
	cd docker/ && docker build .

docker/requirements.txt:
	pipenv lock -r | grep -v -- '-e' > $@

.PHONY: docker
