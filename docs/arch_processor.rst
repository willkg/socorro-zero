=======================
Architecture: Processor
=======================

This document covers the configuration and workings of the part of Socorro known
as "the processor" as it's configured to run on Mozilla's -stage and -prod
environments.


Processor requirements
======================

Hard requirements:

1. Process crash reports.
2. Reprocess crash reports.
3. Save processed crash reports to S3, Postgres and Elasticsearch. [#]_
4. Run an external stackwalker process and manage the symbols files it requires. [#]_
5. Allow people to adjust signature generation related lists. [#]_
6. Run cron jobs updating data used by the processor. FIXME: True?

.. [#] Postgres is used for some reports, but I don't think it's used for much
       else. We might be able to remove it from the mix.

       Further, the plan to move Socorro data to Telemetry might also relieve
       our needs for Elasticsearch depending on how that all pans out.

.. [#] Maybe we could turn stackwalking into a service, too?
   
.. [#] We have toyed with doing this as a separate service. If we spun it out as
       a service, the processor could do an HTTP API request to get a signature
       generated.


Processor architecture
======================

The "processor" consists of a processor process (socorro-processor), a companion
process (SymbolLRUCacheManager) which manages cached symbols files and cron jobs.


Processor
---------

In production, the processor uses the following prefixes in consul:
``socorro/common`` and ``socorro/processor``.

The processor is a ``FetchTransformSaveWithSeparateNewCrashSourceApp``.

You can run it like this::

    $ socorro processor --admin.conf=/path/to/file.ini


The task manager is the producer/consumer class
``socorrolib.lib.threaded_task_manager.ThreadedTaskManater``.


Handling incoming crash ids
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The processor iterates over crash ids with the ``new_crashes`` method of the
``socorro.external.rabbitmq.crashstorage.RabbitMQCrashStorage`` component
configured with the ``new_crash_source`` namespace.

It switches between the ``socorro.normal``, ``socorro.priority`` and
``socorro.reprocessing`` queues using an algorithm that is designed to
prioritize items in the priority queue without starving the other two queues.

For each crash, it sends it through the fetch/transform/save steps.

After a crash is processed, the same thread that plucked the crash from the
crash iterator calls the ``finished_func`` of the resource behind the iterator.
For RMQ, that function acknowledges that the item in the queue has been
successfully processed. Depending on how RMQ is configured, if a item in the
queue is has not been ack'd within a configured timeout, the queued item is
offered again. There is some ambiguity in the behavior of RMQ at this point. It
is unclear if the item is subsequently offered to any random RMQ client or if it
is only offered to the same client again.


Fetch step
~~~~~~~~~~

For each crash id, the processor fetches the raw crash from S3 using the
``socorro.external.boto.crashstorage.BotoS3CrashStore`` configured with the
``source`` namespace.

Fetching the crash happens in two stages: first the raw crash is acquired then
the related dumps.

If the requested crash id is not found in storage, that storage is responsible
for raising the ``CrashIDNotFound`` exception. On receiving that exception, the
FTS framework will reject the ID, logging the exception, acknowledges the item
in the queue and then waiting for the next queued item.

.. Note::

   There is an implementation of a crash store called ``FallbackCrashStorage``
   that can have primary and secondary storage implementations. If the primary
   storage raises the ``CrashIDNotFound`` exception, then the
   ``FallbackCrashStorage`` will intercept the exception and try the secondary
   storage. The ``CrashIDNotFound`` will only propagate outward if both storage
   systems fail to find the ID. This is a useful class to use if migrating from
   one primary crash storage system to another. The newer system can be
   configured as primary, while the older system can be the secondary.

   We don't use this at Mozilla.


Transform step
~~~~~~~~~~~~~~

The transform happens using the
``socorro.processor.mozilla_processor_2015.MozillaProcessorAlgorithm2015`` class
configured with the ``processor`` namespace.


raw_transform
`````````````

::

    [   # rules to change the internals of the raw crash
        "raw_transform",
        "processor.json_rewrite",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_all_rules",

        "socorro.processor.mozilla_transform_rules.ProductRewrite,"
        "socorro.processor.mozilla_transform_rules.ESRVersionRewrite,"
        "socorro.processor.mozilla_transform_rules.PluginContentURL,"
        "socorro.processor.mozilla_transform_rules.PluginUserComment,"
        "socorro.processor.mozilla_transform_rules.FennecBetaError20150430"

    ],


raw_to_processed_transform
``````````````````````````

::

    [   # rules to transform a raw crash into a processed crash
        "raw_to_processed_transform",
        "processer.raw_to_processed",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_all_rules",

        "socorro.processor.general_transform_rules.IdentifierRule, "
        "socorro.processor.breakpad_transform_rules.BreakpadStackwalkerRule2015, "
        "socorro.processor.mozilla_transform_rules.ProductRule, "
        "socorro.processor.mozilla_transform_rules.UserDataRule, "
        "socorro.processor.mozilla_transform_rules.EnvironmentRule, "
        "socorro.processor.mozilla_transform_rules.PluginRule, "
        "socorro.processor.mozilla_transform_rules.AddonsRule, "
        "socorro.processor.mozilla_transform_rules.DatesAndTimesRule, "
        "socorro.processor.mozilla_transform_rules.OutOfMemoryBinaryRule, "
        "socorro.processor.mozilla_transform_rules.JavaProcessRule, "
        "socorro.processor.mozilla_transform_rules.Winsock_LSPRule, "
    ],

The ``socorro.processor.breakpad_transform_rules.BreakdpadStaclkwalkerRule2015``
runs the stackwalker binary as a separate process using the symbols files cached
on the file system and maintained by the SymbolLRUCacheManager.


processed_transform
```````````````````

::

    [   # post processing of the processed crash
        "processed_transform",
        "processer.processed",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_all_rules",

        "socorro.processor.breakpad_transform_rules.CrashingThreadRule, "
        "socorro.processor.general_transform_rules.CPUInfoRule, "
        "socorro.processor.general_transform_rules.OSInfoRule, "
        "socorro.processor.mozilla_transform_rules.BetaVersionRule, "
        "socorro.processor.mozilla_transform_rules.ExploitablityRule, "
        "socorro.processor.mozilla_transform_rules.FlashVersionRule, "
        "socorro.processor.mozilla_transform_rules.OSPrettyVersionRule, "
        "socorro.processor.mozilla_transform_rules.TopMostFilesRule, "
        "socorro.processor.mozilla_transform_rules.MissingSymbolsRule, "
        "socorro.processor.signature_utilities.SignatureGenerationRule,"
        "socorro.processor.signature_utilities.StackwalkerErrorSignatureRule, "
        "socorro.processor.signature_utilities.OOMSignature, "
        "socorro.processor.signature_utilities.AbortSignature, "
        "socorro.processor.signature_utilities.SignatureRunWatchDog, "
        "socorro.processor.signature_utilities.SignatureIPCChannelError, "
        "socorro.processor.signature_utilities.SigTrunc, "
    ],

This generates the signature. Signature generation currently relies on regexes
generated from files checked into GitHub as well as the sentinels file which
helps us establish the top-most frame of the interesting part of the stack
trace. Those files and instructions are here:

https://github.com/mozilla/socorro/tree/master/socorro/siglists


support_classifiers
```````````````````

::

    [   # a set of classifiers for support
        "support_classifiers",
        "processor.support_classifiers",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_until_action_succeeds",

        "socorro.processor.support_classifiers.BitguardClassifier, "
        "socorro.processor.support_classifiers.OutOfDateClassifier"
    ],


jit_classifiers
```````````````

::

    [   # a set of classifiers to help with jit crashes
        "jit_classifiers",
        "processor.jit_classifiers",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_all_rules",

        "socorro.processor.breakpad_transform_rules.JitCrashCategorizeRule, "
        "socorro.processor.signature_utilities.SignatureJitCategory, "
    ],


skunk_classifiers
`````````````````

::

    [   # a set of special request classifiers
        "skunk_classifiers",
        "processor.skunk_classifiers",
        "socorrolib.lib.transform_rules.TransformRuleSystem",
        "apply_until_action_succeeds",

        "socorro.processor.skunk_classifiers.DontConsiderTheseFilter, "
        # currently not in use, anticipated to be re-enabled in the future
        #"socorro.processor.skunk_classifiers.UpdateWindowAttributes, "
        "socorro.processor.skunk_classifiers.SetWindowPos, "
        # currently not in use, anticipated to be re-enabled in the future
        #"socorro.processor.skunk_classifiers.SendWaitReceivePort, "
        # currently not in use, anticipated to be re-enabled in the future
        #"socorro.processor.skunk_classifiers.Bug811804, "
        # currently not in use, anticipated to be re-enabled in the future
        #"socorro.processor.skunk_classifiers.Bug812318, "
        "socorro.processor.skunk_classifiers.NullClassification"
    ]


FIXME: Finish this analysis.


Save step
~~~~~~~~~

Saves to a ``PolyCrashstorage`` destination.

1. storage0: PostgresSQLCrashStorage

   Saves the processed crash to Postgres.

   Postgres is used by something for reports.

   FIXME: ^^^

2. storage1: BotoS3CrashStorage

   Saves the processed crash to the pseudo-filename ``/v1/processed/{crashid}``.

   FIXME: Verify that pseudo-filename.

3. storage2: ESCrashStorageRedactedJsonDump

   This makes some changes to the processed crash and then stores the results in
   ElasticSearch.

   Note: This currently mutates the processed crash, so every crash storage
   class after this is operating on a mutated processed crash.

   ElasticSearch is used by the webapp for super search and other things.

4. storage3: StatsdCounter

FIXME: I thought we had a TelemetryCrashDump, too. Where'd that go?

FIXME: Talk about what happens when one of these fails and "transactions" and
all that.


After everything
~~~~~~~~~~~~~~~~

After everything is completed, ``finished_func()`` is called. For -prod, this
goes back to the ``RabbitMQCrashStore`` which acks the crash id with RabbitMQ.


Symbol lru cache manager
------------------------

The companion process we run in productino is
``socorro.processor.symbol_cache_manager.SymbolLRUCacheManager``.

It starts up and closes down alongside the processor process.

It uses Linux's inotify API to monitor the disk and remove symbols files that
haven't been used in a while.


Cron jobs
---------

FIXME: Are there cron jobs that affect the processor?


About symbols
=============

The processor participates in a larger ecology of symbols which has many parts
that play different roles and bounce data back and forth.

During processing, the breakpad ``stackwalker`` will walk the stack expanding
symbols. It downloads symbols files from a specified URL as needed and caches
them in a specified directory.

The ``SymbolLRUCacheManager`` watches the cache directory and removes symbols
files that haven't been used in a while.

Symbol files are collected through several mechanisms:

1. uploaded through the Socorro webapp by people
2. uploaded through the Socorro webapp by a cron job that runs at Ted's house

   http://hg.mozilla.org/users/tmielczarek_mozilla.com/fetch-win32-symbols/file

3. generated by building Firefox (FIXME: Verify/clarify this.)
4. FIXME: Other places?

FIXME: Talk about Windows Breakpad ``dump_syms``.


About signatures
================

Socorro generates signatures for crashes. This process relies on data that
changes pretty regularly, thus we have a need for reprocessing crashes.

https://github.com/mozilla/socorro/tree/master/socorro/siglists

When those files change, we need to do a deploy to update the processor causing
it to pick up the new lists.

Any changes to those files only affect processing of crashes from that point
onward and doesn't affect crashes that have already been processed. In order to
update those, they need to be reprocessed.


About reprocessing
=================


Other architecture things to note
=================================

FIXME: Add note about how we save to multiple data stores and how we deal with
failures.
