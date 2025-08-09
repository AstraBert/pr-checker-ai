package shell

import "os/exec"

type Shell struct {
	RunFactory func(string) (string, error)
}

func defaultExecuteCommand(command string) (string, error) {
	cmd := exec.Command("bash", "-c", command)
	output, err := cmd.CombinedOutput()
	return string(output), err
}

func DefaultShell() *Shell {
	return &Shell{
		RunFactory: defaultExecuteCommand,
	}
}

func NewShell(fn func(string) (string, error)) *Shell {
	return &Shell{
		RunFactory: fn,
	}
}

func (sh *Shell) Execute(command string) (string, error) {
	runFactory := sh.RunFactory
	return runFactory(command)
}
