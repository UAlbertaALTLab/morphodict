.. morphodict documentation master file, created by
   sphinx-quickstart on Thu Jul 15 10:28:47 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to morphodict's documentation!
======================================

Morphodict is the `University of Alberta
ALTLab <https://altlab.ualberta.ca>`_’s intelligent dictionary application.
It currently powers the `itwêwina Plains Cree
Dictionary <https://itwewina.altlab.app>`_, with support for additional
languages in development.

The project is open-source, with the code currently hosted at
https://github.com/UAlbertaALTLab/cree-intelligent-dictionary; we intend
to rename the repo at some point.

This documentation is mainly targeted at computational linguists, and/or
general linguists with some enthusiasm for programming, who are trying to
get the code running on their local machines so that they can:

  - demo the software
  - contribute linguistic data
  - understand at a high level how the dictionary software works

There is additional developer documentation in README files scattered
throughout the codebase, as well as in comments and docstrings throughout.

..
  BTW this is a comment in RST

  How the toctree seems to work:

  Build up a hierachy by referencing .rst files that have their own toctree
  descriptions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   linguistic-data

   dictionary-data

   developers

   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
