#!/bin/sh

docker stop $(docker ps -a -q)
docker rm $(docker ps -aq)
#docker rmi $(docker images -q)
