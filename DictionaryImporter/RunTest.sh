#!/bin/bash
coverage run --source . -m unittest discover -p  "*_test.py"
coverage report -m