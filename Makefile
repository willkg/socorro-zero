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
	${DC} build
	touch .docker-build

# FIXME(willkg): shell

# FIXME(willkg): test

# FIXME(willkg): clean

run: .docker-build
	${DC} up

.PHONY: default help clean build run
