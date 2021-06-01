"""
Helper script to set up a new dictionary site

Probably will need a bit of tweaking every time it’s used, as it’s an infrequent
operation and will get out of sync, but this should cover most of the basics so
is better than nothing.
"""

# In theory there could be a detailed integration test to run this command to
# create a new site, and then run some smoke tests against it.

import shutil
from argparse import ArgumentParser
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.template import Template, Context


def make_python_dir(path):
    path.mkdir(exist_ok=True)
    (path / "__init__.py").touch()


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--port", type=int, required=True)
        parser.add_argument("source_language")
        parser.add_argument("target_language")

    def handle(self, *args, **options):
        sss = options["source_language"]
        ttt = options["target_language"]
        sssttt = sss + ttt
        new_site_dir = settings.BASE_DIR.parent / sssttt

        make_python_dir(new_site_dir)
        make_python_dir(new_site_dir / "site")
        make_python_dir(new_site_dir / "app")

        db_dir = new_site_dir / "db"
        db_dir.mkdir(exist_ok=True)
        (db_dir / ".keep").touch()

        shutil.copy(
            settings.BASE_DIR / "site" / "urls.py", new_site_dir / "site" / "urls.py"
        )

        def create_file_from_template(file_path, template_path, mode=None):
            template_text = (Path(__file__).parent / template_path).read_text()
            t = Template(template_text)
            ctx = Context(
                {"sss": sss, "ttt": ttt, "sssttt": sssttt, "port": options["port"]}
            )
            rendered = t.render(ctx)
            file_path.write_text(rendered)

            if mode is not None:
                file_path.chmod(mode)

        create_file_from_template(
            new_site_dir / "site" / "settings.py", "settings.py.template"
        )
        create_file_from_template(
            new_site_dir.parent.parent / f"{sssttt}-manage",
            "manage.py.template",
            mode=0o755,
        )
