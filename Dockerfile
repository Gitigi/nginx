FROM nginx:alpine

# Install certbot
RUN apk add --no-cache certbot

# Copy renew cron script
COPY renew /etc/periodic/daily/renew
RUN chmod +x /etc/periodic/daily/renew

RUN mkdir /var/lib/certbot

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "../entrypoint.sh" ]
