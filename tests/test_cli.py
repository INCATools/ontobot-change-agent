# -*- coding: utf-8 -*-

"""Test all CLI commands."""

import unittest
from click.testing import CliRunner
from onto_crawler.api import TOKEN
from onto_crawler.cli import issues

class TestVersion(unittest.TestCase):
    """Test all CLI commands."""

    def setUp(self):
        """Set up variables."""
        runner = CliRunner(mix_stderr=False)
        self.runner = runner
        self.repo_name = "hrshdhgd/onto-crawler"
        self.token = TOKEN

    def test_get_issues(self):
        """Test get_issues CLI command."""
        result = self.runner.invoke(
            issues, ["--label", "test", "--repo", self.repo_name]
        )
        result.stdout
        result.stderr
        self.assertEqual(0, result.exit_code)

