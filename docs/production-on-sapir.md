Production on Sapir
-------------------

As of <time datetime="2021-01-05">January 5, 2021</time>, the itwêwina
is deployed on a server called **Sapir**. You can visit the
production website here:

<https://sapir.artsrn.ualberta.ca/cree-dictionary>


It was supposed to be deprecated in 2020 and decommissions in 2021, but
here we are :/

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

 1. Pull the code on Sapir, somewhere in `/opt`.

 2. Make sure the folder is owned by User `www-data` and group `www-data`.
    This is the user that Apache is running under!

The following commands will probably require the following prefix:

    # sudo -u www-data env HOME=/tmp PIPENV_VENV_IN_PROJECT=1

 - `env` sets environment variables before running a command
 - `HOME=/tmp` allows npm and pip/pipenv to cache things in the "home"
   directory; since the home directory while `sudo`'d is `/root`, set it
   to `/tmp` so there are no write errors or permission errors!
 - `PIPENV_VENV_IN_PROJECT=1` makes sure the virtual environment is
   stored in the project folder in a subdirectory called `.venv`

3. Create the virtual environment:

    This creates `.venv` folder under current directory. Without the
    environment variable pipenv will create virtual environment under
    the users home, which causes permission issues.

        pipenv run pip install mod_wsgi

4. Install Gunicorn, (or any WSGI server, really):

        pipenv run install-server

5. Collect static files

        pipenv run collect-static

6. Copy the database

   You should copy it `CreeDictionary/` within the repo to
   `db.sqlite3`.

7. Configure environment variables

I set up logs to write to `/var/log/cree-dictionary`, so you'll want to
create the folders appropriately:

   # sudo mkdir /var/log/cree-dictionary
   # sudo chown www-data-:www-data /var/log/cree-dictionary

8. Now try the server!

   This should start a server:

        pipenv run gunicorn-locally

Make sure it responds to requests!

        curl -i localhost:8000/

This should return a bunch of HTML with a 200 success code.

**Note**: static file hosting will not work, as that the static file
hosting is disabled when `DEBUG` is unset or `False`.


8. Create a service file `/etc/systemd/system/cree-dictionary.service` with the following content

    ```
    # Inspired by: https://docs.gunicorn.org/en/stable/deploy.html#systemd
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
        --config CreeDictionary/CreeDictionary/gunicorn.conf.py \
        CreeDictionary.wsgi:application
    # Gunicorn will reload if the main process is sent SIGHUP
    ExecReload=/bin/kill -s HUP $MAINPID
    KillMode=mixed
    TimeoutStopSec=10

    [Install]
    WantedBy=multi-user.target
    ```

9. Enable the socket

       # sudo systemctl enable cree-dictionary.service

10. Test the socket:

   Through some systemd magic that I do not understand, accessing the
   socket starts up the service. Try out the socket pretending you are
   `www-data`:

       # sudo -u www-data curl -v --unix-socket /run/cree-dictionary-python-3.9.socket -H'Host: sapir.artsrn.ualberta.ca' http:/cree-dictionary/

You should get the same HTML response with status code 200 like before.

TODO: write systemd stuff

TODO: write apache stuff


- Have a `cree-dictionary.conf` with the following content under `etc/apache2/sites-available/`

    ```.conf
    # Add a trailing slash if it's missing.
    RedirectMatch 301 "^/cree-dictionary$"  "/cree-dictionary/"


    # A proxy for the cree-dictionary service, "sudo systemctl status cree-dictionary"
    ProxyPreserveHost On
    ProxyPass /cree-dictionary/ http://0.0.0.0:8091/cree-dictionary/
    ProxyPassReverse /cree-dictionary/ http://0.0.0.0:8091/cree-dictionary/
    ```

- `sudo a2ensite cree-dictionary`

# `RUNNING_ON_SAPIR` setting and environment variable

This setting is `True` when the app detects it's running on Sapir during
startup. You can also force this setting by doing setting the
environment variable to `True`.

This settings enables certain "features" (read: hacks) required for
running the application properly on Sapir. These features are not
required in other production scenarios.
