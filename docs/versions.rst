========
Versions
========

Crash reports include a ``Version`` key which is the version of the application
that crashed.


Version fixing
==============

There are a few cases where the ``Version`` value isn't the actual version
of the application, but instead is the version the application would have
if it was a final release.

Socorro's processor has a ``BetaVersionRule`` that fixes the version in these
cases. It additionally looks at the ``ReleaseChannel`` value.

1. If the product is Firefox and the release channel is aurora, then it
   could be a beta 1 or beta 2 build.

   For these, the ``BetaVersionRule`` does a Buildhub lookup for
   ("devedition", "aurora", buildid). If that returns a version, then
   ``BetaVersionRule`` changes the version to that.
   

2. If the product is Firefox or Fennec and the release channel is beta, then:

   2.1. it could be a beta build.

        ``BetaVersionRule`` does a Buildhub lookup for
        (product, channel, buildid). If that returns a version that doesn't
        have "rc" in it, then ``BetaVersionRule`` changes the version to that.

   2.2. it could be a release candidate for a release channel build.

        If the version looks like a "major release" and ends in ``.0``,
        ``BetaVersionRule`` does a Buildhub lookup for
        (product, "release", buildid). If that returns a version that
        has "rc" in it, then ``BetaVersionRule`` changes the version
        to that.


You can see the `BetaVersionRule source code here
<https://github.com/mozilla-services/socorro/blob/dc0137d1077c09176de23c3374c978235436fcdc/socorro/processor/mozilla_transform_rules.py#L569>`_.


Buildhub
========

`Buildhub <https://mozilla-services.github.io/buildhub/>`_ is a catalog of
build information for Firefox, Fennec, Devedition, and Thunderbird.

Buildhub has `documentation for the APIs
<https://buildhub.readthedocs.io/en/latest/api.html>`_. At the time of this
writing, I **highly** suggest using the Elasticsearch API as it's much
faster and performant.


Build information
=================

Every time a build is created, the binaries and metadata files are published
at:

https://archive.mozilla.org/pub/

For example, here's the build file for Firefox 64.0b6 en-US Linux-i686:

https://archive.mozilla.org/pub/firefox/candidates/64.0b6-candidates/build1/linux-i686/en-US/firefox-64.0b6.json

Note how the directory name has "64.0b6", but the ``moz_app_version`` is set to
"64.0".

With recent builds, there's an additional ``buildhub.json`` file:

https://archive.mozilla.org/pub/firefox/candidates/64.0b6-candidates/build1/linux-i686/en-US/buildhub.json

That includes similar information, but it's probably the case we'd have to do
less work to infer the important bits.


Rough directory structure::

  pub/
    firefox/         Firefox builds
      candidates/    beta builds
      nightly/       nightly builds
      releases/      release builds; esr builds

    devedition/      Firefox devedition (aka aurora)
      candidates/    beta builds

    mobile/          Fennec builds
      candidates/    beta builds
      nightly/       nightly builds
      releases/      release builds


