dockerimage: docker/requirements.txt docker/CreeDictionary.tar.gz
	cd docker/ && docker build -t creedictionary:latest .

# Exclude the editable install of this package, because:
#  - the editable install is only useful for running tests,
#  - we want to install Python dependencies BEFORE copying over the code
#  (our code changes more often than dependencies)
docker/requirements.txt:
	pipenv lock -r | grep -v -- '-e' > $@

docker/CreeDictionary.tar.gz: collectstatic bundle 
	tar czvf $@ CreeDictionary

bundle:
	npm run build

collectstatic: bundle
	pipenv run python3 CreeDictionary/manage.py collectstatic --no-input

.PHONY: dockerimage bundle collectstatic
