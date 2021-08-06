import os.path


class App:
    def __init__(self, language_pair, port, uwsgi_stats_port, name=None):
        self.language_pair = language_pair
        if name:
            self._name = name
        self.port = port
        self.uwsgi_stats_port = uwsgi_stats_port

    def lfs_mounts(self):
        """Large files that are mounted from the local git lfs checkout,
        instead of being built into the container."""
        return [
            "morphodict/lexicon/resources/vector_models/",
            f"{self.language_pair}/res/fst",
            # Holds phrase-translation FSTs
            "CreeDictionary/res/fst/",
        ]

    def prod_data_dir(self):
        return f"/data_local/application-data/{self.name}"

    def data_mounts(self):
        return [
            DataMount(self, "resources/vector_models/"),
            DataMount(self, "db/"),
            DataMount(self, "CreeDictionary/search_quality"),
        ]

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        return self.language_pair


class DataMount:
    def __init__(self, app, path):
        self.app = app
        self._path = path

        self.target = f"/app/src/{app.language_pair}/{path}"
        self.dev_src = f"../src/{app.language_pair}/{path}"

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
