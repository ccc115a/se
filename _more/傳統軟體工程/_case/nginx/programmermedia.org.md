root@localhost:~# cat /etc/nginx/sites-enabled/programmermedia.org

server {
        listen 443 ssl;
        server_name programmermedia.org;

        ssl_certificate /etc/letsencrypt/live/programmermedia.org/cert.pem;
        ssl_certificate_key /etc/letsencrypt/live/programmermedia.org/privkey.pem;

        location / {
            proxy_pass http://127.0.0.1:80/;
        }
}