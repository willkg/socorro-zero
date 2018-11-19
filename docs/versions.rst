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
<https://buildhub.readthedocs.io/en/latest/api.html>`_. Use the Elasticsearch
API.


Build information
=================

Every time a build is created, the binaries and metadata files are published
at:

https://archive.mozilla.org/pub/

Rough directory structure::

  pub/
    firefox/         Firefox builds
      candidates/    beta, rc, release, and esr builds
      nightly/       nightly builds

    devedition/      DevEdition (aka Firefox aurora)
      candidates/    beta builds for Firefox b1 and b2

    mobile/          Fennec builds
      candidates/    beta, rc, and release builds
      nightly/       nightly builds


In the ``candidates/`` subdirectories are build directories like ``build1/``.
Each of those is a release candidate for that version and the last one is
the final.

For example, here's the direcotry for Firefox 64.0b4:

https://archive.mozilla.org/pub/firefox/candidates/64.0b4-candidates/

In it are two build directories: ``build1/`` and ``build2/``. The first is
64.0b4rc1 and was not released to anyone. The second is 64.0b4rc2, but since
it's the last build in that series, it was released as 64.0b4.

Here's the build file for that for linux-i686 in en-US:

https://archive.mozilla.org/pub/firefox/candidates/64.0b4-candidates/build2/linux-i686/en-US/firefox-64.0b4.json

Note how the directory name has "64.0b4", but the ``moz_app_version`` is set to
"64.0".

With recent builds, there's an additional ``buildhub.json`` file:

https://archive.mozilla.org/pub/firefox/candidates/64.0b4-candidates/build1/linux-i686/en-US/buildhub.json

That includes similar information, but is built to be ingested in Buildhub.

Things to know:

1. Different platforms may have different build ids for a build. For
   example, 54.0b5 has build id 20170504103226 for windows and mac builds and
   20170504173217 for linux builds.

2. As of November 19th, 2018, https://archive.mozilla.org/pub/ appears to be
   missing some/most build information for versions 45 through 49. Buildhub
   is missing it, too. However, Socorro's ``product_versions`` tables have
   this information. I'm not sure how that happened.

3. Firefox beta 1 and beta 2 are released in the DevEdition product in the
   aurora channel. That's been happening since Firefox 55.
