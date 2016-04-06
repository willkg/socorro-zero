==============
The middleware
==============

Current status: The middleware is going away. Peter and Adrian are working on
that.


Architecture
============

The middleware is a web.py application that exposes an API (either REST or
REST-like) for accessing crash and crash stats data.

:framework:   web.py
:entry point: socorro/middleware/middleware_app.py MiddlewareApp
:config:      config/middleware.ini
:help:        python socorro/middleware/middleware_app.py --help


Tips
====

Run the middleware with::

   gunicorn wsgi.middelware -b HOST:PORT

and specify the HOST:PORT for ``MWARE_BASE_URL`` in the webapp settings.

Honcho can also start it up, but it picks a port to use and if that doesn't
match the webapp settings, then the webapp can't communicate with the
middleware.

.. todo:: Fix this--it's pretty annoying.

Enhance logging with::

    --logging.stderr_error_logging_level=10   # debug
    --logging.syslog_error_logging_level=10   # debug


Logs to stderr and also syslog at localhost:514?


Notes
=====

Vestiges of hbase still floating around.

This error when running::

    14:21:16 middleware.1 | /home/vagrant/socorro/socorro-virtualenv/lib/python2.7/site-packages/configman/config_manager.py:743: UserWarning: Invalid options: web_server.port
    14:21:16 middleware.1 |   'Invalid options: %s' % ', '.join(unmatched_keys)


That's fishy.
