Production on Sapir
-------------------

Before <time datetime="2021-01-05">February 12, 2021</time>, itwêwina
was deployed on a server called **Sapir**. It used to be located here:

<https://sapir.artsrn.ualberta.ca/cree-dictionary>


## Redeployment Script

`.github/workflows/test-and-deploy.yml` is configured so that,
after a successful build on master,
Sapir will execute a script that updates and restarts the app. This is
enabled by a tool `redeploy`, maintained by
[Eddie](https://github.com/eddieantonio).

The script does the following in sequence:

   - pull the code
   - npm install
   - npm run build (using [Rollup](https://rollupjs.org/guide/en/))
   - `pipenv install` to update dependencies
   - collect static
   - touch `wsgi.py` to restart service

- to change the script

    `vim scp://sapir.artsrn.ualberta.ca//opt/redeploy/redeploy/cree-dictionary`  (it's a Python file without extension)

- to know details of how redeployment works, check the [repository of redeploy](https://github.com/eddieantonio/redeploy)


## Limits of `redeploy`

`redeploy` does not sync the database file. To make changes to the database, we need to sync our database file, which is
guaranteed to work as SQLite database and is operating system independent.

 > ⚠️ Ask Eddie how database updates are done. It's really bad and
 > shameful.

## Set up

This only needs to be done once and is probably already done. This serves for documentation purpose.

### Clone the code on Sapir

Clone it to somewhere in `/opt` which is actually a symlink to `/data/texts/opt`.

I've chosen `/data/texts/opt/cree-intelligent-dictionary-python-3.9`
because `/data/texts/opt/cree-intelligent-dictionary` is being used by
the old install.

### Make sure it has the correct owner and access rights

Make sure the folder is owned by user `www-data` and group `www-data`.
This is the user that Apache/the server is running under!


```sh
sudo chown www-data:www-data /data/texts/opt/cree-intelligent-dictionary-python-3.9
```

The following commands will probably require the following prefix:

```sh
# sudo -u www-data env HOME=/tmp PIPENV_VENV_IN_PROJECT=1
```

 - `env` sets environment variables before running a command
 - `HOME=/tmp` allows npm and pip/pipenv to cache things in the "home"
   directory; since the home directory while `sudo`'d is `/root`, set it
   to `/tmp` so there are no write errors or permission errors!
 - `PIPENV_VENV_IN_PROJECT=1` makes sure the virtual environment is
   stored in the project folder in a subdirectory called `.venv`

## Create the virtual environment:

This creates `.venv` folder under current directory. Without the
environment variable pipenv will create virtual environment under the
users home, which causes permission issues.

```sh
sudo -u www-data env HOME=/tmp PIPENV_VENV_IN_PROJECT=1 pipenv install
```

### Collect static files

You NEED to `collect-static` because the server will crash on startup
otherwise.

```
sudo -u www-data env HOME=/tmp PIPENV_VENV_IN_PROJECT=1 pipenv run collect-static
```

### Copy the database

You should copy the database file to `CreeDictionary/db.sqlite3`.

### Setup logging

I set up logs to write to `/var/log/cree-dictionary`, so you'll want to
create the folders appropriately:

   # mkdir /var/log/cree-dictionary
   # chown www-data:www-data /var/log/cree-dictionary

If you want to configure logging, see `gunicorn.conf.py`!


### Now try the server!

This should start a server:

    # sudo -u www-data .venv/bin/gunicorn CreeDictionary.wsgi

Make sure it responds to requests!

    $ curl -i localhost:8000/

This should return a bunch of HTML with a 200 success code.

**Note**: static file hosting will not work, as that the static file
hosting is disabled when `DEBUG` is unset or `False`.

### Create the systemd configuration

According to [Gunicorn's docs](https://docs.gunicorn.org/en/stable/deploy.html#systemd),
you'll need two unit files: one for the Unix domain socket, and one for
the actual service proper.

Create the unit file for the socket:

```systemd
# /etc/systemd/system/cree-dictionary-python-3.9.socket
[Unit]
Description=Cree Dictionary (gunicorn) socket

[Socket]
ListenStream=/run/cree-dictionary-python-3.9.socket
User=www-data

[Install]
WantedBy=sockets.target
```

Create the unit file for the service:

```systemd
# /etc/systemd/system/cree-dictionary-python-3.9.service
[Unit]
Description=Cree Intelligent Dictionary (gunicorn)
Requires=cree-dictionary-python-3.9.socket
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=cree-dictionary
WorkingDirectory=/data/texts/opt/cree-intelligent-dictionary-python-3.9/
ExecStart=/data/texts/opt/cree-intelligent-dictionary-python-3.9/.venv/bin/gunicorn \
    --config gunicorn.conf.py \
    CreeDictionary.wsgi:application
# Gunicorn will reload if the main process is sent SIGHUP
ExecReload=/bin/kill -s HUP $MAINPID
# Sends SIGTERM to gunicorn and SIGKILL to child processes if there are
# unruly child processes
# See: https://www.freedesktop.org/software/systemd/man/systemd.kill.html#KillMode=
KillMode=mixed
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
```

### Reload systemd

In order for systemd to acknowledge your changes to the unit files, you
need to reload it:

    # systemctl daemon-reload

### Enable the socket

Enabling the socket permanently requires the socket AND service to start
on boot:

    # sudo systemctl enable cree-dictionary.service

### Test the socket:

Through some systemd magic that I do not understand, accessing the
socket starts up the service. Try out the socket pretending you are
`www-data`:

    # sudo -u www-data curl -v --unix-socket /run/cree-dictionary-python-3.9.socket -H'Host: sapir.artsrn.ualberta.ca' http:/cree-dictionary/

You should get the same HTML response with status code 200 like before.

### Write the Apache config

Write an Apache config file at
`/etc/apache2/sites-available/cree-dictionary-python-3.9.conf`. It will
need to setup the reverse proxy, reverse proxy exception, and static
file hosting. It will have to have the following at minimum:

```conf
# Add a trailing slash if it's missing.
RedirectMatch 301 "^/cree-dictionary$"  "/cree-dictionary/"


# Proxy to the Cree Intelligent Dictionary (itwêwina) service (Gunicorn/Python 3.9)
ProxyPreserveHost On
# Do not proxy /static/:
ProxyPass        "/cree-dictionary/static" !
ProxyPass        /cree-dictionary/ unix:/run/cree-dictionary-python-3.9.socket|http://sapir.artsrn.ualberta.ca/cree-dictionary/
ProxyPassReverse /cree-dictionary/ unix:/run/cree-dictionary-python-3.9.socket|http://sapir.artsrn.ualberta.ca/cree-dictionary/

Alias "/cree-dictionary/static" "/data/texts/opt/cree-intelligent-dictionary-python-3.9/CreeDictionary/static"
<Directory "/data/texts/opt/cree-intelligent-dictionary-python-3.9/CreeDictionary/static">
    AllowOverride None
    Require all granted
</Directory>
```

Then you can enable the site with this command:

    # a2ensite cree-dictionary-python-3.9

Test out the config by using this command:

    # apachectl -t

It should say `Syntax OK`

### Reload Apache

    # service apache2 reload

Then try it!

    $ curl  https://sapir.artsrn.ualberta.ca/cree-dictionary/

(should return an HTML page with status 200)
