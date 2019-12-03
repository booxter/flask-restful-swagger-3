release:
	git tag -a `python setup.py --version` -m "Releasing to https://pypi.python.org/pypi/flask-restful-swagger-3/"
	git push --tags
	rm -rf dist
	python setup.py sdist
	twine upload dist/*
