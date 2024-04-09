#!/bin/sh

sudo docker build . -f Dockerfile.build_all -t bb:stats_build
id=$(sudo docker create bb:stats_build) && \
  sudo docker cp $id:/baseball/webapp/dist.tar.bz2 . && \
  sudo docker rm -v $id && \
  sudo docker build . -f Dockerfile -t bb:stats_srv
