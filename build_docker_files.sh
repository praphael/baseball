#!/bin/bash

ARG=bar   # to force docker rebuild before it copies system files
docker build . -f Dockerfile.build_front_back -t bb:stats_front_back;
docker build . -f Dockerfile.build_db -t bb:stats_db;

r=$?; echo "r=$r"
if [[ $r == 0 ]]; then
  id=$(docker create bb:stats_front_back) && \
  docker cp $id:/baseball/webapp/dist.tar.bz2 . && \
  docker rm -v $id && \
  id=$(docker create bb:stats_db) && \
  docker cp $id:/baseball/baseball.bz2 . && \
  docker build . -f Dockerfile -t praphael/baseball:stats_dist;
  docker push praphael/baseball:stats_dist
else
  echo "Docker build failed, cannot generate distribution image";
fi
