# -*- coding: utf-8 -*-
"""API section."""

import re
from os.path import join, splitext
from pathlib import Path
from typing import Generator, Optional

import kgcl_schema.grammar.parser as kgcl_parser
from github import Github
from github.Issue import Issue
from oaklib.cli import query_terms_iterator
from oaklib.implementations import ProntoImplementation, SimpleOboImplementation
from oaklib.interfaces.patcher_interface import PatcherInterface
from oaklib.selector import get_resource_from_shorthand

HOME_DIR = Path(__file__).resolve().parents[2]
SRC = HOME_DIR / "src/ontobot_change_agent"
TESTS = HOME_DIR / "tests"
ONTOLOGY_RESOURCE = TESTS / "resources/fbbt.obo"
# RESOURCE_DICT = {
#     "hrshdhgd/mondo": "src/ontology/mondo-edit.obo",
#     "hrshdhgd/ontobot-change-agent": ONTOLOGY_RESOURCE,
# }

# Token.txt unique to every user.
# For more information:
#   https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Save the token in a txt file as named below.
SRC = Path(__file__).parent
TOKEN_FILE = join(SRC, "token.txt")

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
    token: str = None,
    title_search: Optional[str] = None,
    label: Optional[str] = None,
    number: Optional[int] = 0,
    state: str = "open",
) -> Generator:
    """Get issues of specific states from a Github repository.

    :param repository_name: Name of the repository [org/repo]
    :param token: Github token for authorization, defaults to None
    :param title_search: Regex for title of the issue., defaults to None
    :param label: Issue label, defaults to None
    :param number: Issue number, defaults to 0
    :param state: State of the issue e.g. open, close etc., defaults to "open"
    :yield: Issue names that match the regex/label/number.
    """
    if token is None:
        token_file = TOKEN_FILE
        with open(token_file, "r") as t:
            token = t.read().rstrip()

    g = Github(token)
    repo = g.get_repo(repository_name)
    label_object = None
    if label:
        label_object = repo.get_label(label)
    if number and number > 0:
        yield _extract_info_from_issue_object(repo.get_issue(number))
    else:
        issues = repo.get_issues(state=state)
        for issue in issues:
            if title_search is None and label_object is None and number == 0:
                yield issue
            elif title_search and re.match(title_search, issue.title):
                yield _extract_info_from_issue_object(issue)
            elif label_object and label_object in issue.labels:
                yield _extract_info_from_issue_object(issue)
            else:
                yield None


def _extract_info_from_issue_object(issue: Issue) -> dict:
    issue_as_dict = issue.__dict__
    important_info = {k: issue_as_dict[RAW_DATA][k] for k in ISSUE_KEYS}
    important_info["body"] = _make_sense_of_body(important_info["body"])
    important_info["user"] = issue_as_dict["_rawData"]["user"]["login"]
    important_info["labels"] = [label["name"] for label in issue_as_dict["_rawData"]["labels"]]
    return important_info


def _make_sense_of_body(body: str) -> str:
    # splitter = "\r\n"
    # if "* " in body:
    #     bullet = "* "
    # else:
    #     bullet = "- "
    # splitter += bullet

    # return (
    #     body.lstrip(bullet).replace("<", "").replace(">", "").split(splitter)
    # )
    return body.replace("<", "").replace(">", "")


def get_all_labels_from_repo(repository_name: str, token: str = None) -> dict:
    """Get all labels available in a repository for tagging issues on creation.

    :param repository_name: Name of the repository.
    :param token: Github token for authorization, defaults to None
    :return: A dictionary of {name: description}
    """
    if token is None:
        token_file = TOKEN_FILE
        with open(token_file, "r") as t:
            token = t.read().rstrip()

    g = Github(token)
    repo = g.get_repo(repository_name)
    return {label.name: label.description for label in repo.get_labels()}


def process_issue_via_oak(input: str, commands: list, output: str = None):
    """Pass KGCL commands in the body to OAK.

    :param input: Path of resource to be worked on.
    :param commands: A list of commands.
    :param output: Path to where the output is written, defaults to None
    """
    resource = get_resource_from_shorthand(input)
    impl_class = resource.implementation_class
    # #! Detour: Implementation class: SimpleObo if Pronto chosen by default
    if impl_class == ProntoImplementation:
        impl_class = SimpleOboImplementation
    impl_obj: PatcherInterface = impl_class(resource)

    _, ext = splitext(str(output))
    # else:
    #     output = str(resource.local_path)
    #     _, ext = splitext(output)

    output_format = ext.replace(".", "")

    for command in commands:
        change = kgcl_parser.parse_statement(command)
        # TODO: There must be a better way to identify label in command.
        if ":" not in command and change.about_node is None:
            change.about_node = list(
                query_terms_iterator([change.old_value.strip("'").strip('"')], impl_obj)
            )[0]

        impl_obj.apply_patch(change)

    impl_obj.dump(output, output_format)


def process_new_term_template(body, prefix):
    """Process an issue generated via new term request template."""
    split_body = body.replace("\r", "").strip("#").split("\n\n###")
    CURIE = prefix + ":XXXXXX"
    body_as_dict = {}

    for line in split_body:
        if line.split("\n\n")[1].strip() not in ["_No response_", "None"]:
            body_as_dict[line.split("\n\n")[0].strip()] = line.split("\n\n")[1].strip()

    kgcl_command_list = [f"create node {CURIE} '{body_as_dict['Label']}'"]

    if "Synonyms" in body_as_dict:
        body_as_dict["Synonyms"] = body_as_dict["Synonyms"].split(",")
        for synonym in body_as_dict["Synonyms"]:
            if "Synonym type" in body_as_dict:
                kgcl_command_list.append(
                    f"create {body_as_dict['Synonym type']} synonym '{synonym.strip()}' for {CURIE}"
                )
            else:
                kgcl_command_list.append(f"create synonym {synonym.strip()} for {CURIE}")

    return (kgcl_command_list, body_as_dict)
