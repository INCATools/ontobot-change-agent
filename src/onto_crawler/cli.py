# -*- coding: utf-8 -*-

"""Command line interface for :mod:`onto_crawler`."""

import logging
from typing import TextIO

import click

from onto_crawler import __version__
from onto_crawler.api import (
    get_all_labels_from_repo,
    get_issues,
    process_issue_via_kgcl,
)

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)

BODY = "body"


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
    default="hrshdhgd/mondo",
    help="Org/name of the github repo.",
)

issue_number_option = click.option(
    "-n",
    "--number",
    type=int,
    help="Filter based on issue number.",
)

label_option = click.option(
    "-l",
    "--label",
    help="Filter based on a search for label of issue.",
)

state_option = click.option(
    "-s",
    "--state",
    default="open",
    help="State of the issue. [open, close etc.]",
)

output_option = click.option(
    "-o",
    "--output",
    help="Output could be a file or sys.stdout.",
)


@main.command()
@repo_option
@state_option
@output_option
@click.option(
    "-t",
    "--title-search",
    help="Filter based on a search for pattern within title of issue.",
)
@label_option
@issue_number_option
def issues(
    repo: str,
    state: str,
    title_search: str,
    label: str,
    number: int,
    output: TextIO,
):
    """Get issues based on different options.

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

    :param repo: GitHub repository name [org/repo_name]
    """
    print(get_all_labels_from_repo(repo))


@main.command()
@repo_option
@label_option
@issue_number_option
@state_option
@output_option
def process_issue(repo: str, label: str, number: int, state: str, output: str):
    """Run processes based on issue label.

    :param repo: GitHub repository name [org/repo_name]
    :param label: Label of issues.
    :param state: State of issue ["open", "close" etc.]
    """
    for issue in get_issues(
        repository_name=repo, label=label, number=number, state=state
    ):
        if output:
            new_output = str(issue["number"]) + "_" + output
        else:
            new_output = output
        process_issue_via_kgcl(
            repository_name=repo, body=issue[BODY], output=new_output
        )
        # Open a new PR corresponding to the issue


if __name__ == "__main__":
    main()
