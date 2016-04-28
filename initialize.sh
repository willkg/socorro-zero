#!/bin/bash

# This initializes a vagrant dev environment. Why do this in a bash script that
# has to be run by hand rather than puppet? Mostly because it's easier to see
# the individual steps in case you have to run any of them by hand later.

pushd socorro

# Sets everything up for development.
make dev

# FIXME: Change the database value in config/alembic.ini so the username is
# breakpad_rw.
# augtool ...

# Set up the db and populate it with 3 days of fake data. 3 seems to be the
# minimum amount of data to do useful things.
./scripts/socorro setupdb --database_name=breakpad --fakedata --fakedata_days=3 --createdb

# Create Elasticsearch index and add data for super search.
pushd scripts
python setup_supersearch_app.py
popd

# Index some crashes--need a way to have this halt at some point.
# FIXME: Fix this.
# python socorro/external/postgresql/crash_migration_app.py

# Set up some partition smoething or other
python socorro/cron/crontabber_app.py --job=weekly-reports-partitions --force

# FIXME: Configure the webapp

# Generate Django tables
pushd webapp-django
# Note that you have to do ``./manage.py migrate auth`` first to get the auth
# tables, otherwise running ``./manage.py migrate`` fails.
./manage.py migrate auth
./manage.py migrate
popd

popd
