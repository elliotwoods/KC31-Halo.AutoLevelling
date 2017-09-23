#!/bin/bash

echo "Cleaning existing docker images"
echo "-------------------------------"
echo ""

docker stop halo.node
docker rm halo.node
docker stop hacnode
docker rm hacnode

echo ""

echo "Purging docker"
echo "--------------"
echo ""

docker container prune --force

echo ""

echo "Updating docker image"
echo "---------------------"
echo ""

docker pull 192.168.0.3:1000/kc31-node
docker inspect -f '{{json .Created }}' 192.168.0.3:1000/kc31-node:latest > ~/dockerImageInfo.json

echo ""

echo "Running docker image"
echo "--------------------"
echo ""

docker run --name hacnode -d -it -v ~:/mnt --privileged --restart unless-stopped --network=host 192.168.0.3:1000/kc31-node