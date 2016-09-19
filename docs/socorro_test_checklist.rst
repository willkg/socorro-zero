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

    * Log into collector node and watch the crashmover logs for errors.
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

    * Log into processor node and watch the processor logs for errors.
    * Check datadog ``processor.save_raw_and_processed`` for appropriate
      environment.

Is the processor saving to S3?

    * Check datadog
      ``processor.s3.BotoS3CrashStorage.save_raw_and_processed`` for
      appropriate environment.

Is the processor saving to ES?

    * FIXME: Check datadog?

Is the processor saving to Postgres?

    * Check datadog
      ``processor.postgres.PostgreSQLCrashStorage.save_raw_and_processed`` for
      appropriate environment.

Submit a crash. Verify processed crash made it to S3, ES and postgres.


Webapp
======

Is the webapp up?

Is the webapp throwing errors?

    * Check sentry for errors
    * Log into webapp node and check logs for errors.
    * Run QA Selenium tests.

Can we log into the webapp?

FIXME: What else do we want to verify?


Crontabber
==========

FIXME: What can we look at here?


Stage crashmover
================

Is it running and sending crashes?

    * Check datadog stage environment ``crashmover.save_raw_crash``
