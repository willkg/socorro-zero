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

FIXME: Does it use ``socorro/reprocessor``?


processor
---------

The processor is a ``FetchTransformSaveWithSeparateNewCrashSourceApp``.

You can run it like this::

    $ socorro processor --admin.conf=/path/to/file.ini



FIXME:


symbol lru cache manager
------------------------

The companion process we run in productino is
``socorro.processor.symbol_cache_manager.SymbolLRUCacheManager``.

FIXME:


Architecture things to note
===========================

FIXME: Add note about how we save to multiple data stores some of which fail
periodically and how we deal with that.
