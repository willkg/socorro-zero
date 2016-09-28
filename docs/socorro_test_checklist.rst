======================
Socorro Test Checklist
======================

This is a high-level system-wide checklist for making sure Socorro is working
correctly in a specific environment. It's a helpful template for figuring out
what you need to change if you're pushing out a significant change.

**Note:** This is used infrequently, so if you're about to make a significant change,
you should go through the checklist to make sure the checklist is correct and
that everything is working as expected and fix anything that's wrong, THEN
make your change, then go through the checklist again.

Lonnen the bear says, "Only you can prevent production fires!"

.. contents::


How to use
==========

"Significant change" can mean any number of things, so this is just a template.
You should do the following:

1. Copy and paste the contents of this into an etherpad.

2. Go through the etherpad and remove the things that don't make sense and
   add additional things that are important.

3. Uplift any interesting changes via PR to this document.


Collector
=========

Is the collector web process handling incoming crashes?

    * Log into collector node and watch the collector logs for errors.

      ``/var/log/messages`` is the log file.

      To check for errors, you could do this::

          grep ERROR /var/log/messages | less


Is the collector crashmover process saving crashes to S3? ES? Postgres?
RabbitMQ?

    * Log into a collector node and watch the crashmover logs for errors.

      ``/var/log/messages`` is the log file.

      To check for errors, you could do this::

          grep ERROR /var/log/messages | less

    * Check datadog ``crashmover.save_raw_crash`` for the appropriate
      environment.

      :prod: it's on the Socorro Prod Perf dashboard
      :stage: it's on the Socorro Stage Perf dashboard
  
    * Submit a crash. Verify raw crash made it to S3. See these
      docs:
      http://socorro.readthedocs.io/en/latest/configuring-socorro.html?highlight=curl#test-collection-and-processing
   

Processor
=========

Is the processor process running?

    * Log into a processor node and watch the processor logs for errors.

      ``/var/log/messages`` is the log file.

      To check for errors, you could do this::

          grep ERROR /var/log/messages | less

    * Check datadog ``processor.save_raw_and_processed`` for appropriate
      environment.

      :prod: Socorro Prod Perf dashboard
      :stage: Socorro Stage Perf dashboard

Is the processor saving to S3?

Is the processor saving to ES? Postgres? S3?

    * Check datadog
      ``processor.es.ESCrashStorageRedactedJsonDump.save_raw_and_processed.avg``

      :prod: Socorro Prod Perf dashboard
      :stage: Socorro Stage Perf dashboard

    * Check datadog
      ``processor.s3.BotoS3CrashStorage.save_raw_and_processed`` for
      appropriate environment.

      :prod: Socorro Prod Perf dashboard
      :stage: Socorro Stage Perf dashboard

    * Check datadog
      ``processor.postgres.PostgreSQLCrashStorage.save_raw_and_processed``

      :prod: Socorro Prod Perf dashboard
      :stage: Socorro Stage Perf dashboard


Submit a crash or look at the crashmover logs for a crash that should
have been processed. Verify the crash was processed and made it to S3, ES and postgres.

**FIXME:** We should write a script that uses envconsul to provide vars and takes
a uuid via the command line and then checks all the things to make sure it's
there. This assumes we don't already have one--we might!


Webapp
======

Is the webapp up?

    * Use a browser and check the healthcheck.

      :prod: https://crash-stats.mozilla.com/monitoring/healthcheck/
      :stage: https://crash-stats.allizom.org/monitoring/healthcheck/

      It should say "ok: true".

Is the webapp throwing errors?

    * Check sentry for errors
    * Log into webapp node and check logs for errors.

      ``/var/log/messages`` is the log file.

      ``grep ERROR /var/log/messages | less`` to check for errors.

    * Run QA Selenium tests.

      :prod: In IRC: ``webqatestbot build socorro.prod.saucelabs``
      :stage: In IRC: ``webqatestbot build socorro.stage.saucelabs``

Can we log into the webapp?

    * Log in and check the profile page.

Is super search working?

    * Click "Super Search" and make a search that is not likely to be cached.
      For example, filter on a specific date.

Top Crashers Signature report and Report index

    * Browse to Top Crashers, browse to Signature report (by clicking a
      signature), browse to Report index (by clicking a crash id) to verify
      these work.

Can you upload a symbols file?

    * Download https://github.com/mozilla/socorro/blob/master/webapp-django/crashstats/symbols/tests/sample.zip
      to disk
    * Log in with a user with permission to upload symbols.
    * Go to the symbol upload section.

      :prod: https://crash-stats.mozilla.com/symbols/upload/web/
      :stage: https://crash-stats.allizom.org/symbols/upload/web/

    * Try to upload the ``sample.zip`` file.
    * To verify that it worked, go to the public symbols S3 bucket:

      :stage: org.mozilla.crash-stats.staging.symbols-public

      and check that there is a ``xpcshell.sym`` file in the root with a recent
      modify date. 


Crontabber
==========

Is crontabber working?

    * Check healthcheck endpoint.

      :prod: https://crash-stats.mozilla.com/monitoring/crontabber/
      :stage: https://crash-stats.allizom.org/monitoring/crontabber/

      It should say ALLGOOD.

      There's a more comprehensive UI:

      :prod: https://crash-stats.mozilla.com/crontabber-state/
      :stage: https://crash-stats.allizom.org/crontabber-state/


Stage crashmover
================

Is it running and sending crashes?

    * Check datadog stage environment ``crashmover.save_raw_crash``
