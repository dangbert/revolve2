<img  align="right" width="150" height="150"  src="/docs/source/logo.png">

# Revolve2
Revolve2 is a Python package for optimization, geared towards modular robots and evolutionary computing.
Its primary features are a modular robot framework, wrappers around physics simulators, and evolutionary optimizers.
It consists of multiple smaller python packages and optional supplementary packages that contain varying functionality that is not always required.

## Setup
This repo is meant to be ran on linux and has been tested with python3 3.8.10 (if needed you can use [pyenv](https://realpython.com/intro-to-pyenv/#installing-pyenv) to switch to this version of python).


### Installation
> Note: see also [docker/README.md](./docker/README.md) for the (work in progress) steps to run this repo in docker.

Before running download

````bash
git clone https://github.com/dangbert/revolve2.git
cd revolve2

# create virtual environment
virtualenv env
. env/bin/activate

# install dependencies:
sudo apt install libcereal-dev screen libcairo2-dev pkg-config python3-dev python3-opencv
mkdir -p deps
cd deps
wget https://github.com/ci-group/MultiNEAT/archive/refs/tags/v0.10.tar.gz && tar -xvzf v0.10.tar.gz && pip install MultiNEAT-0.10/

# now download https://developer.nvidia.com/isaac-gym/download
#   and place file in current folder ('deps)
tar -xvzf IsaacGym_Preview_4_Package.tar.gz && pip install isaacgym/python
cd ..

# now test isaac installation with:
#   (more info at deps/isaacgym/docs/install.html)
python3 deps/isaacgym/python/examples/joint_monkey.py

# install revolve2 (from root of this repo)
pip install -e core/ genotypes/cppnwin/ runners/isaacgym/
pip install numpy pycairo opencv-python squaternion scikit-learn colored seaborn statannot greenlet
````

### Run Example Experiment:
````bash
# one time setup:
sudo mkdir -p "/storage/$USER"
sudo chown "$USER:$USER" "/storage/$USER"

# run example experiment:
. env/bin/activate # ensure virtual env is sourced
# note in pyenv 
cd experiments/default_study/
./run-experiments.sh

# note if you get an error about libpython3.8.so.1.0 not found (in the logs), you can try:
# find / -name "libpython3.8*.so" 2>/dev/null # (find file, then update path below)
# export LD_LIBRARY_PATH="/snap/gnome-3-38-2004/112/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH"
````

After the experiment starts you can view the screen sessions with `screen -ls` and join a session with `screen -r <SESSION_NAME>`

You can view the experiment output/logs here: `cd "/storage/$USER/default_study"`

End the experiment: `killall screen`

## Documentation
[ci-group.github.io/revolve2](https://ci-group.github.io/revolve2/)
