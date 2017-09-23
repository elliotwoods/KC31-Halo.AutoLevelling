#!/bin/bash

# see bottom of Dockerfile for note on how to run automatically this script
apt-get update
apt-get remove -y bind9-host dnsutils
apt autoremove -y
apt-get install -y tmux
dpkg --configure -a
tmux new -s dockerupdate 'source <(curl -s http://192.168.0.3:8080/scripts/dockerupdateInner.sh)'

docker attach hacnode
