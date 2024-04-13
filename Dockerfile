FROM amazonlinux:2023

RUN yum update -y && \
    yum upgrade -y && \
    yum install -y \
        nginx \
        tar \
        bzip2 && \
        yum clean all

# make directories        
RUN mkdir /webapp && \
    mkdir /var/www && \
    mkdir /var/www/baseball

# copy files
COPY index.html /var/www
COPY dist.tar.bz2 /webapp
COPY baseball.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx

# setup - extrac tar archive
# in index.html, need to convert absolute (TLD) path '/assets'
# to relative 'assets', otherwise doesn't work through proxy
RUN cd /webapp && \
    tar xjvf dist.tar.bz2 && \
    rm dist.tar.bz2 && \
    cp -r /webapp/dist/* /var/www/baseball && \
    rm -rf /webapp/dist && \
    cd /var/www/baseball && \
    sed -i 's/\/assets/assets/' index.html

# NOTE: this doesn't automatically expose port
# need to be exposed with docker run command
EXPOSE 80
