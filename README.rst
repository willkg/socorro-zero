======
README
======

My socorro-zero development environment plus notes.

This has the following:

1. some notes on socorro so I don't forget
2. a Vagrant -zero environment that makes it easy/easier to work on the various
   bits that are in different repositories
3. all my opinions codified in 21-carat GOLD


:author: Will Kahn-Greene and a gaggle of goblins
:issues: https://github.com/willkg/socorro-zero

.. Warning::

   It's possible that this is wrong, obsolete, old, overbearing,
   over-engineered, under-thought, unofficial and disasterous to your
   career.

Having said that, if it's helpful, let me know. If you have problems,
write up an issue.


To set this up with Vagrant
===========================

1. Clone this repo::

       $ git clone https://github.com/willkg/socorro-zero.git

2. Change directories::

       $ cd socorro-zero

3. Clone the other repositories::

       $ git clone https://github.com/mozilla/socorro
       $ git clone https://github.com/mozilla/socorrolib
       ...

   For each of these repositories, do whatever it is you need to do to
   get the remotes set up for your needs.

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


To set this up with Docker (doesn't work, yet)
==============================================

1. Clone this repo::

       $ git clone https://github.com/willkg/socorro-zero.git

2. Change directories::

       $ cd socorro-zero

3. Clone the other repositories::

       $ git clone https://github.com/mozilla/socorro
       $ git clone https://github.com/mozilla/socorrolib
       ...

   For each of these repositories, do whatever it is you need to do to
   get the remotes set up for your needs.

4. FIXME (not implemented, yet) Then go back to the socorro-zero root directory
   and run::

       $ docker-compose run socorro initialize.sh


   This will do the following:

   1. create all the docker containers
   2. run ``initialize.sh`` in the socorro one


At this point, you should have a functioning development environment.

Running Charon::

    $ docker-compose run antenna

Running Charon tests::

    $ docker-compose run antenna py.test [ARGS]


FIXME: Explain how to use it.


Zero? What?
===========

This isn't a single Python package, but rather a development environment
with a set of configurations and opinions codified in it. The idea is
that you set it up and then you can do the work you need to do.

The idea is based on the ideas in this blog post:

http://ramblings.timgolden.me.uk/2016/04/14/network-zero/
