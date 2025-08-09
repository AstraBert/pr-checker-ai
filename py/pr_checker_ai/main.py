import os
import sys
import asyncio
import shlex

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from argparse import ArgumentParser
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from .gh import fetch_pr_details, comment_on_pr
from .utils import filter_openai_response, filter_anthropic_response


async def run() -> int:
    cs = Console()
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--pr", help="Number of pull request to be checked", required=True
    )
    parser.add_argument(
        "-o", "--openai", help="OpenAI model to use", required=False, default="gpt-4.1"
    )
    parser.add_argument(
        "-a",
        "--anthropic",
        help="Anthropic model to use",
        required=False,
        default="claude-sonnet-4-0",
    )
    args = parser.parse_args()
    if os.getenv("OPENAI_API_KEY", None) and os.getenv("ANTHROPIC_API_KEY", None):
        openai_client = AsyncOpenAI()
        anthropic_client = AsyncAnthropic()
    else:
        cs.print("Error:", style="bold red")
        cs.print(
            Markdown(
                "`OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` are not available in your environment. _Exiting..._"
            )
        )
        return 1
    pr_number = args.pr
    openai_model = args.openai
    anthropic_model = args.anthropic
    with cs.status("[bold cyan]Checking your PR...") as _:
        details = fetch_pr_details(pr_number=pr_number)
        cs.log("Collected details from your PR")
        openai_response = await openai_client.responses.create(
            input=[
                {
                    "role": "developer",
                    "content": "Thoroughly review the PRs you are given, including references to the changes enacted by the PR and to any other relevant detail. Produce also an approved/not approve statement in the end",
                },
                {"role": "user", "content": details},
            ],
            model=openai_model,
        )
        cs.log("Produced response by OpenAI")
        anthropic_response = await anthropic_client.messages.create(
            model=anthropic_model,
            max_tokens=10000,
            system="Thoroughly review the PRs you are given, including references to the changes enacted by the PR and to any other relevant detail. Produce also an approved/not approve statement in the end",
            messages=[{"role": "user", "content": details}],
        )
        cs.log("Produced response by Anthropic")
        ores = filter_openai_response(openai_response)
        antres = filter_anthropic_response(anthropic_response)
        if (ores != "") and (antres != ""):
            comment_html = shlex.quote(
                f"# PR Review\n\n## OpenAI - {openai_model}\n\n{ores}\n\n## Anthropic - {anthropic_model}\n\n{antres}\n\n---\n\n_Automatically created by PR Checker AI💚_"
            )
            cs.print("Submitted PR comment:", style="bold red")
            print()
            table = Table()
            table.title = "PR Review"
            table.add_column(f"OpenAI - {openai_model}")
            table.add_column(f"Anthropic - {anthropic_model}")
            table.add_row(Markdown(ores), Markdown(antres))
            cs.print(table)
            comment_url = comment_on_pr(pr_number=pr_number, comment=comment_html)
            print()
            cs.print(Markdown(f"View your comment at: [{comment_url}]({comment_url})"))
            return 0
        else:
            cs.print("Error:", style="bold red")
            cs.print(
                Markdown(
                    "There was an error in producing the response by the AI models, retry soon! _Exiting..._"
                )
            )
            return 1


def main() -> None:
    status = asyncio.run(run())
    if status != 0:
        raise RuntimeError("PR checker failed reviewing your PR")
    else:
        sys.exit(0)
