import os.path
from pathlib import Path


class App:
    """Object representing a webapp aka django project to be deployed."""

    def __init__(self, name, port, uwsgi_stats_port):
        self.name = name
        self.port = port
        self.uwsgi_stats_port = uwsgi_stats_port

    def lfs_mounts(self):
        """Large files that are mounted from the local git lfs checkout,
        instead of being built into the container."""
        return [
            "morphodict/lexicon/resources/vector_models/",
            f"{self.name}/resources/fst",
            # Holds phrase-translation FSTs
            "CreeDictionary/res/fst/",
            "CreeDictionary/res/",
            # Not actually an LFS thing, but this is where production dictionary
            # files get stored so they can be imported.
            f"{self.name}/resources/dictionary/",
        ]

    def prod_data_dir(self):
        return f"/data_local/application-data/{self.name}"

    def prod_db_file(self):
        return Path(self.prod_data_dir()) / "db" / "db.sqlite3"

    def data_mounts(self):
        return [
            DataMount(self, "resources/vector_models/"),
            DataMount(self, "db/"),
            DataMount(self, "CreeDictionary/search_quality/"),
        ]


class DataMount:
    def __init__(self, app, path):
        self.app = app
        self._path = path

        self.target = f"/app/src/{app.name}/{path}"
        self.dev_src = f"../src/{app.name}/{path}"

    @property
    def is_dir(self):
        """Is this mount a directory mount?

        Relies on the docker-compose convention that directories can be
        specified as ending with slashes.
        """
        return self._path.endswith("/")

    @property
    def prod_src(self):
        """Where to mount this path from in prod.

        Defaults to a subfolder in app.prod_data_dir(), using only the last
        directory component of the target path.
        """
        # The gymnastics are to preserve trailing slashes
        if self._path.endswith("/"):
            basename = os.path.basename(os.path.dirname(self._path))
        else:
            basename = os.path.basename(self._path)

        return f"{self.app.prod_data_dir()}/{basename}"

    def __repr__(self):
        return f"DataMount<{self.app.name}, {self._path!r}>"
