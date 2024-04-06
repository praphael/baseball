#!/bin/sh

# start nginx to use as reverse-proxy
nginx 
# start webapp
cd /webapp
python3 app.py -k foo -d
