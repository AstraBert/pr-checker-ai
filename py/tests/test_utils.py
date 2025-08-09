import pytest
import time
from typing import List

from pr_checker_ai.utils import Shell, filter_anthropic_response, filter_openai_response
from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputRefusal,
    Response,
    ResponseOutputText,
)
from anthropic.types import TextBlock, Message, Usage, ThinkingBlock
from subprocess import CompletedProcess


def mock_run_factory(
    command: str, shell: bool, capture_output: bool
) -> CompletedProcess:
    if command != "git hello":
        return CompletedProcess(
            args=command, returncode=0, stdout=b"hello world", stderr=b""
        )
    return CompletedProcess(
        args=command, returncode=1, stdout=b"", stderr=b"Command is not allowed"
    )


@pytest.fixture
def sh() -> Shell:
    return Shell(run_factory=mock_run_factory)


@pytest.fixture
def openai_responses() -> List[Response]:
    return [
        Response(
            id="1",
            created_at=time.time(),
            parallel_tool_calls=False,
            tools=[],
            tool_choice="none",
            output=[
                ResponseOutputMessage(
                    content=[
                        ResponseOutputText(
                            text="hello", annotations=[], type="output_text"
                        )
                    ],
                    id="1",
                    role="assistant",
                    status="completed",
                    type="message",
                )
            ],
            model="gpt-5",
            object="response",
        ),
        Response(
            id="2",
            created_at=time.time(),
            parallel_tool_calls=False,
            tools=[],
            tool_choice="none",
            output=[
                ResponseOutputMessage(
                    content=[
                        ResponseOutputText(
                            text="hello", annotations=[], type="output_text"
                        ),
                        ResponseOutputText(
                            text="world", annotations=[], type="output_text"
                        ),
                    ],
                    id="2",
                    role="assistant",
                    status="completed",
                    type="message",
                )
            ],
            model="gpt-5",
            object="response",
        ),
        Response(
            id="3",
            created_at=time.time(),
            parallel_tool_calls=False,
            tools=[],
            tool_choice="none",
            output=[
                ResponseOutputMessage(
                    content=[ResponseOutputRefusal(refusal="", type="refusal")],
                    id="3",
                    role="assistant",
                    status="completed",
                    type="message",
                )
            ],
            model="gpt-5",
            object="response",
        ),
    ]


@pytest.fixture
def anthropic_responses() -> List[Message]:
    return [
        Message(
            id="1",
            content=[TextBlock(text="hello", type="text")],
            model="claude-sonnet-4-0",
            role="assistant",
            type="message",
            usage=Usage(input_tokens=10, output_tokens=10),
        ),
        Message(
            id="2",
            content=[
                TextBlock(text="hello", type="text"),
                TextBlock(text="world", type="text"),
            ],
            model="claude-sonnet-4-0",
            role="assistant",
            type="message",
            usage=Usage(input_tokens=10, output_tokens=10),
        ),
        Message(
            id="3",
            content=[ThinkingBlock(signature="", thinking="", type="thinking")],
            model="claude-sonnet-4-0",
            role="assistant",
            type="message",
            usage=Usage(input_tokens=10, output_tokens=10),
        ),
    ]


def test_shell(sh: Shell) -> None:
    assert sh.run("git --help") == "hello world"
    assert sh.run("gh repo") == "hello world"
    assert "An error occurred:\n\n" in sh.run("git hello")


def test_filter_openai_responses(openai_responses: List[Response]) -> None:
    assert "hello\n" == filter_openai_response(openai_responses[0])
    assert "hello\nworld\n" == filter_openai_response(openai_responses[1])
    assert "" == filter_openai_response(openai_responses[2])


def test_filter_anthropic_responses(anthropic_responses: List[Message]) -> None:
    assert "hello\n" == filter_anthropic_response(anthropic_responses[0])
    assert "hello\nworld\n" == filter_anthropic_response(anthropic_responses[1])
    assert "" == filter_anthropic_response(anthropic_responses[2])
