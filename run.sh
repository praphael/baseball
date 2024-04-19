#!/bin/bash

id=$(sudo docker run -p 5000:5000 -w /webapp praphael/baseball:bb_stats_dist ./httpd 1903 2022 0.0.0.0 5000 . 2)
#  This version runs nginx inside the container
#  id=$(sudo docker run -p 80:80 -w /webapp bb:stats_dist ./httpd 1903 2022 127.0.0.1 5000 . 2)
#    && sudo docker exec ${id} nginx &


