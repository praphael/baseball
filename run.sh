#!/bin/bash

id=$(sudo docker run -p 80:80 -w /webapp bb:stats_srv ./httpd 127.0.0.1 5000 . 2) && \
    sudo docker exec ${id} nginx &


