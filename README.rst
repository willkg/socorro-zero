======
README
======

This is my separate Socorro Secret Manual where I write stuff down with
several expectations:

1. initially, it's my notes from onboarding and geared towards me
2. it could be horribly wrong so I don't really want other non-me people
   depending on it
3. it's missing bits which might get filled in over time depending on
   what I spend my time on
4. the bits that are right and finished will be migrated in some form
   to the real manual


To build
========

::

    $ mkvirtualenv sm
    $ pip install -r requirements.txt
    $ cd docs && make html
