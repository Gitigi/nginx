base = '''
    upstream django {
        #[%
            server unix:/var/run/dummy.sock; # dummy socket to prevent nginx from stopping
        #%]
    }
'''

port80 = '''
    server {
        listen      80 default_server;
        server_name 0.0.0.0;
        charset     utf-8;
        sendfile        on;
        gzip  on;
        server_tokens off;
        client_max_body_size 75M;
        
        location /media  {
            alias /etc/static/media;
        }
        
        location /static {
            alias /etc/static;
        }
        
        location / {
            uwsgi_pass  django;
            include     /etc/nginx/uwsgi_params;
        }
    }

'''

port80_443 = '''
    server {
        listen       80;
        server_name  0.0.0.0;
        rewrite ^ https://$http_host$request_uri? permanent;    # force redirect http to https
    }
'''

port443 = '''
    server {
        listen      443 default_server;
        ssl on;
        server_name 0.0.0.0;
        charset     utf-8;
        sendfile        on;
        gzip  on;
        
        ssl_certificate     /usr/src/cacert.crt;
        ssl_certificate_key /usr/src/cacert.key;

        client_max_body_size 75M;
        
        ssl_session_timeout 5m;
        ssl_session_cache shared:SSL:5m;

        # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
        ssl_dhparam /etc/nginx/dhparam.pem;

        # secure settings (A+ at SSL Labs ssltest at time of writing)
        # see https://wiki.mozilla.org/Security/Server_Side_TLS#Nginx
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:DHE-RSA-CAMELLIA256-SHA:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-SEED-SHA:DHE-RSA-CAMELLIA128-SHA:HIGH:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS';
        ssl_prefer_server_ciphers on;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        server_tokens off;

        
        location /media  {
            alias /etc/static/media;
        }
        
        location /static {
            alias /etc/static;
        }
        
        location / {
            uwsgi_pass  django;
            include     /etc/nginx/uwsgi_params;
        }
    }

'''

import os

if os.environ.get('force-https') is not None:
    base += '\n' + port80_443
else:
    base += '\n' + port80

if os.environ.get('certificate') is not None and os.environ.get('certificate_key') is not None:
    with open('/usr/src/cacert.crt','w') as c:
        c.write(os.environ.get('certificate').replace('\\n','\n'))
        
    with open('/usr/src/cacert.key','w') as k:
        k.write(os.environ.get('certificate_key').replace('\\n','\n'))
        
    base +='\n' + port443

with open('/etc/nginx/conf.d/default.conf', 'w') as conf:
    conf.write(base)

print(base)