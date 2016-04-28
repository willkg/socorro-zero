======
README
======

My super secret Socorro development container machine.

This has the following:

1. my notes on socorro so I don't forget.
2. a Vagrant super environment that makes it easy to work on the various
   bits that are in different repositories
3. all my opinions codified in 21-carat GOLD

:author: Will Kahn-Greene and a gaggle of goblins

.. Warning::

   This is wrong, obsolete, old, overbearing, over-engineered, under-thought,
   unofficial and disasterous to your career.

Having said that, if you have problems, let me know.


To set this up
==============

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
