package cmd

import (
	"fmt"
	"os"
	"pr-checker-cli/ai"
	"pr-checker-cli/gh"
	"pr-checker-cli/shell"
	"strconv"
	"strings"
	"sync"

	"github.com/rvfet/rich-go"
	"github.com/spf13/cobra"
)

func ProduceComments(prNumber string) string {
	if _, err := strconv.Atoi(prNumber); err != nil {
		return "An error occurred: the PR number you provided is not a real number."
	}

	details := gh.FetchPrDetails(prNumber, shell.DefaultShell())

	rich.Info("Fetched details for your PR...")
	var inputs = []struct {
		details    string
		aiProvider string
	}{
		{details, "anthropic"},
		{details, "openai"},
	}

	ch := make(chan string, 2) // Buffered channel
	var wg sync.WaitGroup

	for _, input := range inputs {
		wg.Add(1)
		go createResponseForChannel(input.details, input.aiProvider, ch, &wg)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	var finalRes string
	for result := range ch {
		finalRes += result + "\n\n"
	}
	rich.Info("PR reviews generated, creating the comment...")
	outUrl := gh.CommentOnPr(prNumber, finalRes+"\n\n---\n\nAutomatically Generated (with 💚) by PR Checker AI", shell.DefaultShell())

	return "Find your comment at: [u]" + outUrl + "[/]"
}

func createResponseForChannel(details, aiProvider string, ch chan<- string, wg *sync.WaitGroup) {
	defer wg.Done()

	switch aiProvider {
	case "anthropic":
		res, err := ai.AnthropicResponse(details)
		if err != nil {
			rich.Error("No response from " + strings.ToTitle(aiProvider))
			ch <- "No response from " + strings.ToTitle(aiProvider)
		} else {
			rich.Info("Produced response by [green][b]Claude 4[/]")
			ch <- "# Claude 4 Sonnet's Review\n\n" + res
		}
	default:
		res, err := ai.OpenAIResponse(details)
		if err != nil {
			rich.Error("No response from " + strings.ToTitle(aiProvider))
			ch <- "No response from " + strings.ToTitle(aiProvider)
		} else {
			rich.Info("Produced response by [red][b]GPT-5[/]")
			ch <- "# GPT-5's Review\n\n" + res
		}
	}
}

var rootCmd = &cobra.Command{
	Use:   "pr-checker-cli",
	Short: "pr-checker-cli is a CLI tool for reviewing PRs on GitHub using AI and gh toolbox.",
	Long:  "pr-checker-cli is a CLI tool for reviewing PRs on GitHub, using Claude 4 Sonnet from Anthropic and GPT-5 from OpenAI, as well as leveraging the gh CLI toolbox for fetching PR details and publishing comments.",
	Run: func(cmd *cobra.Command, args []string) {
		cmd.Help()
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Oops. An error while executing pr-checker-cli '%s'\n", err)
		os.Exit(1)
	}
}

var prNumber string

var fetchCmd = &cobra.Command{
	Use:     "check",
	Aliases: []string{"c"},
	Short:   "Check a PR with the given number",
	Long:    "Check a PR with a given number, passing it with the -p/--pr flag.",
	Run: func(cmd *cobra.Command, args []string) {
		if prNumber == "" {
			fmt.Fprintf(os.Stderr, "Error: PR number is required, use the -p/--pr flag.\n")
			os.Exit(1)
		}
		commentUrl := ProduceComments(prNumber)
		rich.Print(commentUrl)
	},
}

func init() {
	fetchCmd.Flags().StringVarP(&prNumber, "pr", "p", "", "Number of the PR you would like to review")
	fetchCmd.MarkFlagRequired("pr")

	rootCmd.AddCommand(fetchCmd)
}
