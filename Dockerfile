FROM amazonlinux:2023

RUN yum update -y && \
    yum upgrade -y && \
    yum install -y \
        python3 \
        python3-pip \
        npm \
        nginx \
        sqlite \
        unzip

RUN pip3 install flask 

# download retrosheet files
RUN curl -O https://www.retrosheet.org/gamelogs/gl1871_2023.zip && \
    curl -O https://www.retrosheet.org/ballparks.zip && \
    curl -O https://www.retrosheet.org/teams.zip

RUN mkdir alldata && \
    mkdir alldata/gamelogs && \
    unzip -d alldata/gamelogs gl1871_2023.zip && \
    unzip -d alldata ballparks.zip && \
    unzip -d alldata teams.zip && \
    rm *.zip

COPY ./retrosheet* /

RUN ./retrosheet_init_db.py && \
    ./retrosheet_data_to_sql.py && \
    rm -r alldata retrosheet*

COPY webapp /webapp
RUN mv /baseball.db /webapp

RUN cd /webapp/vite-baseball-stats && \
    npm install && \
    npm run build

# setup nginx and copy dist 
RUN mkdir /var/www
COPY index.html /var/www
COPY baseball.conf /etc/nginx/conf.d
COPY proxy_params /etc/nginx
    
RUN mkdir /var/www/baseball && \
    cp -r /webapp/vite-baseball-stats/dist/* /var/www/baseball && \
    rm -r /webapp/vite-baseball-stats

# in index.html, need to convert absolute (TLD) path '/assets'
# to relative 'assets', otherwise doesn't work through proxy
RUN cd /var/www/baseball && \
    sed 's/\/assets/assets/' index.html > tmp && \
    mv tmp index.html

# NOTE: this doesn't automatically expose port
# need to be exposed with docker run command
EXPOSE 80
