# Using Docker with Revolve2

The following assumes you have already installed: 
* [docker](https://docs.docker.com/engine/install/)
* [docker-compose](https://docs.docker.com/compose/install/linux/)


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