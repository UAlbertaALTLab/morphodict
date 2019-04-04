#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2019 Eddie Antonio Santos <easantos@ualberta.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Runs hfst-optimized-lookup to generate word form from the Cree FST.

Requirements
------------

 * crk-normative-generator.hfstol -- download from here: https://github.com/UAlbertaALTLab/plains-cree-fsts/releases
 * HFST -- See here for instructions: https://github.com/hfst/hfst#installation

Usage
-----

    import generate_forms_hfst

    # Use this to generate wordforms for many, many analyses!
    generate_forms_hfst.generate(['analysis-1', 'analysis-2', ..., 'analysis-N'], file='path/to/generator.hfstol')

Tests
-----

To run the doctests in this module, first make sure that the HFST suite is
installed and that crk-normative-generator.hfstol is in the current working
directory. Then run:

    python3 -m doctest --verbose generate_forms_hfst.py

Copying
-------

This code is copyright © 2019 Eddie Antonio Santos. It is distributed under
the terms of the Apache 2.0. license.
"""

import subprocess
import shutil
import os
from subprocess import PIPE


# Determine the location of hfst-optimized-lookup
if os.name == "nt":
    HFSTOL_PATH = "../hfst/bin/hfst-optimized-lookup.exe"
else:
    HFSTOL_PATH = shutil.which('hfst-optimized-lookup')
if HFSTOL_PATH is None:
    raise ImportError(
        'hfst-optimized-lookup is not installed.\n'
        'Please install the HFST suite on your system '
        'before importing this module.\n'
        'See: https://github.com/hfst/hfst#installation'
    )


def generate(analyses, fst_path='./crk-normative-generator.hfstol'):
    """
    Given one or more analyses, returns a dictionary with keys being the input
    parameters, and values being the set of returned analyses.

    For best performance, call this on as many many analyses as possible — use
    a big list of analyses!

    Args:
        analyses (iterable of str): zero or more of analyses to
                                    convert into word forms
    Kwargs:
        fst_path (str): path to the *.hfstol file

    Returns:
        dict of anaylsis (keys) and a set of its word forms (values)

    Example: Generate from exactly one anaylsis:
    >>> generate(['nôhkom+N+A+D+Px1Pl+Sg'])
    {'nôhkom+N+A+D+Px1Pl+Sg': {'nôhkominân'}}

    Example: Returns an empty set when the analysis could not be found:
    >>> generate(['nôhkom+N+A+I+Px1Pl+Sg'])
    {'nôhkom+N+A+I+Px1Pl+Sg': set()}

    Example: An analysis can return multiple analyses.
    >>> generate(['nôhkom+N+A+D+Der/Dim+N+A+D+Px2Sg+Sg'])
    {'nôhkom+N+A+D+Der/Dim+N+A+D+Px2Sg+Sg': {'kôhkomis', 'kôhkomisis'}}

    Example: You can pass in multiple analyses.
    >>> generate(('mitêh+N+I+D+PxX+Sg', 'wâpamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO', 'nîpiy+N+I+Loc'))
    {'mitêh+N+I+D+PxX+Sg': {'mitêh'}, 'wâpamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO': {'wâpamêw'}, 'nîpiy+N+I+Loc': {'nîpîhk'}}

    Example: You can explicitly provide the path to the generator FST:
    >>> generate({'mitêh+N+I+D+PxX+Sg'}, fst_path='./crk-normative-generator.hfstol')
    {'mitêh+N+I+D+PxX+Sg': {'mitêh'}}
    """

    # hfst-optimized-lookup expects each analysis on a separate line:
    lines = '\n'.join(analyses).encode('UTF-8')

    status = subprocess.run([HFSTOL_PATH, '--quiet', '--pipe-mode', fst_path],
                            input=lines, stdout=PIPE, stderr=PIPE, shell=False)

    analysis2wordform = {}
    for line in status.stdout.decode('UTF-8').splitlines():
        # Remove extraneous whitespace.
        line = line.strip()
        # Skip empty lines.
        if not line:
            continue

        # Each line will be in this form:
        #   verbatim-analysis \t wordform
        # where \t is a tab character
        # e.g.,
        #   nôhkom+N+A+D+Px1Pl+Sg \t nôhkominân
        # If the analysis doesn't match, the transduction will have +?:
        # e.g.,
        #   nôhkom+N+A+I+Px1Pl+Sg	nôhkom+N+A+I+Px1Pl+Sg	+?
        analysis, word_form, *rest = line.split('\t')

        # ensure the set exists:
        if analysis not in analysis2wordform:
            analysis2wordform[analysis] = set()

        # Generating this word form failed!
        if '+?' in rest:
            continue

        analysis2wordform[analysis].add(word_form)

    return analysis2wordform
