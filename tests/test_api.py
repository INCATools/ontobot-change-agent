# -*- coding: utf-8 -*-

"""Test all API functions."""

import unittest

from github.Issue import Issue

from onto_crawler.api import TOKEN, get_all_labels_from_repo, get_issues


class TestAPI(unittest.TestCase):
    """Test all API functions."""

    def setUp(self) -> None:
        """Set up variables."""
        self.repo_name = "hrshdhgd/onto-crawler"
        self.token = TOKEN
        self.label = "test"
        self.issue_title = "Test issue"

    def test_get_issues_with_label(self):
        """Test if 'get_issues' returns the correct label."""
        issues = []
        for issue in get_issues(
            repository_name=self.repo_name, label=self.label
        ):
            issues.append(issue)
        
        self.assertEqual(len(issues), 1)
        self.assertTrue(type(issues[0]), Issue)
        self.assertTrue(issues[0]['number'], 2)
        self.assertTrue(issues[0]['title'], self.issue_title)
        self.assertTrue(issues[0]['labels'][0]['name'], self.label)

    def test_get_issues_with_title(self):
        """Test if 'get_issues' returns the correct title."""
        issues = []
        for issue in get_issues(
            repository_name=self.repo_name, title_search=self.issue_title
        ):
            issues.append(issue)

        self.assertEqual(len(issues), 1)
        self.assertTrue(type(issues[0]), Issue)
        self.assertTrue(issues[0]['number'], 2)
        self.assertTrue(issues[0]['title'], self.issue_title)
        self.assertTrue(issues[0]['labels'][0]['name'], self.label)

    def test_get_issues_with_number(self):
        """Test return the correct issue by number."""
        issues = []
        for issue in get_issues(repository_name=self.repo_name, number=2):
            issues.append(issue)

        self.assertEqual(len(issues), 1)

    def test_get_all_labels_from_repo(self):
        """Test if get labels returns the correct dict of labels."""
        label_dict = {}
        label_dict = get_all_labels_from_repo(self.repo_name)

        self.assertEqual(len(label_dict), 10)
