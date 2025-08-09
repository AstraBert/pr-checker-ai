from .utils import Shell

sh = Shell()


def fetch_pr_details(pr_number: str, shell: Shell = sh) -> str:
    general_info = shell.run("gh pr view " + pr_number)
    diff = shell.run("gh pr diff " + pr_number)
    return f"## General PR info\n\n{general_info}\n\n## Changes related to the PR\n\n{diff}"


def comment_on_pr(pr_number: str, comment: str, shell: Shell = sh) -> str:
    comment_url = shell.run("gh pr comment " + pr_number + " --body " + comment + "")
    return comment_url
