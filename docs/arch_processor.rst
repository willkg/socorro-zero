=======================
Architecture: Processor
=======================

This document covers the configuration and workings of the part of Socorro known
as "the processor" as it's configured to run on Mozilla's -stage and -prod
environments.


Processor requirements
======================

FIXME:


Processor architecture
======================

The processor is a single process which runs a "companion process".

In production, it uses the following prefixes in consul: ``socorro/common``
and ``socorro/processor``.

The processor is a ``FetchTransformSaveWithSeparateNewCrashSourceApp``.

You can run it like this::

    $ socorro processor --admin.conf=/path/to/file.ini


The task manager is the producer/consumer class
``socorrolib.lib.threaded_task_manager.ThreadedTaskManater``.


Incoming crash ids
------------------

The processor iterates over crash ids with the ``new_crashes`` method of the
``socorro.external.rabbitmq.crashstorage.RabbitMQCrashStorage`` component
configured with the ``new_crash_source`` namespace.

It switches between the ``socorro.normal``, ``socorro.priority`` and
``socorro.reprocessing`` queues using an algorithm that is designed to
prioritize items in the priority queue without starving the other two queues.

For each crash, it sends it through the fetch/transform/save steps.

After successfully processing a crash id, the ``FTSWSNCSA`` will call into
``RabbitMQCrashStorage`` which will remove the crash id from the queue. If
something happens during processing and this step doesn't occur, then the item
stays in the queue.

FIXME: ^^^ Is that correct?


Fetch
-----

For each crash id, the processor fetches the raw crash from S3 using the
``socorro.external.boto.crashstorage.BotoS3CrashStore`` configured with the
``source`` namespace.

Fetching the crash happens in two stages: first the raw crash is acquired then
the related dumps.

FIXME: What happens if the crash isn't there?


Transform
---------

The transform happens using the
``socorro.processor.mozilla_processor_2015.MozillaProcessorAlgorithm2015`` class
configured with the ``processor`` namespace.


raw_transform
~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

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


support_classifiers
~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

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

Save
----

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
----------------

After everything is completed, ``finished_func()`` is called. For -prod, this
goes back to the ``RabbitMQCrashStore`` which acks the crash id with RabbitMQ.


Symbol lru cache manager
========================

The companion process we run in productino is
``socorro.processor.symbol_cache_manager.SymbolLRUCacheManager``.

FIXME:


Architecture things to note
===========================

FIXME: Add note about how we save to multiple data stores some of which fail
periodically and how we deal with that.
