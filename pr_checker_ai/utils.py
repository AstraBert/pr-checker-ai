import subprocess as sp

from dataclasses import dataclass
from typing import Callable
from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputRefusal,
    Response,
)
from anthropic.types import TextBlock, Message


@dataclass
class Shell:
    shell: bool = True
    capture_output: bool = True
    run_factory: Callable[..., sp.CompletedProcess] = sp.run

    def run(self, command: str) -> str:
        return self._process_output(
            self.run_factory(
                command, shell=self.shell, capture_output=self.capture_output
            )
        )

    def _process_output(self, output: sp.CompletedProcess) -> str:
        if output.returncode == 0:
            return str(output.stdout, encoding="utf-8")
        else:
            return "An error occurred:\n\n" + str(output.stderr, encoding="utf-8")


def filter_openai_response(response: Response) -> str:
    text = ""
    for item in response.output:
        if isinstance(item, ResponseOutputMessage):
            for piece in item.content:
                if not isinstance(piece, ResponseOutputRefusal):
                    text += piece.text + "\n"
    return text


def filter_anthropic_response(response: Message) -> str:
    text = ""
    for block in response.content:
        if isinstance(block, TextBlock):
            text += block.text + "\n"
    return text
