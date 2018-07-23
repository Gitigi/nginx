FROM nginx:1.12-alpine

RUN apk add --update python3 py3-pip
RUN pip3 install docker-py

COPY dhparam.pem /etc/nginx/dhparam.pem
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY monitor.py /usr/src
COPY run.sh /usr/src
COPY generate_configuration.py /usr/src


CMD sh /usr/src/run.sh
