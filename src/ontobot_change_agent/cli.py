# -*- coding: utf-8 -*-

"""Command line interface for :mod:`ontobot_change_agent`."""

import logging
import os
import re
from typing import TextIO, Union

import click

from ontobot_change_agent import __version__
from ontobot_change_agent.api import (
    get_all_labels_from_repo,
    get_issues,
    process_issue_via_jar,
    process_issue_via_oak,
    process_new_term_template,
)
from ontobot_change_agent.constants import NEW_TERM_LABEL, OWL_EXTENSION

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)

BODY = "body"
TITLE = "title"
USER = "user"


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
token_option = click.option(
    "-g",
    "--token",
    help="Github token for the repository.",
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

prefix_option = click.option("-p", "--prefix", help="Assign prefix based on ontology resource.")

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
jar_path_option = click.option(
    "-j",
    "--jar-path",
    type=click.Path(exists=True),
    help="Path to jar file.",
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
@token_option
@label_option
@issue_number_option
def issues(
    repo: str,
    token: str,
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
        token=token,
        state=state,
        title_search=title_search,
        label=label,
        number=number,
    ):
        print(issue, file=output)


@main.command("get-labels")
@repo_option
@token_option
def get_labels(repo: str, token: str):
    """Get all labels for issues.

    :param repo: GitHub repository name [org/repo_name]
    """
    print(get_all_labels_from_repo(repo, token))


@main.command()
@input_argument
@repo_option
@token_option
@prefix_option
@label_option
@issue_number_option
@state_option
@jar_path_option
@output_option
def process_issue(
    input: str,
    repo: str,
    prefix: str,
    token: str,
    label: str,
    number: int,
    state: str,
    jar_path: str,
    output: str,
):
    """Run processes based on issue label.

    :param repo: GitHub repository name [org/repo_name]
    :param label: Label of issues.
    :param state: State of issue ["open", "close" etc.]
    """
    if input.endswith(OWL_EXTENSION) and jar_path is None:
        click.UsageError("If the resource is an OWL file, kgcl-java jar filepath must be provided.")

    for issue in get_issues(
        repository_name=repo, token=token, label=label, number=number, state=state
    ):
        # Make sure ontobot_change_agent needs to be triggered or no.
        if issue:
            KGCL_COMMANDS = []
            if NEW_TERM_LABEL in issue["labels"]:
                formatted_body = "The following input was provided: </br> "
                KGCL_COMMANDS, body_as_dict, reason = process_new_term_template(
                    issue["body"], prefix
                )
                if reason is None:
                    formatted_body += _convert_to_markdown(body_as_dict)
                    formatted_body += "</br> The following commands were executed: </br> "
                else:
                    click.echo(
                        f"""{issue[TITLE]} does not need ontobot's attention since {reason}""",  # noqa
                    )
                    break

            elif re.match(r"(.*)ontobot(.*)apply(.*):(.*)", issue[BODY]):
                formatted_body = "The following commands were executed: </br> "
                bullet_starters = ["* ", "- "]
                for bullet in bullet_starters:
                    KGCL_COMMANDS.extend(
                        [
                            str(item).replace(bullet, "")
                            for item in issue[BODY].splitlines()
                            if item.lstrip().startswith(bullet)
                        ]
                    )

                KGCL_COMMANDS = [x.strip() for x in KGCL_COMMANDS]

            else:
                click.echo(f"""{issue[TITLE]} does not need ontobot's attention.""")
        else:
            click.echo(f"""Issue number:{number} is either closed or does not exist.""")
            break

        new_output = output if output else input

        if issue["number"] == number and len(KGCL_COMMANDS) > 0:  # noqa W503
            if input.endswith("owl"):
                process_issue_via_jar(
                    input=input,
                    commands=KGCL_COMMANDS,
                    jar_path=jar_path,
                    output=new_output,
                )
            elif input.endswith("obo"):
                process_issue_via_oak(
                    input=input,
                    commands=KGCL_COMMANDS,
                    output=new_output,
                )
            else:
                logger.error(f"{[input]}=> resource can only be OWL or OBO extension files.")
                break

            formatted_body += _convert_to_markdown(KGCL_COMMANDS)
            formatted_body += "</br>Fixes #" + str(issue["number"])

            if os.getenv("GITHUB_ENV"):
                with open(os.getenv("GITHUB_ENV"), "a") as env:  # type: ignore
                    print(f"PR_BODY={formatted_body}", file=env)
                    print(f"PR_TITLE={issue[TITLE]}", file=env)
                    print(f"ISSUE_CREATOR={issue[USER]}", file=env)

            click.echo(
                f"""
                PR_BODY={formatted_body}
                PR_TITLE={issue[TITLE]}
                ISSUE_CREATOR={issue[USER]}
                """
            )


def _convert_to_markdown(item: Union[list, dict]) -> str:
    bullet = "* "
    md = ""
    if isinstance(item, list):
        for line in item:
            md += bullet + line + "</br>"
    elif isinstance(item, dict):
        for k, v in item.items():
            md += bullet + k + ":" + str(v) + "</br>"
    return md


if __name__ == "__main__":
    main()
