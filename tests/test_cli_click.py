import pytest
from click.testing import CliRunner

from grsched.__main__ import cmd


class Test_help:
    @pytest.mark.parametrize(
        ["options", "expected"],
        [
            [["-h"], 0],
            [["events", "-h"], 0],
            [["show", "-h"], 0],
            [["users", "-h"], 0],
        ],
    )
    def test_help(self, options, expected):
        runner = CliRunner()
        result = runner.invoke(cmd, options)
        assert result.exit_code == expected


class Test_version_subcmd:
    def test_smoke(self):
        runner = CliRunner()
        result = runner.invoke(cmd, ["version"])
        assert result.exit_code == 0
        assert len(result.stdout) > 30
