# -*- coding: utf-8 -*-

"""Command line interface for :mod:`onto_crawler`."""

import logging
from typing import TextIO

import click

from onto_crawler import __version__
from onto_crawler.api import get_issues

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """CLI for onto_crawler.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)


@main.command()
@click.option(
    "-r",
    "--repo",
    default="monarch-initiative/mondo",
    help="Org/name of the github repo.",
)
@click.option(
    "-s",
    "--state",
    default="open",
    help="State of the issue. [open, close etc.]",
)
@click.option(
    "-o",
    "--output",
    help="Output could be a file or sys.stdout.",
)
@click.option(
    "-t",
    "--title",
    help="Filter based on a search for pattern within title of issue.",
)
@click.option(
    "-l",
    "--label",
    help="Filter based on a search for label of issue.",
)
def issues(repo: str, state: str, title: str, label: str, output: TextIO):
    for issue in get_issues(
        repository_name=repo, state=state, title=title, label=label
    ):
        print(issue, file=output)


if __name__ == "__main__":
    main()
