# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

DC := $(shell which docker-compose)

.PHONY: help
help: default
	@echo "You need to specify a subcommand."
	@exit 1

.PHONY: default
default:
	@echo "setup            - set up Socorro repositories"

.PHONY: setup
setup:
	@echo "tbd"
