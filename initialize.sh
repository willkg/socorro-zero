#!/bin/bash

set -o errexit

# This initializes a vagrant dev environment. Why do this in a bash script that
# has to be run by hand rather than puppet? Mostly because it's easier to see
# the individual steps in case you have to run any of them by hand later.

# FIXME: Check for an active virtualenv and balk if there is one.

ROOTDIR="$(pwd)"

# Sets everything up for development
cd "${ROOTDIR}/socorro"
make dev

# Activate the virtual environment
. "${ROOTDIR}/socorro/socorro-virtualenv/bin/activate"

# If socorrolib repo is here, stomp on the released package with it
if [[ -e "${ROOTDIR}/socorrolib" ]]
then
    echo ">>> Found socorrolib repo--installing that...."
    cd "${ROOTDIR}/socorrolib"
    pip install -e .
fi

# FIXME: Check for configuration files, generate the ones that are
# missing and edit them with the appropriate values for this vm.

# FIXME: Change the database value in config/alembic.ini so the username is
# breakpad_rw.
# augtool ...

# Set up the db and populate it with 3 days of fake data. 3 seems to be the
# minimum amount of data to do useful things.
cd "${ROOTDIR}/socorro"
./scripts/socorro setupdb --database_name=breakpad --fakedata --fakedata_days=3 --createdb

# Create Elasticsearch index and add data for super search.
cd "${ROOTDIR}/socorro/scripts"
python setup_supersearch_app.py

# Index some crashes--need a way to have this halt at some point.
# FIXME: Fix this.
# python socorro/external/postgresql/crash_migration_app.py

# Set up some partition smoething or other
cd "${ROOTDIR}/socorro"
python socorro/cron/crontabber_app.py --job=weekly-reports-partitions --force

# Generate Django tables
cd "${ROOTDIR}/socorro/webapp-django"
# Note that you have to do ``./manage.py migrate auth`` first to get the auth
# tables, otherwise running ``./manage.py migrate`` fails.
./manage.py migrate auth
./manage.py migrate

cd "${ROOTDIR}"

echo "You'll want to activate the python virtualenv. Run:"
echo ""
echo "    . socorro/socorro-virtualenv/bin/activate"
