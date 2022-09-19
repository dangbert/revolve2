# Using Docker with Revolve2

The following assumes you have already installed: 
* [docker](https://docs.docker.com/engine/install/)
* [docker-compose](https://docs.docker.com/compose/install/linux/)

Also you must download the following into the docker/lib folder:

* `IsaacGym_Preview_4_Package.tar.gz`, [download here](https://developer.nvidia.com/isaac-gym/download)


````bash
# building image:
cd docker/
sudo docker-compose build

# start container:
sudo docker-compose up -d
# enter container and run whatever you like:
sudo docker exec -it revolve2_main_1 bash

# stop container:
sudo docker-compose down
````

Note: once the docker container is running, your local code should be mounted at `/revolve2`

## Depedencies:
* [nVidia IsaacGym](https://developer.nvidia.com/isaac-gym)
* [nVidia CUDA driver](https://developer.nvidia.com/cuda-downloads?target_os=Linux)

## Deploy docker on remote server:

````bash
# on local machine export docker after building (if you don't want to build on server):
sudo docker image save revolve2_main:latest -o "rev2--$(date +"%m%d%y").tar"
scp rev2*.tar gpu:/mnt/ssd/revolve2/docker

# on server in desired directory:
cd /mnt/ssd/revolve2
git clone https://github.com/dangbert/revolve2.git
#git checkout --track origin/setup-docker
# ...
cd docker
sudo docker-compose build
````
