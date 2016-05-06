#!/bin/bash

# set -o errexit
set -x

ROOTDIR="$(pwd)"

# FIXME: Check for an active virtualenv and activate it if it's not currently
# activated.

# This cleans everything up so you're back to a mostly pristine environment that
# you can run "./initialize.sh" in.

# Remove the socorro db
# FIXME: This throws an error saying "breakpad" doesn't exist after successfully
# dropping the db like we asked it to. I have no idea why it throws an error
# afterwards.
cd "${ROOTDIR}/socorro"
./scripts/socorro setupdb --database_name=breakpad --dropdb
echo "Note: This threw an error saying the database doesn't exist--that's ok."

# Remove elasticsearch indexes
# FIXME: Implement this

# Remove all .pyc files in socorro/
cd "${ROOTDIR}/socorro"
find . -name "*.pyc" -exec 'rm' '{}' ';'

# Deactivate the virtual environment.
deactivate

# Last, remove the socorro virtual environment
cd "${ROOTDIR}"
rm -rf socorro/socorro-virtualenv/
