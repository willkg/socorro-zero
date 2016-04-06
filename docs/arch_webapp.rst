==========
The webapp
==========


Architecture
============

The webapp is a Django app.

:framework:   Django
:entry point: ``webapp-django/``
:config:      ``webapp-django/crashstats/settings/``, ``webapp-django/.env``



Notes
=====

* Vestiges of playdoh floating around.
* Hard to 
* Get this when it errors out when running with Honcho::

     14:22:27 web.1        | Raven is not configured (logging is disabled). Please see the documentation for more information.


* If you're running the middleware and web separately, you need to start the web
  first so it grabs port 5000. Otherwise the middleware will

  So I tried this::

     # In terminal A
     cd webapp-django && ./manage.py runserver 0.0.0.0:5000

     # In terminal B
     honcho start middleware

  That doesn't work, because honcho will try to start the middleware on 5000 and
  fail.

  So I did it manually without honcho::

     # In terminal A
     cd webapp-django && ./manage.py runserver 0.0.0.0:5000

     # In terminal B
     gunicorn wsgi.middleware

  That starts the middleware on port 8000. Where is it getting the port number
  from?
