package gh

import (
	"fmt"
	"pr-checker-cli/shell"
	"testing"
)

func mockRunFactory(command string) (string, error) {
	return command, nil
}

func TestFetchPrDetails(t *testing.T) {
	shell := shell.NewShell(mockRunFactory)

	var tests = []struct {
		prNumber string
		want     string
	}{
		{"7", fmt.Sprintf("## General PR info\n\n%s\n\n## Changes related to the PR\n\n%s", "gh pr view 7", "gh pr diff 7")},
		{"8", fmt.Sprintf("## General PR info\n\n%s\n\n## Changes related to the PR\n\n%s", "gh pr view 8", "gh pr diff 8")},
		{"9", fmt.Sprintf("## General PR info\n\n%s\n\n## Changes related to the PR\n\n%s", "gh pr view 9", "gh pr diff 9")},
	}

	for _, tt := range tests {
		result := FetchPrDetails(tt.prNumber, shell)
		if result != tt.want {
			t.Errorf("Testing FetchPrDetails: wanting %s, got %s", tt.want, result)
		}
	}
}

func TestCommentOnPr(t *testing.T) {
	shell := shell.NewShell(mockRunFactory)

	var tests = []struct {
		prNumber string
		comment  string
		want     string
	}{
		{"7", "hello world", "gh pr comment 7 --body 'hello world'"},
		{"8", "hello", "gh pr comment 8 --body hello"},
		{"9", "hello friend's dog", "gh pr comment 9 --body 'hello friend'\\''s dog'"},
	}

	for _, tt := range tests {
		result := CommentOnPr(tt.prNumber, tt.comment, shell)
		if result != tt.want {
			t.Errorf("Testing CommentOnPr: wanting %s, got %s", tt.want, result)
		}
	}
}
