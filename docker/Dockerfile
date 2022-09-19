#### target for building flask backend container: ####
#  https://registry.hub.docker.com/_/python/
FROM python:3.8.10-slim as base

# need a c compiler for certain pip packages:
RUN apt-get update && apt-get install -y g++ wget libboost-all-dev
RUN pip install --upgrade pip

RUN mkdir -p /tmp/deps
WORKDIR /tmp/deps

# revolve2 needs the ci-group version of MultiNEAT
#   https://github.com/ci-group/MultiNEAT
#   (note this package is called 'multineat' in python, whereas the official package is called 'MultiNEAT')
RUN apt install -y cmake #libcereal-dev
RUN wget -qO /usr/local/bin/ninja.gz https://github.com/ninja-build/ninja/releases/latest/download/ninja-linux.zip && \
  gunzip /usr/local/bin/ninja.gz && chmod a+x /usr/local/bin/ninja
RUN wget https://github.com/USCiLab/cereal/archive/refs/tags/v1.3.2.tar.gz && \
  tar -xvzf v1.3.2.tar.gz && mv cereal-1.3.2/include/cereal /usr/include/cereal

RUN wget https://github.com/ci-group/MultiNEAT/archive/refs/tags/v0.10.tar.gz && \
  tar -xvzf v0.10.tar.gz && cd MultiNEAT-0.10/ && pip install .


# commented this section out as I think it's only needed for installing the offical version of MultiNEAT:
## needed by boost python:
##   https://github.com/stefanseefeld/faber
#RUN wget https://github.com/stefanseefeld/faber/archive/refs/tags/release/0.6.0.dev1.tar.gz && \
#  tar -xvzf 0.6.0.dev1.tar.gz && cd faber-release-0.6.0.dev1/ && python setup.py install
#
## libboost-all-dev only supports up to python3.7, so we build from source:
##   https://github.com/boostorg/python
#RUN pip3 install numpy
#RUN wget https://github.com/boostorg/python/archive/refs/tags/boost-1.80.0.tar.gz && \
#  tar -xvzf boost-1.80.0.tar.gz && cd python-boost-1.80.0/ && \
#  faber && cp src/g++-8/x86_64/shared/libboost_python38.so src/g++-8/x86_64/shared/libboost_numpy38.so /usr/lib/x86_64-linux-gnu/ && ldconfig
#
## official version of MultiNEAT:
##   https://github.com/MultiNEAT/MultiNEAT
#RUN pip install psutil
#RUN wget https://github.com/MultiNEAT/MultiNEAT/archive/refs/tags/release/0.5.2.tar.gz && \
#  tar -xvzf 0.5.2.tar.gz && cd MultiNEAT-release-0.5.2 && \
#  python setup.py build_ext && python setup.py install

WORKDIR /revolve2
# misc packages needed by revolve2:
RUN apt install -y libcairo2-dev pkg-config python3-dev python3-opencv
RUN pip install numpy pycairo opencv-python squaternion scikit-learn colored seaborn statannot greenlet
#   (git needed for cppnwin below)
RUN apt install -y git
# efficiently cache the install of core/
COPY ./core ./core
COPY ./actor_controller ./actor_controller
COPY ./serialization ./serialization
RUN pip install -e ./core

# copy rest of code
COPY ./ /revolve2
# https://ci-group.github.io/revolve2/installation/genotypes/cppnwin.html
RUN pip install -e genotypes/cppnwin/

# final cleanup
RUN rm -rf /tmp/deps

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

CMD /bin/bash

# this image contains the IsaacGym
#FROM base as Isaac
#RUN mkdir -p /tmp/deps
#WORKDIR /tmp/deps
## install nVidia driver
#COPY ./docker/lib/NVIDIA-Linux-x86_64-410.72.run .
#RUN bash NVIDIA-Linux-x86_64-410.72.run
## install CUDA
##   https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local
#RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin && \
#  mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
#  wget https://developer.download.nvidia.com/compute/cuda/11.7.1/local_installers/cuda-repo-ubuntu2204-11-7-local_11.7.1-515.65.01-1_amd64.deb && \
#  dpkg -i cuda-repo-ubuntu2204-11-7-local_11.7.1-515.65.01-1_amd64.deb && \
#  cp /var/cuda-repo-ubuntu2204-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/cp /var/cuda-repo-ubuntu2204-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/ && \
#  apt update && apt install -y cuda
#
## install IsaacGym (must be donwloaded locally already)
##   https://developer.nvidia.com/isaac-gym/download
