FROM ubuntu:18.04
MAINTAINER support@charm-crypto.com

RUN apt update && apt install --yes build-essential flex bison wget subversion m4 python3 python3-dev python3-setuptools libgmp-dev libssl-dev
RUN wget https://crypto.stanford.edu/pbc/files/pbc-1.0.0.tar.gz && tar xvf pbc-1.0.0.tar.gz && cd /pbc-1.0.0 && ./configure LDFLAGS="-lgmp" && make && make install && ldconfig
COPY . /charm
RUN cd /charm && ./configure.sh && make && make install && ldconfig
