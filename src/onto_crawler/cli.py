# -*- coding: utf-8 -*-

"""Command line interface for :mod:`onto_crawler`."""

import logging
from typing import TextIO

import click

from onto_crawler import __version__
from onto_crawler.api import get_all_labels_from_repo, get_issues

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


# All frequently used options.
repo_option = click.option(
    "-r",
    "--repo",
    default="monarch-initiative/mondo",
    help="Org/name of the github repo.",
)


@main.command()
@repo_option
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
    "--title-search",
    help="Filter based on a search for pattern within title of issue.",
)
@click.option(
    "-l",
    "--label",
    help="Filter based on a search for label of issue.",
)
@click.option(
    "-n",
    "--number",
    type=int,
    help="Filter based on issue number.",
)
def issues(
    repo: str,
    state: str,
    title_search: str,
    label: str,
    number: int,
    output: TextIO,
):
    """Get issues of specific states, title, labels or number from a Github repository.

    :param repo: GitHub repository name [org/repo_name]
    :param state: State of issue ["open", "close" etc.]
    :param title_search: String lookup in title of issue.
    :param label: Label lookup for issues.
    :param output: Output location.
    """
    for issue in get_issues(
        repository_name=repo,
        state=state,
        title_search=title_search,
        label=label,
        number=number,
    ):
        print(issue, file=output)


@main.command("get-labels")
@repo_option
def get_labels(repo: str):
    """Get all labels for issues.

    :param repo: Name of the repository.
    """
    print(get_all_labels_from_repo(repo))


if __name__ == "__main__":
    main()
