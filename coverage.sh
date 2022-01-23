coverage erase
coverage run -m unittest discover test
coverage report -m
coverage html
bandit --ini .bandit -r -f json -o bandit_baseline.json