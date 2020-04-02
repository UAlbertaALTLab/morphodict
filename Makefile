dockerimage: docker/requirements.txt
	cd docker/ && docker build -t creedictionary:latest .

# Exclude the editable install of this package, because:
#  - the editable install is only useful for running tests,
#  - we want to install Python dependencies BEFORE copying over the code
#  (our code changes more often than dependencies)
docker/requirements.txt:
	pipenv lock -r | grep -v -- '-e' > $@

.PHONY: dockerimage
