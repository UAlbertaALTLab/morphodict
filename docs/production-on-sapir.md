Production on Sapir
-------------------

As of <time datetime="2019-11-18">November 18, 2019</time>, the Cree
Dictionary is deployed on a server called **Sapir**. You can visit the
production website here:

<https://sapir.artsrn.ualberta.ca/cree-dictionary>


## Redeployment Script

`.travis.yml` is configured so that, after a successful build on master,
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


## Limit of `redeploy`

`redeploy` does not sync the database file. To make changes to the database, we need to sync our database file, which is
guaranteed to work as SQLite database and is operating system independent.

When you want to make changes to the database, do a `$ pipenv run pull-db` first to pull database from Sapir.

Just make sure your user is in `www-data` group on Sapir so that www-data on Sapir has access to the uploaded database.
If your username on Sapir is different from your username on you local
machine, add environment variable `SAPIR_USER=<your name>` in `.env` file.

It has admin authentication information stored and shouldn't be
overwritten. And it probably has edited tables. After the changes, do
 `$ pipenv run push-db` to upload the changed database back to Sapir


## Set up

This only needs to be done once and is probably already done. This serves for documentation purpose.

- pull the code
- `sudo PIPENV_VENV_IN_PROJECT=1 pipenv install`

    This creates `.venv` folder under current directory. Without the environment variable pipenv will create virtual
    environment under the users home, which causes permission issues.

- `sudo pipenv run pip install mod_wsgi`

    DO NOT use `pipenv install`. mod_wsgi is used on sapir only to serve the application

- setup mod_wsgi

    ```.bash
    $ sudo pipenv run python CreeDictionary/manage.py runmodwsgi --setup-only --port=8091 --user www-data --group www-data --server-root=mod_wsgi-express-8091
    ```

    this creates folder `mod_wsgi-express-8091`, which contains a separate apache to serve the application.

- Create a service file `/etc/systemd/system/cree-dictionary.service` with the following content

    ```
    [Unit]
    Description=Cree Dictionary HTTP service

    [Service]
    Type=forking
    EnvironmentFile=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/envvars
    PIDFile=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/httpd.pid
    ExecStart=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl start
    ExecReload=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl graceful
    ExecStop=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl stop
    KillSignal=SIGCONT
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target
    ```

- `sudo pipenv run collect-static`

- `sudo systemctl enable cree-dictionary.service`

- `sudo mkdir CreeDictionary/res/dictionaries`

- `cd .. && sudo chown -R www-data:www-data cree-intelligent-dictionary/`


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
