import pytest

from subprocess import CompletedProcess
from pr_checker_ai.utils import Shell
from pr_checker_ai.gh import fetch_pr_details, comment_on_pr


def mock_run_factory(
    command: str, shell: bool, capture_output: bool
) -> CompletedProcess:
    return CompletedProcess(
        args=command, returncode=0, stdout=bytes(command, encoding="utf-8"), stderr=b""
    )


@pytest.fixture
def sh() -> Shell:
    return Shell(run_factory=mock_run_factory)


def test_fetch_pr_details(sh: Shell) -> None:
    res = fetch_pr_details("7", sh)
    assert (
        "## General PR info\n\ngh pr view 7\n\n## Changes related to the PR\n\ngh pr diff 7"
        == res
    )


def test_comment_on_pr(sh: Shell) -> None:
    res = comment_on_pr(pr_number="7", comment="hello world", shell=sh)
    assert res == "gh pr comment 7 --body hello world"
