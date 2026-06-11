package main

import (
	"bytes"
	"context"
	"strings"
	"testing"
)

func TestRunHelp(t *testing.T) {
	t.Parallel()

	var stdout, stderr bytes.Buffer
	code := run(context.Background(), []string{"--help"}, &stdout, &stderr)

	if code != 0 {
		t.Fatalf("run() code = %d, want 0", code)
	}
	if !strings.Contains(stderr.String(), "Usage:") {
		t.Fatalf("help output does not contain usage: %s", stderr.String())
	}
	if !strings.Contains(stderr.String(), "--list-sk") {
		t.Fatalf("help output does not contain --list-sk: %s", stderr.String())
	}
	if strings.Contains(stderr.String(), "--list-skills") {
		t.Fatalf("help output still contains --list-skills: %s", stderr.String())
	}
	if !strings.Contains(stderr.String(), "--local") {
		t.Fatalf("help output does not contain --local: %s", stderr.String())
	}
}

func TestRunRejectsIncompleteInstallOptions(t *testing.T) {
	t.Parallel()

	var stdout, stderr bytes.Buffer
	code := run(context.Background(), []string{"--model", "codex"}, &stdout, &stderr)

	if code != 2 {
		t.Fatalf("run() code = %d, want 2", code)
	}
	if !strings.Contains(stderr.String(), "--model and --skill are required") {
		t.Fatalf("error output does not explain required flags: %s", stderr.String())
	}
}

func TestRunRejectsRemovedListSkillsFlag(t *testing.T) {
	t.Parallel()

	var stdout, stderr bytes.Buffer
	code := run(context.Background(), []string{"--list-skills"}, &stdout, &stderr)

	if code != 2 {
		t.Fatalf("run() code = %d, want 2", code)
	}
	if !strings.Contains(stderr.String(), "flag provided but not defined: -list-skills") {
		t.Fatalf("error output does not explain removed flag: %s", stderr.String())
	}
}
