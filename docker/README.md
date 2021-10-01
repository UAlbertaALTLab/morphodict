# Docker for morphodict

The morphodict dictionaries are deployed on a single host with docker-compose.

Here's how it works!

## Quick summary

This `docker-compose.yml` is intended to run on production. Once set up:

    $ ssh itw.altlab.dev
    $ sudo -i -u morphodict
    $ cd ~/morphodict/docker

    # Runs production by default:
    docker-compose up -d

The containers will expose **ports like 8010** to the machine. See
the [application registry] and [docker/helper/settings.py].

[application registry]: https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv
[docker/helper/settings.py]: https://github.com/UAlbertaALTLab/morphodict/blob/main/docker/helpers/settings.py

## Development

We don’t currently have a docker setup intended for development work.
Developers generally check out and edit and run the code the normal way
without any containers, on Linux or macOS.

## Staging

If you want to try the docker-compose configuration locally before
trying it on production, use **staging**:

    ./helper.py staging up

Use this environment to test the Docker deployment _before_ pushing to
production. It will build a docker container that is essentially the same
as what will run in production, and will use the normal paths inside your
local code checkout for resources and databases.

On linux, the app may be unable to write to the database unless you
add a `docker-compose.override.yml` file to run morphodict inside the
container with the same UID that you use for development.

    version: "3"

    services:
      itwewina:
        user: "$YOUR_LOCAL_NUMERIC_USER_ID_EG_1000"

The staging setup *can* be made to work on Docker for Mac, but there are
some subtle differences in how users and mount permissions are handled
between Docker for Mac and docker on linux. Using docker on linux for
staging is recommended, as that’s closer to the production setup, so there
will be fewer surprises when shifting to production.

If you want to run the Cypress tests on the staging container, use
the following:

     CYPRESS_BASE_URL=http://localhost:8001 npx cypress open

Setting `CYPRESS_BASE_URL` is [one of several ways to set] [cypress settings].

[one of several ways to set]: https://docs.cypress.io/guides/guides/environment-variables
[cypress settings]: https://docs.cypress.io/guides/references/configuration

See: https://docs.cypress.io/guides/guides/environment-variables.html#We-can-move-this-into-a-Cypress-environment-variable

When satisfied with the Docker environment used in staging, move it to
production:

## Production

The containers run on the server `itw.altlab.dev`, with nginx on the
`altlab.dev` gateway server proxying traffic to it.

The production machines run relatively recent releases of Ubuntu LTS.

The docker image is automatically built and uploaded by github actions as
[`ghcr.io/ualbertaaltlab/itwewina.altlab.app:latest`][ghcr].
But you can also build it locally, and tag your local build as the ghcr one
as well in a pinch.

### Users and groups

There are two users: `morphodict` and `morphodict-run`. The `morphodict` user is
a regular UNIX user that owns the git checkout, has access to docker, and
which people can sudo to for interaction with the production deploy.

The other is a much more limited user used for running the container. In
case something goes wrong inside the container, it should have limited
access to a few data directories, and no other privileges. In particular it
should not be able to access the docker API, should not be a member of the
`docker` or `morphodict` groups, and should not have write access to
application code.

There are also groups with the same names, `morphodict` and
`morphodict-run`. The `morphodict` user belongs to both groups so that it
does setup, configuration, and debugging; the `morphodict-run` user belongs
*only* to the `morphodict-run` group since it should have as few privileges
as possible.

In general, you should interact with the production deployment by
using `sudo` to run commands as `morphodict`.

Feel free to add yourself to the `morphodict` and `morphodict-run` groups
to more easily poke at the production environment.

### Data paths

Production data is stored in `/data_local/application-data`, and mounted
into the containers. Data files should all be readable, and some should
also be writable, by the `morphodict-run` group.

To help ensure that directories are usable by the `morphodict-run` group
even if the `morphodict` user or someone else creates them, the base
application directories are created with the `g+s` aka `0o2000` chmod bit.
According to [inode(7)],

> The set-group-ID bit (S_ISGID) has several special uses.  For a
> directory, it indicates that … for that directory: files created there
> inherit their group ID from the directory, not from the effective group
> ID of the creating process, and directories created there will also get
> the S_ISGID bit set.

[inode(7)]: https://man7.org/linux/man-pages/man7/inode.7.html

This means that files and directories created by the `morphodict` user
inside the base directory will automatically inherit the `morphodict-run`
group of their parent directories. However, do note that the `g+s` bit is
silently removed when running chown, even if the user and group are the
same before and after.

### The helper tool

Rather than giving you a bunch of commands to copy and substitute values
into and paste into your terminal, morphodict gives you `docker/helper.py`,
a tool that encapsulates all the fiddly commands you’d otherwise have to
copy-and-paste (or memorize!), along with automatically filling in needed
parameters from a single place: [docker/helper/settings.py][].

Run `./docker/helper.py --help` to see more about what it can do.

That said, if you are in production you can poke at the containers directly
with `docker`, and if you are in the `~morphodict/morphodict/docker`
directory, you can also run `docker-compose` directly. It’s really up to
you.

  - For restarting a container, `docker-compose restart `sssttt` is
    easiest, but must be run from the correct directory.

  - For running a management command inside a docker container, there is a
    handy helper into the tool.

  - Sometimes for debugging you will want to use the `docker` command-line
    tool directly.

The basic guideline in developing the tool was that any common operation
that needed any fiddly options or multiple commands to make work was
encapsulated in a helper command. That’s why there’s not (yet?) a command
for restarting a container: `docker-compose restart sssttt` isn’t very
fiddly.

### Installation

These steps should only be needed if you are setting up morphodict on a new
production host. But if something goes wrong, it’s generally safe to repeat
the steps to make sure everything is set up correctly.

#### Privileged setup

To set up initial users, groups, and base directories, all of which require
root access, there is an ansible script in `docker/plays`.

 It only needs to be run:
  - When first setting up a new production morphodict host
  - When adding a new dictionary
  - If it is edited to effect some desired configuration change

It’s off in its own little world because it requires sudo access to run,
and it creates the users and directories that would normally have a
checkout containing the setup code.

When getting started, from your local machine’s `docker/plays` folder, copy
`initial-setup.yml` and `vars.yml` to anywhere on the production machine,
and you’ll be able to run them from there.

To install ansible on the production host, run this, **as your login user,
not as root**:

    pip3 install --user ansible

To get a *preview* of what changes the playbook would apply if you weren’t
previewing it, run it with the `--check` option as a non-root user:

    ansible-playbook --check --diff initial-setup.yml

To actually apply changes, run the following command. `--become` means that
it will use your sudo privileges to become the root user in order to apply
the changes.

    ansible-playbook --become --ask-become-pass --diff initial-setup.yml

If you are repeatedly editing and re-running the playbook within short
periods of time from the same terminal, you can leave off
`--ask-become-pass` after the first run, as your cached sudo credentials
will be used.

Once the privileged setup is complete, you can use the `morphodict` user
and directories it created:

#### Unprivileged setup

Check out the morphodict repo to `~morphodict/morphodict`, if you haven’t
already done that. Make sure LFS is set up! Otherwise you will get
inscrutable error messages on startup like `_pickle.UnpicklingError:
invalid load key, 'v'.`

    $ sudo -i -u morphodict
    $ git clone https://github.com/UAlbertaALTLab/morphodict
    $ cd morphodict && git lfs install && git lfs fetch && git lfs checkout

As the `morphodict` user, run `docker/helper.py setup`, and it’ll create
all the required files and directories, or error out if the privileged
setup hasn’t been done yet.

 1. Run the helper tool to create all the files and directories and set
    permissions. **If you don’t do this first, docker will create
    directories where there should be files and confusion will follow.**

        sudo -u morphodict ~morphodict/morphodict/docker/helper.py setup

 2. Because of how Docker works, the following commands can only work if
    the target container is already running.

    So, first run

        cd ~morphodict/morphodict/docker && docker-compose up -d

    to start all the containers. The apps won’t work yet, but they will
    after you restart them at the end of this list.

 3. Create the initial schema with:

        docker/helper.py all manage migrate

 4. Populate the dictionary for a specific app, e.g., `arpeng`, with

        docker/helper.py manage arpeng importjsondict

    or try

        docker/helper.py manage arpeng importjsondict \
            src/arpeng/resources/dictionary/arpeng_test_db.importjson

    if you only want the test dictionary for now. Note that the specified
    path must be inside the container, and be specified relative to the git
    repo root.

    For more on updating production dictionaries, see [dictionaries in
    production](dictionaries-in-production).

 5. The app may not work very well if it the container was started before
    the database schema was in place, or if an import has invalidated some
    caches built on startup. You can restart a container with

        docker-compose restart arpeng

Once the app is up and running, you can serve it to the world by adding an
nginx proxy to the gateway.

### nginx

The configuration files are located in `/etc/nginx/sites-available`, with
symlinks in `/etc/nginx/sites-enabled`.

To add a new site:

  - Create a new file `/etc/nginx/sites-available/$SUBDOMAIN.altlab.dev`
    containing

        server {
            listen 443 ssl;
            server_name $SUBDOMAIN.altlab.dev;
            access_log /var/log/nginx/$SUBDOMAIN.dev.access.log;

            location / {
                proxy_set_header Host $host;
                proxy_pass http://altlab-itw:$PORT;
            }
        }

        server {
            listen 80;
            server_name $SUBDOMAIN.altlab.dev;
            return 301 https://$SUBDOMAIN.altlab.dev$request_uri;
        }

    with `$SUBDOMAIN` and `$PORT` replaced by the correct values.

  - Symlink the configuration file into the correct directory:

        cd /etc/nginx/sites-enabled && sudo ln -s ../sites-available/$SUBDOMAIN.altlab.dev .

  - Apply the nginx configuration change:

        sudo nginx -t && sudo systemctl reload nginx

  - Set up TLS certificates by running `sudo certbot`, entering the number
    of your new domain from the list it provides, and skipping the part
    about setting up redirects because that’s already handled in the
    snippet above.

#### Domains with diacritics

Did you know that
[https://itwêwina.altlab.app](https://itwêwina.altlab.app) is a valid link?
To make things like this work, you enter magic ascii hostnames into the
nginx config file that browsers convert to non-ascii. Search the web for a
‘punycode converter’ that’ll tell you that `itwêwina.altlab.app` ==
`xn--itwwina-lya.altlab.app`. Take a look at the nginx config file with
that name on `altlab.dev` in production.

For webapps, it’s not a good idea to have multiple domains serving up
exactly the same content, so you should pick one canonical domain to appear
in the address bar, and set all the other versions of the name to redirect
to it. For itwêwina, the canonical domain is currently
`itwewina.altlab.app`, but one could conceivably have the
`itwêwina.altlab.app` one be canonical with the `itwewina.altlab.app`
version redirecting to it.

Note that for security reasons, browsers have complicated rules about which
limited sets of characters they’ll allows to be displayed directly in the
URL bar, with any transgression of those rules resulting int he domain
displaying as the raw punycode form instead, e.g.,
`xn--itwwina-lya.altlab.app`. If you try using diacritics for the canonical
domain, be sure to test it on many browsers on many platforms!

## Redeployment

Every time a commit is pushed to the default branch on GitHub, the
redeployment workflow begins on GitHub actions:

 - the unit tests and integration tests run
 - a Docker image is built
 - the Docker image is pushed to the [GitHub container
   registry][ghcr]

At the end of a successful CI run on the main branch, the CI workflow POSTs
to <https://deploy.altlab.dev/>, which triggers the `docker/deploy` script
to run on itw.altlab.dev.

This script:
  - pulls the latest changes **both** from the git repository **and** from
    the uploaded Docker image
  - restarts the container
  - runs migrations

It is totally fine to run the deploy script by hand, especially for
debugging; just try to be sure that no automated deployments are happening
at the same time.

    sudo -u morphodict ~morphodict/morphodict/docker/deploy

[ghcr]: https://github.com/orgs/UAlbertaALTLab/packages/container/package/itwewina.altlab.app
