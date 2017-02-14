DC := $(shell which docker-compose)

default:
	@echo "You need to specify a subcommand."
	@exit 1

help:
	@echo "build            - build docker containers for dev"
	@echo ""
	@echo "run              - run all the socorro nodes"

# Dev configuration steps
.docker-build:
	make build

build:
	${DC} build socorrobase
	touch .docker-build

bootstrap: .docker-build
	${DC} run socorrobase bin/build_stackwalker.sh
	${DC} run socorrobase bin/bootstrap_webapp.sh

# FIXME(willkg): shell

# FIXME(willkg): test

# FIXME(willkg): clean

run: .docker-build
	${DC} up

.PHONY: default help clean build run
