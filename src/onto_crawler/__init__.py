# -*- coding: utf-8 -*-

"""Crawl github for ontology related issues."""

import sys

from .api import *  # noqa

if sys.version_info >= (3, 8):
    import importlib.metadata

    __version__ = importlib.metadata.version(__name__)
elif sys.version_info < (3, 8):
    import importlib_metadata

    __version__ = importlib_metadata.version(__name__)
