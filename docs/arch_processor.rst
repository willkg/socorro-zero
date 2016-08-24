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

Save
----

Saves to a ``PolyCrashstorage`` destination.

1. storage0: PostgresSQLCrashStorage
2. storage1: BotoS3CrashStorage
3. storage2: BotoS3CrashStorage or ESCrashStorageRedact--can't tell which
4. storage3: StatsdCounter


After everything
----------------

After everything is completed, ``finished_func()`` is called.

FIXME: What does that do?


Symbol lru cache manager
========================

The companion process we run in productino is
``socorro.processor.symbol_cache_manager.SymbolLRUCacheManager``.

FIXME:


Architecture things to note
===========================

FIXME: Add note about how we save to multiple data stores some of which fail
periodically and how we deal with that.
