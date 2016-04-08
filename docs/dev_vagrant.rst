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

             Skip this for now.

   .. todo:: Seems like this fails on the stackwalk stuff if it's there. Might
             have to remove it before this step or something.

#. Set up the database::

      ./scripts/socorro setupdb --database_name=breakpad --fakedata --fakedata_days=3 --createdb

   This creates the database and populates it with 3 days of fake data.

   3 days seems to be the minimum amount of data to do things. If you need more,
   you can use the default which is 7.

   .. Note::

      If you ever need to wipe the database and start anew, you can do::

         ./scripts/socorro setupdb --database_name=breakpad --dropdb

      .. todo:: This drops the database, but then throws "FATAL: database
                "breakpad" does not exist" error which it probably shouldn't
                since we just told it to drop the database.

   .. todo:: With 512mb, I get out-of-memory errors here. Maybe we can switch
             lists to generators or other common Python memory optimizations in
             the fakedata generation code?

#. Created Elasticsearch index and add data for super search::

      cd scripts
      python setup_supersearch_app.py

   .. todo:: If the index exists, it'd better if this script recognized that
             better. Also, it'd be nice if this script could delete and recreate
             the index or had a flag to delete and recreate the index.

#. Index some crashes::

      python socorro/external/postgresql/crash_migration_app.py

   .. Note::

      This will take a *long* time to run, so you can CTRL-C it after a while.

#. Set up some partition something or other::

      python socorro/cron/crontabber_app.py --job=weekly-reports-partitions --force

   .. todo:: What's this do? Why do we need to do it here?

#. Configure the webapp. One way to do this is with a ``webapp-django/.env``
   file. Here's one that matches the configuration we've done so far plus
   expects you to use gunicorn which sets up the webapp on 5000 and the
   middleware on 5100::

      ALLOWED_HOSTS=''
      MWARE_BASE_URL='http://localhost:5100'
      MWARE_HTTP_HOST='socorro-middleware'
      DEBUG='True'
      CACHE_MIDDLEWARE='True'
      CACHE_MIDDLEWARE_FILES='False'
      DEFAULT_PRODUCT='WaterWolf'
      CACHE_BACKEND='django.core.cache.backends.locmem.LocMemCache'
      CACHE_LOCATION='localhost:1121'
      CACHE_KEY_PREFIX='blah'
      BROWSERID_AUDIENCES='http://localhost:5000'
      DATABASE_ENGINE='django.db.backends.postgresql_psycopg2'
      DATABASE_NAME='breakpad'
      DATABASE_USER='breakpad_rw'
      DATABASE_PASSWORD='aPassword'
      DATABASE_HOST='localhost'
      DATABASE_PORT='5432'
      SESSION_COOKIE_SECURE='False'
      COMPRESS_OFFLINE='False'
      SECRET_KEY='fixme'
      GOOGLE_ANALYTICS_ID=''
      DATASERVICE_DATABASE_USERNAME='breakpad_rw'
      DATASERVICE_DATABASE_PASSWORD='aPassword'
      DATASERVICE_DATABASE_HOSTNAME='localhost'
      DATASERVICE_DATABASE_NAME='breakpad'
      AWS_ACCESS_KEY=''
      AWS_SECRET_ACCESS_KEY=''
      SYMBOLS_BUCKET_DEFAULT_NAME=''
      SYMBOLS_BUCKET_EXCEPTIONS_USER=''
      SYMBOLS_BUCKET_EXCEPTIONS_BUCKET=''
      SYMBOLS_BUCKET_DEFAULT_LOCATION=''
      ANALYZE_MODEL_FETCHES='True'
      PWD_ALGORITHM='sha512'
      HMAC_KEYS={'any': 'thing'}
      COMPRESS_ENABLED='False'
      DATASERVICE_DATABASE_PORT='5432'
      ELASTICSEARCH_URLS='http://localhost:9200'


#. Generate Django tables::

      cd webapp-django
      ./manage.py migrate auth
      ./manage.py migrate

   Note that you have to do ``./manage.py migrate auth`` first to get the auth
   tables, otherwise running ``./manage.py migrate`` fails.

   .. todo:: Might have to migrate auth before doing the rest because of an
             ordering problem in ``INSTALLED_APPS``. Should look into it on a
             rainy day.

Running the collector
=====================

::

   honcho start collector


Running the processor
=====================

::

   honcho start process


Running the webapp and middleware
=================================

The webapp depends on the middleware, so you need to run both.

::

   honcho start web middleware


Then connect to http://localhost:5000 to see the webapp.


Outstanding:

* Getting errors from the webapp suggesting that the middleware is returning ES
  errors. I'm not positive, though.

  ::

     Traceback:
     File "/home/vagrant/socorro/socorro-virtualenv/lib/python2.7/site-packages/django/core/handlers/base.py" in get_response
       132.                     response = wrapped_callback(request, *callback_args, **callback_kwargs)
     File "/home/vagrant/socorro/webapp-django/crashstats/crashstats/utils.py" in wrapper
       54.         response = f(request, *args, **kw)
     File "/home/vagrant/socorro/webapp-django/crashstats/crashstats/decorators.py" in inner
       66.         return view(request, *args, **kwargs)
     File "/home/vagrant/socorro/webapp-django/crashstats/crashstats/views.py" in frontpage_json
       620.             product, versions, start_date, end_date
     File "/home/vagrant/socorro/webapp-django/crashstats/crashstats/views.py" in _get_frontpage_data_from_supersearch
       559.         params, start_date, end_date, platforms, 'report'
     File "/home/vagrant/socorro/webapp-django/crashstats/crashstats/views.py" in _get_crashes_per_day_with_adu
       322.     histogram = results['facets']['histogram_date']

     Exception Type: KeyError at /home/frontpage_json
     Exception Value: 'histogram_date'


.. todo:: Don't run with honcho. Run with a split terminal.
