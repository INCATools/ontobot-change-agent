# -*- coding: utf-8 -*-

"""Test all CLI commands."""

import unittest

from click.testing import CliRunner

from ontobot_change_agent.api import ONTOLOGY_RESOURCE, TESTS, TOKEN
from ontobot_change_agent.cli import get_labels, issues, process_issue


class TestVersion(unittest.TestCase):
    """Test all CLI commands."""

    def setUp(self):
        """Set up variables."""
        runner = CliRunner(mix_stderr=False)
        self.runner = runner
        self.repo_name = "hrshdhgd/ontobot-change-agent"
        self.resource = str(ONTOLOGY_RESOURCE)
        self.token = TOKEN
        self.output = TESTS / "resources/tmp/test.obo"

    def test_get_issues(self):
        """Test get_issues CLI command."""
        result = self.runner.invoke(issues, ["--label", "test", "--repo", self.repo_name])
        result.stdout
        result.stderr
        self.assertEqual(0, result.exit_code)

    def test_get_labels(self):
        """Test get_labels CLI command."""
        result = self.runner.invoke(get_labels, ["--repo", self.repo_name])
        result.stdout
        result.stderr
        self.assertEqual(0, result.exit_code)

    def test_process_issues(self):
        """Test process_issue CLI command."""
        result = self.runner.invoke(
            process_issue,
            [
                self.resource,
                "--repo",
                self.repo_name,
                "-n",
                30,
                "-o",
                self.output,
            ],
        )
        result.stdout
        result.stderr
        self.assertEqual(0, result.exit_code)

    # def test_process_issues_fail(self):
    #     """Test process_issue CLI command."""
    #     result = self.runner.invoke(
    #         process_issue,
    #         [
    #             self.resource,
    #             "--repo",
    #             self.repo_name,
    #             "-n",
    #             10,
    #             "-o",
    #             self.output,
    #         ],
    #     )
    #     self.assertIsInstance(result.exception, ValueError)
