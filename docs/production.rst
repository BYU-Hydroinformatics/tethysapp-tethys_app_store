========================
Production Installation
========================

On a production server, ensure that you set the custom settings which require the SUDO password to the server user that has the ability to restart the Tethys Process. Usually this is the same as the user you used to setup Tethys. The password is stored in a Database and is only used when we need to restart the server after installing an application so that the changes can be seen. 

Also, in case the Tethys portal is run within a Docker container, we need to ensure that the proxy setup on the host machine to forward Tethys requests to the Docker container supports Websockets as well. A working example is here:

.. code-block::

    # top-level http config for websocket headers
    # If Upgrade is defined, Connection = upgrade
    # If Upgrade is empty, Connection = close
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }


    server {
        listen 8008 default_server;
        listen [::]:8008 default_server ipv6only=on;


    location /tethys {
                rewrite ^/tethys/(.*)$ /$1 break;
                proxy_pass http://127.0.0.1:8006$uri$is_args$args;
                proxy_set_header Host $host;
                proxy_set_header X-Script-Name /tethys;
                proxy_cookie_path / /tethys;

                #WEBSOCKET Support
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection $connection_upgrade;
            }

    }


