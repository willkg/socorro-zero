======================
Socorro Test Checklist
======================

This is a high-level system-wide checklist for making sure Socorro is working
correctly in a specific environment. It's helpful after we've made a significant
change.

.. contents::


Collector
=========

Is the collector web process handling incoming crashes?

    * Log into collector node and watch the collector logs for errors.

Is the collector crashmover process saving crashes to S3? ES? Postgres?
RabbitMQ?

    * Log into a collector node and watch the crashmover logs for errors.

      ``/var/log/messages`` is the log file.

      ``grep ERROR /var/log/messages | less`` to check for errors.

    * Check datadog ``crashmover.save_raw_crash`` for the appropriate
      environment.

      :prod: it's on the Socorro Prod dashboard
      :stage: ?
  
    * Submit a crash. Verify raw crash made it to S3. See these
      docs:
      http://socorro.readthedocs.io/en/latest/configuring-socorro.html?highlight=curl#test-collection-and-processing
   

Processor
=========

Is the processor process running?

    * Log into a processor node and watch the processor logs for errors.

      ``/var/log/messages`` is the log file.

      ``grep ERROR /var/log/messages | less`` to check for errors.

    * Check datadog ``processor.save_raw_and_processed`` for appropriate
      environment.

Is the processor saving to S3?

    * Check datadog
      ``processor.s3.BotoS3CrashStorage.save_raw_and_processed`` for
      appropriate environment.

Is the processor saving to ES?

    * Check datadog
      ``processor.es.ESCrashStorageNoStackwalkerOutput.save_raw_and_processed.avg``
      on the Socorro Prod Perf dashboard.

Is the processor saving to Postgres?

    * Check datadog
      ``processor.postgres.PostgreSQLCrashStorage.save_raw_and_processed`` for
      appropriate environment.

Submit a crash. Verify processed crash made it to S3, ES and postgres.


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
