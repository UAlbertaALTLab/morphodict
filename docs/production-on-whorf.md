Production deployment on Whorf
------------------------------

Updated: <time datetime="2021-04-16">April 16, 2021</time>.

itwêwina is deployed on ALTLab's "Whorf Cluster"; specifically, a host
called `itw.altlab.dev`. Its web address is:

<https://itwewina.altlab.dev>

## Where is everything?

All paths are on `itw.altlab.dev`, unless otherwise specified:

<dl>
<dt>The `itwewina` user's home directory</dt> 
<dd>`/opt/docker-compose/itwewina`</dd>
<dt>The cloned repository</dt> 
<dd>`/opt/docker-compose/itwewina/cree-intelligent-dictionary`</dd>
<dt>The database</dt> 
<dd>Please refer to the `volumes` key in the [`docker-compose.yml`][docker-compose] file</dd>
<dt>The Docker image</dt>
<dd>The [GitHub container registry][ghcr]</dd>
</dl>


## Important files to check for deployment

 - `docker/docker-compose.yml`
 - `docker/Dockerfile`
 - `docker/deploy`
 - `CreeDictionary/uwsgi.ini`

## Redeployment

Every time a commit is pushed to the default branch on GitHub, the
redeployment workflow begins on GitHub actions:

 - the unit tests and integration tests run
 - a Docker image is built
 - the Docker image is built and pushed to the [GitHub container
   registry][ghcr]

When the tests pass, <https://deploy.altlab.dev/>, which then instructs
the Whorf cluster to pull the latest changes **both** from the git
repository **and** from the uploaded Docker image. The new Docker image
is run on `itw.altlab.dev`.

Migrations are run, and (in most cases), the new code is deployed!

[ghcr]: https://github.com/orgs/UAlbertaALTLab/packages/container/package/itwewina.altlab.app
[docker-compose]: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/blob/master/docker/docker-compose.yml
