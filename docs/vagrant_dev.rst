===================
Vagrant environment
===================

Setup
=====

#. If you already have a ``stackwalk/`` directory, delete it::

      rm -rf stackwalk/

   .. note::

      If we don't delete this now, then ``make dev`` fails later on and I'm not
      sure why. We can't delete it from within the vagrant vm because it kicks
      up permission errors. I don't know why.

   .. todo:: Figure out why we have to do this and why it's not handled
      better in ``make dev``.

#. From the repository root run::

      vagrant up

   This creates the vm.

   .. todo:: We should add port forwarding so it's easier to connect to the
             webapp. Doing ``honcho start web`` runs gunicorn at port 5000, but
             doing ``./manage.py runserver`` runs the django webserver at
             port 8000.

             We should pick one and write a shell script/alias/whatever for the
             other.

   .. todo:: Vagrantfile currently sets the memory at 512mb, but I hit
             out-of-memory errors with that. Increasing to 1024mb fixed it.

   .. todo:: There's a line to enable debug output when provisioning. This is
             commented out. Instead of doing that, we should make it environment
             variable affected.

#. Then log into the vm::

      vagrant ssh

#. Nix the firewall::

      sudo -s
      systemctl disable firewalld
      systemctl stop firewalld

   CentOS 7 has a firewall enabled, so nothing listening to ports will ever get
   incoming connections. That'll stop and disable the firewall from running in
   the future.

   .. todo::

      We should add this to the Vagrant provisioning.

#. Then cd to the socorro directory::

      cd socorro

#. Build the basic stuff::

      make dev

#. Create the ``breakpad_rw`` role::

      sudo -s postgresql psql template1 -c "create user breakpad_rw with encrypted password 'aPassword' superuser"

   .. todo:: We should probably do this in the vagrant provisioning.

#. Edit ``config/alembic.ini``. You want to change the ``database_username`` to
   ``breakpad_rw``.

   The previous value is for the test role and I think we want to not be using
   the test role for things.

   .. todo:: Does this sound right? Why use the test role for testing and
             development?

#. Run::

      make test

   .. todo:: Why run make test here? It seems like it does some setup but I
             don't know what or why this gets done in make test and not other
             ways.

#. Set up the database::

      ./scripts/socorro setupdb --database_name=breakpad --fakedata --createdb

   This creates the database and populates it with fake data.

   .. Note::

      If you ever need to wipe the database and start anew, you can do::

         ./scripts/socorro setupdb --database_name=breakpad --dropdb

   .. todo:: With 512mb, I get out-of-memory errors here. Maybe we can switch
             lists to generators or other common Python memory optimizations in
             the fakedata generation code?

#. Set up some partition something or other::

      python socorro/cron/crontabber_app.py --job=weekly-reports-partitions --force

   .. todo:: What's this do? Why do we need to do it here?

#. Generate Django tables::

      cd webapp-django
      ./manage.py migrate auth
      ./manage.py migrate

   Have to do ``./manage.py migrate auth`` first to get the auth tables.
   Otherwise ``./manage.py migrate`` fails.

   .. todo:: Might have to migrate auth before doing the rest because of an
             ordering problem in ``INSTALLED_APPS``. Should look into it on a
             rainy day.

#. Add data to ES for super search::

      cd scripts
      python setup_supersearch.py

   .. todo:: If the index exists, it'd better if this script recognized that
             better. Also, it'd be nice if this script could delete and recreate
             the index.

   .. todo:: I have no idea what this does, but I ran it for hours and it never
             terminated. Further, it seems to make the system unstable. I'm
             guessing either there's an infinite loop or we generate a lot of
             fakedata and it needs to all get added and it does it slowly or
             some third thing.
