package main

import (
	"fmt"

	"github.com/kballard/go-shellquote"
)

func main() {
	// Quote a single argument
	quoted := shellquote.Join("hello friend's dog")
	// Result: "hello world"

	fmt.Println(quoted)
}
