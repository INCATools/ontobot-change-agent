# -*- coding: utf-8 -*-
"""Onto-crawl API section."""
import re
from os import getcwd
from os.path import join
from pathlib import Path
from typing import Generator

from github import Github

# Token.txt unique to every user.
# For more information:
#   https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
# Save the token in a txt file as named below.
SRC = Path(__file__).parent
TOKEN_FILE = join(SRC, "token.txt")

with open(TOKEN_FILE, "r") as t:
    TOKEN = t.read().rstrip()

# Example for API: https://pygithub.readthedocs.io/en/latest/examples.html


def get_issues(
    repository_name: str,
    title: str,
    label: str = "synonym",
    state: str = "open",
) -> Generator:
    """Get issues of specific states from a Github repository.

    :param repository_name: Name of the repository [org/repo]
    :param search: Regex for title of the issue.
    :param state: State of the issue e.g. open, close etc., defaults to "open"
    :yield: Issue names that match the regex.
    """
    g = Github(TOKEN)
    repo = g.get_repo(repository_name)
    if label:
        label_object = repo.get_label(label)

    issues = repo.get_issues(state=state)
    for issue in issues:
        if title and re.match(title, issue.title):
            yield issue.title
        if label_object and label_object in issue.labels:
            yield issue.title
