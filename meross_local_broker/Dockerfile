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
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    gnupg gpg-agent \
    libdbus-1-dev \
    libffi-dev \
    libglib2.0-0 \
    libglib2.0-dev \
    logrotate \
    nginx \
    openssl \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    sqlite3 \
    python3-flask \
    python3-sqlalchemy \
    python3-paho-mqtt \
    python3-flask-cors \
    python3-expiringdict \
    python3-packaging \
;

RUN pip3 install \
  meross_iot \
  asyncio-mqtt \
  dbus-python \
  debugpy \
;

RUN apt-get clean \
  && rm -fr \
  /etc/nginx \
  /opt/acl \
  /tmp/* \
;

WORKDIR /
COPY rootfs /

RUN chmod +x /usr/local/bin/*.sh
