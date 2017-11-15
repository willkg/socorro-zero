======
README
======

My socorro-zero development environment plus notes.

This has the following:

1. some notes on socorro so I don't forget
2. a Docker-based -zero environment that makes it easy/easier to work on the
   various parts in different repositories as well as the integrated whole in
   various configurations
3. all my opinions codified in 21-carat GOLD


:author: Will Kahn-Greene and a gaggle of goblins
:issues: https://github.com/willkg/socorro-zero

.. Warning::

   It's possible that this is wrong, obsolete, old, overbearing,
   over-engineered, under-thought, unofficial and disasterous to your
   career.

Having said that, if it's helpful, let me know. If you have problems,
write up an issue.


Docker setup
============

Status: January 30th, 2017
--------------------------

* DONE: collector
* DONE: crashmover
* In-progress: prod-like configuration
* Todo: processor
* Todo: middleware
* Todo: webapp


Setup instructions
------------------

1. Install Docker 1.10.0+ and docker-compose 1.6.0+.

2. Clone this repo::

     $ git clone https://github.com/willkg/socorro-zero.git

   We're going to call that directory the repository root.

3. Clone the other repositories as subdirectories of the repository root::

     $ git clone https://github.com/mozilla/socorro

     # FIXME(willkg): are there other repositories needed?

   For each of these repositories, do whatever it is you need to do to get the
   remotes set up for your needs.

   At the end of this step, the socorro-zero repository root should look like::

     bin/
     dockerfiles/
     docs/
     socorro/             <-- the socorro git repo
     Dockerfile
     LICENSE
     README.rst
     docker-compose.yml
     ...

4. In the repository root, do this::

     make build

   This will build the required docker containers.


Usage
-----

To run everything::

  $ make run

To send a test crash:

FIXME

To check graphite and see statsd data, go to http://localhost/ .


Vagrant setup
=============

Status: January 30th, 2017
--------------------------

This setup is deprecated, but I still use it to run the socorro test suite.
I'm not doing any maintenance work on it.


Setup instructions
------------------

1. Clone this repo::

     $ git clone https://github.com/willkg/socorro-zero.git

2. Change directories::

     $ cd socorro-zero

3. Clone the other repository::

     $ git clone https://github.com/mozilla/socorro

   Do whatever it is you need to do to get the remotes set up for your needs.

4. Then go back to the socorro-zero root directory and run::

     $ vagrant up

   This will do the following:

   1. create a vagrant environment for development
   2. FIXME

5. Log into the vm::

     $ vagrant ssh

6. Initialize the development environment::

     $ cd zero/
     $ ./initialize.sh


At this point, you should have a functioning development environment.

Usage
-----

To run unit tests::

    $ cd zero
    $ cd socorro
    $ ./scripts/test.sh


Zero? What?
===========

This isn't a single Python package, but rather a development environment
with a set of configurations and opinions codified in it. The idea is
that you set it up and then you can do the work you need to do.

The idea is based on the ideas in this blog post:

http://ramblings.timgolden.me.uk/2016/04/14/network-zero/
