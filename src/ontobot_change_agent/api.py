# -*- coding: utf-8 -*-
"""API section."""

import json
import os
import re
import subprocess  # noqa S404
from os.path import join, splitext
from pathlib import Path
from typing import Generator, Optional
from urllib.parse import quote

import kgcl_schema.grammar.parser as kgcl_parser
import requests
import yaml
from github import Github
from github.Issue import Issue
from oaklib.cli import query_terms_iterator
from oaklib.implementations import ProntoImplementation, SimpleOboImplementation
from oaklib.interfaces.patcher_interface import PatcherInterface
from oaklib.selector import get_resource_from_shorthand

from ontobot_change_agent.constants import DEFINITION, SYNONYM_TYPE, SYNONYMS

HOME_DIR = Path(__file__).resolve().parents[2]
SRC = HOME_DIR / "src/ontobot_change_agent"
TESTS = HOME_DIR / "tests"
ONTOLOGY_RESOURCE = TESTS / "resources/fbbt.obo"
# RESOURCE_DICT = {
#     "hrshdhgd/mondo": "src/ontology/mondo-edit.obo",
#     "INCATools/ontobot-change-agent": ONTOLOGY_RESOURCE,
# }

# Token.txt unique to every user.
# For more information:
#   https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Save the token in a txt file as named below.
SRC = Path(__file__).parent
TOKEN_FILE = join(SRC, "token.txt")
ISSUE_TEMPLATE_DIR = ".github/ISSUE_TEMPLATE"
# TODO: This variable below needs to be standard across the board.
NEW_TERM_TEMPLATE_YAML = "/add-term.yml"
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
    repo = _get_repo_object(repository_name, token)
    global ISSUE_TEMPLATE_DIR
    ISSUE_TEMPLATE_DIR = repo.contents_url.replace("{+path}", ISSUE_TEMPLATE_DIR)
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


def get_comment_from_repo(repository_name: str, token: str = None, comment_id: int = 0):
    """Get a comment from a Github repository."""
    repo = _get_repo_object(repository_name, token)

    for comment in repo.get_issues_comments():
        if comment.id == comment_id:
            return comment.body
    return None


def _get_repo_object(repository_name: str, token: str = None):
    if token is None:
        token_file = TOKEN_FILE
        with open(token_file, "r") as t:
            token = t.read().rstrip()

    g = Github(token)
    return g.get_repo(repository_name)


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
    return body.replace("<", "").replace(">", "") if body else body


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
    """Process an issue generated via new term request template.

    :param body: Body of the issue.
    :param prefix: Prefix of the ontology corresponding to the repository.
    :return: Command list and body as a dict. If Issue does not match template: (None, None)
    :raises ValueError: If prefix is absent.
    """
    split_body = body.replace("\r", "").strip("#").split("\n\n###")
    reason = None
    if prefix:
        CURIE = prefix + ":XXXXXX"
    else:
        raise (ValueError("Prefix must be provided in the command."))

    body_as_dict = {}

    for line in split_body:
        if line.split("\n\n")[1].strip() not in ["_No response_", "None"]:
            body_as_dict[line.split("\n\n")[0].strip()] = line.split("\n\n")[1].strip()
    response_1 = requests.get(
        ISSUE_TEMPLATE_DIR + NEW_TERM_TEMPLATE_YAML, allow_redirects=True, timeout=5
    )
    metadata = json.loads(response_1.content.decode("utf-8"))
    if "message" in metadata and metadata["message"] == "Not Found":
        reason = "the 'New Term request' template yml does not exist."
        return (None, None, reason)
    else:
        download_url = metadata["download_url"]
        response_2 = requests.get(download_url, allow_redirects=True, timeout=5)
        content = response_2.content.decode("utf8")
        template = yaml.safe_load(content)
        list_of_template_keys = [x["attributes"]["label"] for x in template["body"] if "id" in x]
        if all(key in list_of_template_keys for key in body_as_dict.keys()):
            kgcl_command_list = [f"create node {CURIE} '{body_as_dict['Label']}'"]

            if SYNONYMS in body_as_dict:
                body_as_dict[SYNONYMS] = body_as_dict[SYNONYMS].split(",")
                for synonym in body_as_dict[SYNONYMS]:
                    if SYNONYM_TYPE in body_as_dict:
                        kgcl_command_list.append(
                            f"create {body_as_dict[SYNONYM_TYPE]} synonym '{synonym.strip()}' for {CURIE}"  # noqa
                        )
                    else:
                        kgcl_command_list.append(f"create synonym {synonym.strip()} for {CURIE}")

            if DEFINITION in body_as_dict:
                kgcl_command_list.append(
                    f"add definition '{body_as_dict[DEFINITION].strip()}' to {CURIE}"
                )

            return (kgcl_command_list, body_as_dict, reason)
        else:
            reason = "the issue does not match the 'New Term request' template."
            return (None, None, reason)


def process_issue_via_jar(input: str, commands: list, jar_path: str, output: str = None):
    """Pass KGCL commands in the body to kgcl-java.

    :param input: Path of resource to be worked on.
    :param commands: A list of commands.
    :param output: Path to where the output is written, defaults to None
    """
    if jar_path:
        cli_command = "java -jar {} apply -i {}".format(jar_path, input)
        # conversion = f" convert --format ofn -o {output}"
    else:
        cli_command = "robot kgcl:apply -i {}".format(input)
        # conversion = f" -o {output}"

    conversion = f" convert --format ofn -o {output}"
    kgcl_commands = [
        ' -k "{}"'.format(command.replace('"', "'")) for command in commands if len(commands) > 0
    ]
    full_command = cli_command + " ".join(kgcl_commands) + conversion
    # Run the command on the command line
    subprocess.run(full_command, shell=True)  # noqa S602


def _update_readme_with_new_content(readme_content, new_content):
    # Define the start and end markers
    start_marker = "<!-- IMPLEMENTERS_START -->"
    end_marker = "<!-- IMPLEMENTERS_END -->"

    # Find the start and end indices of the old content
    start_index = readme_content.find(start_marker) + len(start_marker)
    end_index = readme_content.find(end_marker)

    # Check if both markers are present
    if start_index == -1 or end_index == -1:
        raise ValueError("The start or end marker is missing in the README.md content.")

    # Replace the old content with the new content
    updated_readme = (
        readme_content[:start_index] + "\n" + new_content + "\n" + readme_content[end_index:]
    )

    return updated_readme


def get_ontobot_implementers(token: str = None):
    """Get the implementers of ontobot-change-agent and update the README.md.

    :param token: GitHub token for authorization, defaults to None.
    """
    # Define the search term, filter type, and repository details
    search_term = "Check if issue body contains 'Hey ontobot'"
    source = "INCATools/ontobot-change-agent"  # Replace with your GitHub organization/user
    repo = "repository"  # Replace with your GitHub repository name

    # Construct the search URL
    url = f"https://api.github.com/search/code?q={quote(search_term)}+in:file"

    # Headers for authorization and accepting the response in v3 format
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # Make a GET request to the GitHub API to search for the term
    response = requests.get(url, headers=headers, timeout=30)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        search_results = response.json()

        # Start constructing the new content to append to the README
        new_content = "\nOntology resources that are powered by `ontobot-change-agent`:\n"

        # Initialize an empty list to hold the repository details
        repo_details = []

        for item in search_results["items"]:
            # Extract the repository details
            repo = item["repository"]
            full_name = repo["full_name"]  # type: ignore
            html_url = repo["html_url"]  # type: ignore

            # Add the details to the list if the repository is not the source
            if full_name != source:
                repo_details.append((full_name, html_url))

        # Sort the list of tuples by the repository full name
        sorted_repo_details = sorted(repo_details, key=lambda x: x[0])

        # Iterate over the sorted list and append each item to new_content
        for full_name, html_url in sorted_repo_details:
            new_content += f" - [{full_name}]({html_url})\n"

        # Get current README.md file

        # Check if the script is running in a GitHub Actions environment
        if os.getenv("GITHUB_ACTIONS") == "true":
            # Use GITHUB_WORKSPACE environment variable to get the working directory
            github_workspace = Path(os.getenv("GITHUB_WORKSPACE"))  # type: ignore
            readme_path = github_workspace / "README.md"
        else:
            # Fallback to a local path (e.g., relative to the script) if not on GitHub Actions
            readme_path = Path(__file__).parents[2] / "README.md"
        with open(readme_path, "r") as file:
            current_readme_content = file.read()

        try:
            updated_readme_content = _update_readme_with_new_content(
                current_readme_content, new_content
            )
            with open(readme_path, "w") as file:
                file.write(updated_readme_content)
        except ValueError as e:
            print(e)
    else:
        print(f"Search failed. Status code: {response.status_code}")
