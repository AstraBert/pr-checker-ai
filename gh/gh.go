package gh

import (
	"fmt"
	"pr-checker/shell"

	"github.com/kballard/go-shellquote"
)

func FetchPrDetails(prNumber string, sh *shell.Shell) string {
	det, err := sh.Execute("gh pr view " + prNumber)
	if err != nil {
		return err.Error()
	}
	diff, err := sh.Execute("gh pr diff " + prNumber)
	if err != nil {
		return err.Error()
	}
	return fmt.Sprintf("## General PR info\n\n%s\n\n## Changes related to the PR\n\n%s", det, diff)
}

func CommentOnPr(prNumber, comment string, sh *shell.Shell) string {
	commentUrl, err := sh.Execute("gh pr comment " + prNumber + " --body " + shellquote.Join(comment))
	if err != nil {
		return err.Error()
	}
	return commentUrl
}
