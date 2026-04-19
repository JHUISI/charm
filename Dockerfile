FROM ubuntu:22.04
LABEL maintainer="jakinye3@jhu.edu"

RUN apt-get update && apt-get install --yes --no-install-recommends \
    build-essential flex bison wget subversion m4 python3 python3-dev \
    python3-setuptools libgmp-dev libssl-dev libntl-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download PBC library over HTTPS and verify checksum
RUN wget --no-verbose https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz \
    && echo "772527404117587560080241cedaf441e5cac3269009cdde4c588a1dce4c73a6  pbc-0.5.14.tar.gz" | sha256sum -c - \
    && tar xzf pbc-0.5.14.tar.gz \
    && cd /pbc-0.5.14 \
    && ./configure LDFLAGS="-lgmp" \
    && make && make install && ldconfig \
    && cd / && rm -rf pbc-0.5.14 pbc-0.5.14.tar.gz

COPY . /charm
RUN cd /charm && ./configure.sh --enable-lattice && make && make install && ldconfig
