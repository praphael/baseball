#!/bin/bash

ARG=bar   # to force docker rebuild before it copies system files
docker build . -f Dockerfile.build_all -t bb:stats_build;
r=$?; echo "r=$r"
if [[ $r == 0 ]]; then
  id=$(docker create bb:stats_build) && \
  docker cp $id:/baseball/webapp/dist.tar.bz2 . && \
  docker rm -v $id && \
  docker build . -f Dockerfile -t praphael/baseball:stats_dist;
  docker push praphael/baseball:stats_dist
else
  echo "Docker build failed, cannot generate distribution image";
fi
