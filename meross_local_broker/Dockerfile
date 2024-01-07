ARG BUILD_FROM
FROM $BUILD_FROM

# Build arguments
ARG BUILD_ARCH

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set workdir
WORKDIR /usr/src

# Install base dependencies
# hadolint ignore=DL3003
RUN apt-get update \
  && apt-get install --no-install-recommends -y gnupg gpg-agent \
  && apt-get --no-install-recommends install -y \
  build-essential \
  libffi-dev \
  python3-dev \
  bash \
  sqlite \
  openssl \
  python3 \
  python3-setuptools \
  python3-pip \
  nginx \
  logrotate \
  libglib2.0-0 \
  libglib2.0-dev \
  libdbus-1-dev \
  && pip3 install wheel

# Setup GO source # export GOARM=7 ;
RUN apt-get clean \
  && rm -fr \
  /etc/nginx \
  /opt/acl \
  /tmp/*

# Copy the requirements.txt file and install the listed packages
COPY rootfs/opt/custom_broker/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /
COPY rootfs /

RUN chmod +x /usr/local/bin/*.sh
