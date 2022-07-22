# -*- coding: utf-8 -*-
"""Onto-crawl API section."""

import re
from os.path import join
from pathlib import Path
from typing import Generator, Optional

import kgcl_schema.grammar.parser as kgcl_parser
from github import Github
from github.Issue import Issue
from oaklib.interfaces.patcher_interface import PatcherInterface
from oaklib.selector import get_resource_from_shorthand

HOME_DIR = Path(__file__).resolve().parents[2]
SRC = HOME_DIR / "src/onto_crawler"
TESTS = HOME_DIR / "tests"
ONTOLOGY_RESOURCE = TESTS / "resources/fbbt.obo"

# Token.txt unique to every user.
# For more information:
#   https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Save the token in a txt file as named below.
SRC = Path(__file__).parent
TOKEN_FILE = join(SRC, "token.txt")

with open(TOKEN_FILE, "r") as t:
    TOKEN = t.read().rstrip()

g = Github(TOKEN)
# Example for API: https://pygithub.readthedocs.io/en/latest/examples.html

RAW_DATA = "_rawData"
ISSUE_KEYS = [
    # 'repository_url',
    # 'html_url',
    "number",
    "title",
    # 'user',
    "labels",
    # 'assignee',
    # 'assignees',
    # "comments",
    # "created_at",
    # "updated_at",
    "body",
]


def get_issues(
    repository_name: str,
    title_search: Optional[str] = None,
    label: Optional[str] = None,
    number: Optional[int] = 0,
    state: str = "open",
) -> Generator:
    """Get issues of specific states from a Github repository.

    :param repository_name: Name of the repository [org/repo]
    :param title_search: Regex for title of the issue.
    :param state: State of the issue e.g. open, close etc., defaults to "open"
    :yield: Issue names that match the regex/label/number.
    """
    repo = g.get_repo(repository_name)
    label_object = None
    if label:
        label_object = repo.get_label(label)

    issues = repo.get_issues(state=state)

    for issue in issues:
        if title_search is None and label_object is None and number == 0:
            yield issue
        else:
            if title_search and re.match(title_search, issue.title):
                yield _extract_info_from_issue_object(issue)
            if label_object and label_object in issue.labels:
                yield _extract_info_from_issue_object(issue)
            if number and number == issue.number:
                yield _extract_info_from_issue_object(issue)


def _extract_info_from_issue_object(issue: Issue) -> dict:
    issue_as_dict = issue.__dict__
    important_info = {k: issue_as_dict[RAW_DATA][k] for k in ISSUE_KEYS}
    important_info["body"] = _make_sense_of_body(important_info["body"])
    return important_info


def _make_sense_of_body(body: str) -> list:
    return body.replace("\r", "").replace("\n", "").split("* ")[1:]


def get_all_labels_from_repo(repository_name: str) -> dict:
    """Get all labels available in a repository for tagging issues on creation.

    :param repository_name: Name of the repository.
    :return: A dictionary of {name: description}
    """
    repo = g.get_repo(repository_name)
    return {label.name: label.description for label in repo.get_labels()}


def process_issue_via_kgcl(body: list):
    """Pass KGCL commands in the body to OAK.

    :param body: A list of commands.
    """
    resource = get_resource_from_shorthand(str(ONTOLOGY_RESOURCE))
    impl_class = resource.implementation_class
    impl_obj: PatcherInterface = impl_class(resource)
    for command in body:
        # Run Command
        change = kgcl_parser.parse_statement(command)
        impl_obj.apply_patch(change)
