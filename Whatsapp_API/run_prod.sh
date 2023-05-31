# --forwarded-allow-ips='*' to allow NGINX to forward requests
# --proxy-headers to correctly handle X-Forwarded-For, X-Forwarded-Proto, etc.
# gunicorn -w 3 --forwarded-allow-ips="10.170.3.217,10.170.3.220" test:app

gunicorn main:app -c ./config_files/gunicorn.conf.py