# Dockerfile for socorrobase
FROM centos:centos7

# Set Python-related environment variables to reduce annoying-ness
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app

# Set up the postgres repo
COPY files/pgdg.repo /etc/yum.repos.d
RUN rpm --import http://yum.postgresql.org/RPM-GPG-KEY-PGDG

# Get all the stuff we need to build everything
RUN yum -y install epel-release \
    && yum -y update \
    && yum -y group install "Development Tools" \
    && yum -y install ca-certificates \
    && yum -y install gcc-c++ git subversion make \
    && yum -y install libcurl-devel libffi-devel libxml2-devel libxslt-devel memcached openldap-devel openssl-devel rpm-build rub-devel rsync subygem-puppet-lint time unzip \
    && yum -y install postgresql94-devel postgres94-contrib postgres94-plperl postgres94-server \
    && yum -y install nodejs npm nodejs-less \
    && yum -y install python-devel python-pip pylint

# Update to pip8
COPY socorro/tools/pipstrap.py /app/socorro/tools/pipstrap.py
RUN python /app/socorro/tools/pipstrap.py

# Install everything--but do it such that we bust the cache if
# requirements.txt files changes
ADD socorro/requirements.txt /app/socorro/requirements.txt
RUN PATH=$PATH:/usr/pgsql-9.4/bin/ pip install --require-hashes -r /app/socorro/requirements.txt

# Copy over the app
ADD socorro /app/socorro/

# FIXME: build stackwalk and put the binaries in the right place; this doesn't
# change much, so we probably want it before the previous ADD. We probably want
# it in its own script that we can call from scripts/bootstrap.sh as well as
# here.

# Run the equivalent of "make dev"
RUN SOCORRO_DEVELOPMENT_ENV=1 \
    cd /app/socorro && python setup.py develop

