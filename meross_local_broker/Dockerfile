ARG BUILD_FROM
FROM $BUILD_FROM

# Build arguments
ARG BUILD_ARCH

# Versions
ENV HIVEMQ='b2043e7fcbd5897a3799869d42c6202122221fbc' \
  LIBWEBSOCKETS='3.1.0' \
  GOVERSION=1.16.4

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
  git \
  cmake \
  libssl-dev \
  libffi-dev \
  python3-dev \
  dbus \
  bash \
  sqlite \
  curl \
  socat \
  openssl \
  python3 \
  python3-setuptools \
  python3-pip \
  nginx \
  software-properties-common \
  xsltproc \
  logrotate \
  libglib2.0-0 \
  libglib2.0-dev \
  libdbus-1-dev \
  && pip3 install wheel

# Setup GO source # export GOARM=7 ;
RUN mkdir -p /tmp/go \
  && export GOOS=linux \
  && if [ "${BUILD_ARCH}" = "armhf" ]; then \
    export GOBIN_GOARCH=armv6l ; \
    export GOARCH=arm ; \
    export GOARM=6 ; \
    ln -s /lib/ld-linux.so.3 /lib/ld-linux-armhf.so.3 ; \
  elif [ "${BUILD_ARCH}" = "armv7" ]; then \
    export GOBIN_GOARCH=armv6l ; \
    export GOARCH=arm ; \
    export GOARM=7 ; \
  elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
    export GOBIN_GOARCH=arm64 ; \
    export GOARCH=arm64 ; \
  elif [ "${BUILD_ARCH}" = "i386" ]; then \
    export GOBIN_GOARCH=386 ; \
    export GOARCH=386 ; \
  elif [ "${BUILD_ARCH}" = "amd64" ]; then \
    export GOBIN_GOARCH=amd64 ; \
    export GOARCH=amd64 ; \
  else \
    echo 'NOT VALID BUILD'; exit 1; \
  fi \
  && curl https://dl.google.com/go/go${GOVERSION}.${GOOS}-${GOBIN_GOARCH}.tar.gz --output /tmp/go/go.tar.gz \
  && tar -C /usr/local -xzf /tmp/go/go.tar.gz \
  && export PATH=$PATH:/usr/local/go/bin \
  && git clone --branch "v${LIBWEBSOCKETS}" --depth=1 https://github.com/warmcat/libwebsockets.git /tmp/libwebsockets \
  && mkdir -p /tmp/libwebsockets/build \
  && cd /tmp/libwebsockets/build \
  && cmake .. \
  -DCMAKE_BUILD_TYPE=MinSizeRel \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DLWS_IPV6=OFF \
  -DLWS_WITHOUT_BUILTIN_GETIFADDRS=ON \
  -DLWS_WITHOUT_CLIENT=ON \
  -DLWS_WITHOUT_EXTENSIONS=ON \
  -DLWS_WITHOUT_TESTAPPS=ON \
  -DLWS_WITH_SHARED=OFF \
  -DLWS_WITH_ZIP_FOPS=OFF \
  -DLWS_WITH_ZLIB=OFF \
  && make \
  && make install \
  && apt-get clean \
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
