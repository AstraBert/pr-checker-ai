package ai

import (
	"context"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/openai/openai-go/v2"
)

func OpenAIResponse(message string) (string, error) {
	client := openai.NewClient()
	chatCompletion, err := client.Chat.Completions.New(context.TODO(), openai.ChatCompletionNewParams{
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.SystemMessage("Thoroughly review the PRs you are given, including references to the changes enacted by the PR and to any other relevant detail. Produce also an approved/not approve statement in the end"),
			openai.UserMessage(message),
		},
		Model: openai.ChatModelGPT5,
	})
	if err != nil {
		return err.Error(), err
	}

	content := ""

	for _, choice := range chatCompletion.Choices {
		if choice.Message.Content != "" {
			content += choice.Message.Content + "\n"
		}
	}

	return content, nil
}

func AnthropicResponse(message string) (string, error) {
	client := anthropic.NewClient()
	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeSonnet4_0,
		MaxTokens: 1024,
		System: []anthropic.TextBlockParam{
			{Text: "Thoroughly review the PRs you are given, including references to the changes enacted by the PR and to any other relevant detail. Produce also an approved/not approve statement in the end"},
		},
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(message)),
		},
	})
	if err != nil {
		return err.Error(), err
	}

	content := ""

	for _, block := range response.Content {
		if val, ok := any(block).(*anthropic.TextBlock); ok {
			content += val.Text + "\n"
		}
	}

	return content, nil
}
