export DOCKER_USER=mashajing2000
export PROJECT_NAME=websocket-mockserver
export IMAGE=${DOCKER_USER}/${PROJECT_NAME}
export VERSION=2.0.1
export PYPI_URL=pypi
export REPO_URL=https://github.com/MashaJing/Websocket-Mockserver

.PHONY: build
build:
	docker build --pull -t ${IMAGE}:${VERSION} .
	docker push ${IMAGE}:${VERSION}

.PHONY: publish
publish:
	@pip install twine
	@python3 setup.py sdist bdist_wheel
	@python -m twine upload --repository ${PYPI_URL} dist/* --verbose
