# -*- coding: utf-8 -*-

"""Command line interface for :mod:`ontobot_change_agent`."""

import ast
import logging
import os
import re
from typing import TextIO, Union

import click

try:
    from llm_change_agent.cli import execute

    llm_change_agent_available = True
except ImportError:
    # Handle the case where the package is not installed
    llm_change_agent_available = False


from ontobot_change_agent import __version__
from ontobot_change_agent.api import (
    get_all_labels_from_repo,
    get_comment_from_repo,
    get_issues,
    get_ontobot_implementers,
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

comment_id_option = click.option(
    "-c",
    "--comment-id",
    type=int,
    help="Comment id of KGCL command presence.",
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
use_llm_option = click.option(
    "--use-llm/--no-use-llm",
    is_flag=True,
    default=False,
    help="Use llm-change-agent for processing.",
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
@comment_id_option
@state_option
@jar_path_option
@output_option
@use_llm_option
def process_issue(
    input: str,
    repo: str,
    prefix: str,
    token: str,
    label: str,
    number: int,
    comment_id: int,
    state: str,
    jar_path: str,
    output: str,
    use_llm: bool = False,
):
    """Run processes based on issue label.

    :param repo: GitHub repository name [org/repo_name]
    :param label: Label of issues.
    :param state: State of issue ["open", "close" etc.]
    """
    if input.endswith(OWL_EXTENSION) and jar_path is None:
        click.UsageError("If the resource is an OWL file, kgcl-java jar filepath must be provided.")

    if comment_id:
        formatted_body = "The following commands were executed: </br> "
        comment_body = get_comment_from_repo(
            repository_name=repo, token=token, comment_id=comment_id
        )
        KGCL_COMMANDS = _get_kgcl_commands(comment_body)
        issue = next(
            get_issues(repository_name=repo, token=token, label=label, number=number, state=state)
        )

    else:
        issues = get_issues(
            repository_name=repo, token=token, label=label, number=number, state=state
        )
        ontobot_pattern = re.compile(r"(.*)ontobot(.*)apply(.*):(.*)", re.DOTALL)

        click.echo("Starting to process issues...")

        for issue in issues:
            if not issue or not issue[BODY]:
                click.echo(
                    f"Issue number:{number} is either closed, does not exist or has no body."
                )
                break

            click.echo(f"Processing issue: {issue[TITLE]}")

            KGCL_COMMANDS = []
            formatted_body = ""

            if NEW_TERM_LABEL in issue["labels"]:
                click.echo("New term label found. Processing new term template...")
                formatted_body = "The following input was provided: </br> "
                KGCL_COMMANDS, body_as_dict, reason = process_new_term_template(
                    issue["body"], prefix
                )
                if reason is None:
                    click.echo("No reason found to skip. Converting body to markdown...")
                    formatted_body += _convert_to_markdown(body_as_dict)
                    formatted_body += "</br> The following commands were executed: </br> "
                else:
                    click.echo(f"{issue[TITLE]} does not need ontobot's attention since {reason}")
                    break
            elif ontobot_pattern.match(issue[BODY].lower()):
                click.echo("Ontobot apply command found. Extracting KGCL commands...")
                formatted_body = "The following commands were executed: </br> "
                KGCL_COMMANDS = _get_kgcl_commands(issue[BODY])

            elif use_llm and llm_change_agent_available:
                click.echo(f"Summoning llm-change-agent for {issue[TITLE]}")
                with click.Context(execute) as ctx:
                    ctx.params["prompt"] = issue[BODY]
                    ctx.params["provider"] = "cborg"
                    ctx.params["model"] = "google/gemini:latest"
                    response = execute.invoke(ctx)
                    KGCL_COMMANDS = [
                        command.replace('"', "'") for command in ast.literal_eval(response)
                    ]
                if KGCL_COMMANDS:
                    click.echo(f"llm-change-agent result: {response}")
                    formatted_body = "The following commands were executed: </br> "
                    click.echo(formatted_body + "\n".join(KGCL_COMMANDS))
                else:
                    click.echo(f"{issue[TITLE]} does not need ontobot's attention.")
            else:
                click.echo(
                    f"""{issue[TITLE]} does not need ontobot's
                      attention unless `--use-llm` flag is True."""
                )

    new_output = output if output else input

    # if issue["number"] == number and len(KGCL_COMMANDS) > 0:  # noqa W503
    if len(KGCL_COMMANDS) > 0:  # noqa W503
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
            # break

        formatted_body += _convert_to_markdown(KGCL_COMMANDS)
        formatted_body += "</br>Fixes #" + str(issue["number"])
        pr_title = f"Applying changes for: {issue['title']}"

        if os.getenv("GITHUB_ENV"):
            with open(os.getenv("GITHUB_ENV"), "a") as env:  # type: ignore
                print(f"PR_BODY={formatted_body}", file=env)
                print(f"PR_TITLE={pr_title}", file=env)
                print(f"ISSUE_CREATOR={issue[USER]}", file=env)

        click.echo(
            f"""
            PR_BODY={formatted_body}
            PR_TITLE={pr_title}
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


def _get_kgcl_commands(issue_body: str) -> list:
    KGCL_COMMANDS = []
    bullet_starters = ["* ", "- "]
    for bullet in bullet_starters:
        KGCL_COMMANDS.extend(
            [
                str(item).replace(bullet, "").replace('"', "'")
                for item in issue_body.splitlines()
                if item.lstrip().startswith(bullet)
            ]
        )
    KGCL_COMMANDS = [x.strip() for x in KGCL_COMMANDS]
    return KGCL_COMMANDS


@main.command("update-readme")
@input_argument
def get_implementers(input: str):
    """Get implementers of ontobot_change_agent."""
    get_ontobot_implementers(token=input)


if __name__ == "__main__":
    main()
