FROM amazonlinux:2023

RUN yum update -y && \
    yum upgrade -y && \
    yum install -y \
        nginx \
        tar \
        bzip2 && \
        yum clean all

# download retrosheet files
RUN mkdir /webapp
COPY dist.tar.bz2 /webapp
RUN cd /webapp && \
    tar xjvf dist.tar.bz2 && \
    rm dist.tar.bz2

# setup nginx and copy dist 
RUN mkdir /var/www
COPY index.html /var/www
RUN mkdir /var/www/baseball && \
    cp -r /webapp/vite-baseball-stats/dist/* /var/www/baseball &&\
    rm -rf /webapp/vite-baseball-stats

COPY baseball.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx

# in index.html, need to convert absolute (TLD) path '/assets'
# to relative 'assets', otherwise doesn't work through proxy
RUN cd /var/www/baseball && \
    sed 's/\/assets/assets/' index.html > tmp && \
    mv tmp index.html

# NOTE: this doesn't automatically expose port
# need to be exposed with docker run command
EXPOSE 80
