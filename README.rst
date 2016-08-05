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


To set this up with Docker
==========================

1. Install Docker 1.10.0+ and docker-compose 1.6.0+.

2. Clone this repo::

     $ git clone https://github.com/willkg/socorro-zero.git

   We're going to call that directory the repository root.

3. Clone the other repositories as subdirectories of the repository root::

     $ git clone https://github.com/mozilla/socorro
     $ git clone https://github.com/mozilla/socorrolib
     ...

   For each of these repositories, do whatever it is you need to do to get the
   remotes set up for your needs.

4. Then go back to the repository root and run::

     FIXME

   This will create all the required docker containers and launch it all with a
   configuration that's like Mozilla crash-stats production.


Zero? What?
===========

This isn't a single Python package, but rather a development environment
with a set of configurations and opinions codified in it. The idea is
that you set it up and then you can do the work you need to do.

The idea is based on the ideas in this blog post:

http://ramblings.timgolden.me.uk/2016/04/14/network-zero/
