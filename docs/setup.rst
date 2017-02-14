=====
Setup
=====

:Date: February 1st, 2017
:Author: Will Kahn-Greene


Summary
=======

This is an analysis of all the setup that's required to get Socorro going in an
environment. It's currently a tangle of scripts, so it's a little hard to
follow. Further, when we dockerize things, we're going to want to change things
to take advantage of layer caching for Docker images.

This is going to trace how to set up Socorro in Vagrant since that's a
self-contained and complete environment.

After that, it'll talk about re-ordering the steps and configuration adjustments
to make it work better in Docker.


What happens
============

Socorro Puppet file is here: ``socorro/puppet/vagrant/modules/socorro/manifests/init.pp``

1. Add repositories

   Elasticsearch: http://packages.elasticsearch.org/elasticsearch/1.4/centos
   Postgresql: http://yum.postgresql.org/9.4/redhat/rhel-$releasever-$basearch

2. Install packages

   fpm, ca-certificates, yum-plugin-fastestmirror

3. Install build requirements

   bzip2-devel, epel-release, gcc-c++, git, httpd, java-1.7.0-openjdk,
   java-1.7.0-openjdk-devel, libcurl-devel, libffi-devel, libxml2-devel,
   libxslt-devel, make, memcached, mercurial, mod_wsgi, nodejs, npm,
   openldap-devel, openssl-devel, pylint, python-devel, rpm-build, rsync,
   ruby-devel, rubygem-puppet-lint, sqlite-devel, subversion, time, unzip

   .. Note::

      We probably don't need pylint.

      Possibly don't need httpd or mod_wsgi, either--pretty sure we use nginx
      now.

   .. Note::

      We'll use a separate container for memcache.

4. Build Python 2.7.11

   Uses ``socorro/puppet/vagrant/modules/socorro/files/build_python.sh`` to
   build Python 2.7.11.

5. Install Postgres 9.4

   postgres94-contrib, postgres94-devel, postgres94-plperl, postgres94-server

   Runs ``/usr/pgsql-9.4/bin/postgresql94-setup initdb``.

   .. Note::

      We'll use a separate docker container for postgres, but we still need to
      build the Python lib, so we'll need postgres94-devel.

      Probably want to add a note that the version of the package we're using
      needs to match the container image we're using.

   There's a pgsql.sh file that is installed. We should think about this.

   ``socorro/puppet/vagrant/modules/socorro/etc_profile.d/pgsql.sh``

   There's a pg_hba.conf file that is installed. We should think about this.

   ``socorro/puppet/vagrant/modules/socorro/var_lib_pgsql_9.4_data/pg_hba.conf``

6. Create two postgres roles

   test::

     cmd: sudo -u postgres psql template1 -c "create user test with encrypted password \'aPassword\' superuser"
     unless: sudo -u postgres psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'test\'" | grep -q 1

   breakpad_rw::

     cmd: sudo -u postgres psql template1 -c "create user breakpad_rw with encrypted password \'aPassword\' superuser"
     unless: sudo -u postgres psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'breakpad_rw\'" | grep -q 1

7. Install more packages

   python-virtualenv, supervisor, rabbitmq-server, python-pip, nodejs-less

   .. NOTE::

      If we're installing our own Python, we probably don't need
      python-virtualenv and python-pip and should install our own and not system
      versions.

   .. NOTE::

      rabbitmq should be its own Docker container.

8. Install packages to make Will happy

   vim, emacs-nox

9. Install elasticsearch

   elasticsearch

   .. NOTE::

      We'll want to have Elasticsearch run in a separate container.

   There's an elasticsearcy.yml file that is installed. We should think about
   this.

10. Install motd file

    .. NOTE::

       Not sure we need this. This was to make the Vagrant vm more user-friendly.

11. Configure sshd

    .. NOTE::

       Not sure we need this.

12. 
