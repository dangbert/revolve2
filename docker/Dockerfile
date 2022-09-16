#### target for building flask backend container: ####
#  https://registry.hub.docker.com/_/python/
FROM python:3.8.10-slim as base

# need a c compiler for certain pip packages:
RUN apt-get update && apt-get install -y g++ wget libboost-all-dev
RUN pip install --upgrade pip

RUN mkdir -p /tmp/deps
WORKDIR /tmp/deps

# needed by boost python:
#   https://github.com/stefanseefeld/faber
RUN wget https://github.com/stefanseefeld/faber/archive/refs/tags/release/0.6.0.dev1.tar.gz && \
  tar -xvzf 0.6.0.dev1.tar.gz && cd faber-release-0.6.0.dev1/ && python setup.py install

# libboost-all-dev only supports up to python3.7, so we build from source:
#   https://github.com/boostorg/python
RUN pip3 install numpy
RUN wget https://github.com/boostorg/python/archive/refs/tags/boost-1.80.0.tar.gz && \
  tar -xvzf boost-1.80.0.tar.gz && cd python-boost-1.80.0/ && \
  faber && cp src/g++-8/x86_64/shared/libboost_*.so /usr/lib/x86_64-linux-gnu/ && ldconfig

# revolve2 needs MultiNEAT:
#   https://github.com/MultiNEAT/MultiNEAT
RUN pip install psutil
RUN wget https://github.com/MultiNEAT/MultiNEAT/archive/refs/tags/release/0.5.2.tar.gz && \
  tar -xvzf 0.5.2.tar.gz && cd MultiNEAT-release-0.5.2 && \
  python setup.py build_ext && python setup.py install

WORKDIR /revolve2
# efficiently cache the install of core/
COPY ./core ./core
COPY ./actor_controller ./actor_controller
COPY ./serialization ./serialization
RUN pip install -e ./core

# copy rest of code
COPY ./ /revolve2

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

CMD /bin/bash