package shell

import (
	"strings"
	"testing"
)

func mockRunFactory(command string) (string, error) {
	return command, nil
}

func TestShell(t *testing.T) {
	shell := DefaultShell()
	_, ok := any(*shell).(Shell)
	if !ok {
		t.Error("Testing DefaultShell: DefaultShell does not produce a Shell instance")
	}
	secondShell := NewShell(mockRunFactory)
	_, secondOk := any(*secondShell).(Shell)
	if !secondOk {
		t.Error("Testing NewShell: NewShell does not produce a Shell instance")
	}
	out, _ := shell.Execute("echo 'hello world'")
	out1, _ := secondShell.Execute("hello world")
	if strings.ReplaceAll(strings.TrimSpace(out), "\n", "") != out1 {
		t.Errorf("Testing Shell.Execute: expected the same output ('hello world'), got two different ones: %s and %s", out, out1)
	}
}
