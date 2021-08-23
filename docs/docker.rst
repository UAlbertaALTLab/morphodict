..
    `toctree`s can’t directly reference files outside the docs/ directory.
    But they can reference stub files like this one that use the `include`
    directive to pull in those same files from outside the docs/ directory.

    See https://stackoverflow.com/questions/10199233/can-sphinx-link-to-documents-that-are-not-located-in-directories-below-the-root

    Even though this file is a stub, don’t call it `foo-stub.rst` because
    the filename will show up in the public URL, e.g.,
    https://morphodict.readthedocs.io/en/latest/docker-stub.html
..

.. contents::
   :local:

.. include:: ../docker/README.md
    :parser: myst_parser_hack
