# -*- coding: utf-8 -*-

"""Command line interface for :mod:`ontobot_change_agent`."""

import logging
import re
from typing import TextIO

import click

from ontobot_change_agent import __version__
from ontobot_change_agent.api import (
    get_all_labels_from_repo,
    get_issues,
    process_issue_via_oak,
)

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)

BODY = "body"
TITLE = "title"


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """CLI for ontobot_change_agent.

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


# Input arguments for obo/owl
input_argument = click.argument("input", required=True, type=click.Path())
# All frequently used options.
repo_option = click.option(
    "-r",
    "--repo",
    required=True,
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
@input_argument
@repo_option
@label_option
@issue_number_option
@state_option
@output_option
def process_issue(
    input: str, repo: str, label: str, number: int, state: str, output: str
):
    """Run processes based on issue label.

    :param repo: GitHub repository name [org/repo_name]
    :param label: Label of issues.
    :param state: State of issue ["open", "close" etc.]
    """
    formatted_body = "The following commands were executed: </br>"

    for issue in get_issues(
        repository_name=repo, label=label, number=number, state=state
    ):
        issue_body = issue[BODY].replace("\n", "  ")
        begin_match = re.match(r"(.*)ontobot(.*)apply(.*):(.*)\*", issue_body)
        end_match = re.match(r"(.*)---", issue_body)

        if begin_match:
            begin_index = begin_match.end() - 1
        else:
            begin_index = 0

        if end_match is not None:
            end_index = end_match.end() - 3
        else:
            end_index = 0

        if output:
            new_output = output
        else:
            new_output = input

        if begin_index < end_index:
            KGCL_COMMANDS = issue_body[begin_index:end_index].split("* ")[1:]
            KGCL_COMMANDS = [x.strip() for x in KGCL_COMMANDS]
            if (
                issue["number"] == number  # noqa W503
                and len(KGCL_COMMANDS) > 0  # noqa W503
            ):
                process_issue_via_oak(
                    input=input,
                    commands=KGCL_COMMANDS,
                    output=new_output,
                )

                formatted_body += _list_to_markdown(KGCL_COMMANDS)
                formatted_body += "</br>Fixes #" + str(issue["number"])

                click.echo(
                    f"""
                    ::set-output name=PR_BODY::{formatted_body}
                    ::set-output name=PR_TITLE::{issue[TITLE]}
                    """
                )
        else:
            click.echo(
                f"""{issue[TITLE]} does not need ontobot's attention."""
            )


def _list_to_markdown(list: list) -> str:
    bullet = "* "
    md = ""
    for line in list:
        md += bullet + line + "</br>"
    return md


if __name__ == "__main__":
    main()
