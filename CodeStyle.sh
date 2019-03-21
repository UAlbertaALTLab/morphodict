autopep8 --in-place -r --aggressive --list-fixes --exclude ./CreeDictionary/API/migrations/*.py .
pycodestyle . --exclude=./CreeDictionary/API/migrations/*.py,./env/