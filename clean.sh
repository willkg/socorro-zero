#!/bin/bash

# This cleans everything up so you're back to a mostly pristine environment that
# you can run "./initialize.sh" in.

# Remove the socorro db
# FIXME: This throws an error saying "breakpad" doesn't exist after successfully
# dropping the db like we asked it to. I have no idea why it throws an error
# afterwards.
pushd socorro
./scripts/socorro setupdb --database_name=breakpad --dropdb
echo "Note: This threw an error saying the database doesn't exist--that's ok."
popd

# Remove elasticsearch indexes
# FIXME: Implement this

# Remove all .pyc files in socorro/
pushd socorro
find . -name "*.pyc" -exec 'rm' '{}' ';'
popd

# Deactivate the virtual environment.
# FIXME: Maybe we should check to see if we're in a virtual environment first?
deactivate

# Last, remove the socorro virtual environment
rm -rf socorro/socorro-virtualenv/
