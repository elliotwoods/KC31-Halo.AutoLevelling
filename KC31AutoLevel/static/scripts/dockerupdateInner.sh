#!/bin/bash

echo "Cleaning existing docker images"
echo "-------------------------------"
echo ""

docker stop halo.node
docker rm halo.node
docker stop hacnode
docker rm hacnode

echo ""

echo "Setting up docker"
echo "-----------------"
echo ""

curl http://192.168.0.3:8080/scripts/docker_hosts.conf > /etc/systemd/system/docker.service.d/hosts.conf
curl http://192.168.0.3:8080/scripts/docker_daemon.json > /etc/docker/daemon.json
echo "Restarting..."
systemctl daemon-reload
sudo service docker restart

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