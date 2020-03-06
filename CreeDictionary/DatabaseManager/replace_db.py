import os
import sys
from ast import NodeTransformer, parse, Assign, Module, walk, FunctionDef
from pathlib import Path
from subprocess import Popen, PIPE

from astunparse import unparse
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.writer import MigrationWriter
from django.db.migrations import Migration


def get_import_new_dictionaries_node(node: Module):
    """
    get the function node of `import_new_dictionaries`
    """
    for descendent in walk(node):
        if (
            isinstance(descendent, FunctionDef)
            and descendent.name == "import_new_dictionaries"
        ):
            return descendent


# This function will be yoinked to the created migration. Please use local imports if dependencies are needed.
def import_new_dictionaries(apps, schema_editor):  # pragma: no cover
    # todo: (pseudocode)
    #   subprocess(manage-db, import --use-db temporary.db.sqlite3)
    #   swap(temporary.db.sqlite3, db.sqlite3)

    # this way production server wont get interrupted while it migrates
    pass


class CustomPythonMigrationEditor(NodeTransformer):
    def visit_Assign(self, node: Assign):
        # add RunPython to the (empty) operations
        if node.targets[0].id == "operations":
            assert len(node.value.elts) == 0
            node.value.elts.append(
                parse("migrations.RunPython(import_new_dictionaries)")
            )
        return node


# adapted from django.core.management.commands.makemigrations and django.db.migrations.autodetector
def create_replacing_migration():
    """
    # produce a migration that re-imports xml files
    """

    print("producing migration for the new database")

    # Load the current graph state. Pass in None for the connection so
    # the loader doesn't try to resolve replaced migrations from DB.
    loader = MigrationLoader(None, ignore_no_migrations=True)
    leaves = loader.graph.leaf_nodes(app="API")
    assert len(leaves) == 1
    leaf_migration_file_stem = leaves[0][1]
    next_number = (
        MigrationAutodetector.parse_number(leaf_migration_file_stem) or 0
    ) + 1
    new_name = "%04i_%s" % (next_number, "use_new_xml_files")
    migration = Migration(new_name, "API")
    migration.dependencies.append(("API", leaf_migration_file_stem))

    writer = MigrationWriter(migration, include_header=False)

    # Write the migrations file to the disk.
    migrations_directory = os.path.dirname(writer.path)
    os.makedirs(migrations_directory, exist_ok=True)
    migration_string = writer.as_string()
    filled_migration = CustomPythonMigrationEditor().visit(parse(migration_string))
    with open(writer.path, "w", encoding="utf-8") as fh:
        # write the `import_new_dictionaries_node` function
        fh.write("from django.db import migrations")
        fh.write(
            unparse(get_import_new_dictionaries_node(parse(Path(__file__).read_text())))
        )
        fh.write(unparse(filled_migration)[len("from django.db import migrations\n") :])
    Popen([sys.executable, "-m", "black", str(writer.path)], stdout=PIPE).wait()
