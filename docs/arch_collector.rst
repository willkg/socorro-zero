=======================
Architecture: Collector
=======================

This document covers the configuration and workings of the part of Socorro known
as "the collector" as it's configured to run on Mozilla's -stage and -prod
environments.


Collector requirements
======================

1. Reliable: We shouldn't drop crashes and the HTTP endpoint should be
   working--lots of 9s.
2. Get crash data to S3 as fast and reliably as possible.
3. Scale horizontally: We have multiple collector nodes behind an ELB.
4. Handle crash reports ~500k in size. (See crash report size analysissection.)

Soft requirements (it might be possible to do this differently):

1. We need to throttle incoming crashes to get rid of junk data and so we don't
   overwhelm the processor.
2. We need to feed our -stage system with real crash data for testing and
   development.


Crash report size analysis
==========================

From https://bugzilla.mozilla.org/show_bug.cgi?id=1271790#c3

On May 16th, 2016, Adrian wrote:

    I downloaded 10,000 processed crashes from our stage S3 onto my file system
    on May 12. Hopefully that's a big enough set, because it took a full night
    to download all that data. :)

    Note that documents include sensitive data and the full json dump. Raw crash
    data is not included.

    Here's an analysis of the size of those documents (numbers in kilobytes)::

        count    10000
        mean       486
        std       1170
        min          1
        25%        177
        50%        250
        75%        348
        max      18944

    Then, to find the average number of processed crashes per week, I used this
    query:
    https://crash-stats.mozilla.com/api/SuperSearch/?_results_number=0&_facets=_histogram.date&_histogram_interval.date=1w&date=%3E2016-01-04&date=%3C2016-05-16
    (count of documents per week between the beginning of the year and now).
    Using the above average document size, I got those results::

        Average number of documents per week: 2,533,611
        Estimated number of documents for 26 weeks: 65,873,886
        Estimated size of 1 week of data: 1,174 Gb
        Estimated size of 26 weeks of data: 29 Tb


Collector architecture
======================

Each web node runs three things:

1. nginx
2. gunicorn which contains the WSGI application (web app)
3. crashmover process


Web app
-------

The web app part of the collector uses the web.py WSGI application framework.

In production, it uses the following prefixes in consul: ``socorro/common``
and ``socorro/collector``.

It handles incoming HTTP POST requests to the ``/submit`` endpoint.

Breakpad crash data is submitted as ``multipart/form-data``.

It can be gzipped.

It can contain a ``Throttleable=1`` parameter which indicates that the crash
should not be throttled.

Incoming HTTP POST requests are handled in this way:

1. contents are uncompressed if need be
2. ``current_timestamp`` is generated
3. if there's no ``uuid`` parameter, then a crash id is created from a randomly
   generated uuid4 and the date of the current timestamp as YYMMDD
4. the crash is run through the throttler and the result and percentage is
   saved on the raw crash
5. depending on the throttle result:

   ACCEPT, DEFER:

   1. crash is saved to the local filesystem
   2. ``CrashID=xxxxx`` is returned to client in HTTP response

   DISCARD:

   1. ``Discarded=1`` is returned to client

   IGNORED:

   1. ``Unsupported=1`` is returned to client


As of August 5th, 2016, the throttler rules are something like::

  # drop the browser side of all multi submission hang crashes
  ("*", '''lambda d: "HangID" in d
      and d.get("ProcessType", "browser") == "browser"''', None),
  # 100% of crashes with comments
  ("Comments", '''lambda x: x''', 100),
  # 100% of all aurora, beta, esr channels
  ("ReleaseChannel", '''lambda x: x in ("aurora", "beta", "esr")''', 100),
  # 100% of all crashes that report as being nightly
  ("ReleaseChannel", '''lambda x: x.startswith('nightly')''', 100),
  # 10% of Firefox
  ("ProductName", 'Firefox', 10),
  # 100% of Fennec
  ("ProductName", 'Fennec', 100),
  # 100% of all alpha, beta or special
  ("Version", r'''re.compile(r'\..*?[a-zA-Z]+')''', 100),
  # 100% of Thunderbird & SeaMonkey
  ("ProductName", '''lambda x: x[0] in "TSC"''', 100),
  # reject everything else
  (None, True, 0)


Crashmover process
------------------

The crashmover process monitors the local filesystem for new crashes.

In production, it uses the following prefixes in consul: ``socorro/common`` and
``socorro/crashmover``.

For each crash, it does the following:

1. saves the crash to S3 as a "raw_crash"
2. (ACCEPT-only) tosses the crash id in the "socorro.normal" rabbitmq queue for
   processing
3. (PROD-only, ACCEPT-only) tosses the crash id in the "socorro.stagesubmitter"
   rabbitmq queue for processing
4. plus some statsd pings for various things


Architectural things to note
============================

1. nginx can't decompress POST data, so we have to do it in Python-land

2. We want to return a crashid and end the HTTP connection as quickly as
   possible. Because of this, we can't wait to send the data to S3 and RabbitMQ.
   Thus we store the crash on disk and have the separate crashmover process deal
   with it.

3. Storing the crash on disk allows us to manually go in and send crashes along
   if the crashmover process ever dies and can't come back up.

4. We want to be able to get a list of all crashes that came in on a specific
   day. Because of that, we use the following pseudo-filename schema::

     {prefix}/v2/{name_of_thing}/{entropy}/{date}/{id}

   For the Mozilla production setup, that's effectively::

     /v2/raw_crash/{entropy}/{date}/{id}

   where "entropy" is the first three characters of the id and "date" is the last
   six characters.

5. We siphon 10% of crashes submitted to the production system to the stage
   system. The way we do this is by having the production collector crashmover
   submit 10% of incoming crashes to the ``socorro.stag esubmitter`` rabbitmq
   queue.

   A magical fairy named "stage submitter" watches that queue, pulls the raw
   crash data from S3 and HTTP POSTs it to the stage collector.

6. We remove ``\00`` characters from incoming crash data because it hoses later
   processing. Theoretically, there shouldn't be any in there anyhow.
