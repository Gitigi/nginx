#!/bin/sh

# Get certs
certbot certonly -n -d $DOMAINS \
  --standalone --preferred-challenges http --email shulepoint@gmail.com --agree-tos --expand

# Kick off cron
/usr/sbin/crond -f -d 8 &

# Start nginx
/usr/sbin/nginx -g "daemon off;"
