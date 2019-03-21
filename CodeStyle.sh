
autopep8 --in-place -r --aggressive --exclude ./CreeDictionary/API/migrations/*.py .
pycodestyle . --exclude=./CreeDictionary/API/migrations/*.py,./env/