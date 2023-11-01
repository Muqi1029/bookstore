#!/bin/sh
export PATHONPATH=`pwd`
python
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data
coverage combine
coverage report
coverage html

read -p "Press any key to exit"