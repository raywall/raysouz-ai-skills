package app

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type fakeSkillSource struct {
	content string
	called  bool
}

func (f *fakeSkillSource) DownloadSkill(_ context.Context, _, _, _, _, destination string) error {
	f.called = true
	if err := os.MkdirAll(destination, 0o755); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(destination, "SKILL.md"), []byte(f.content), 0o644)
}

func TestServiceInstall(t *testing.T) {
	t.Parallel()

	source := &fakeSkillSource{content: "# Installed"}
	destination := t.TempDir()
	service := NewService(source, io.Discard)

	err := service.Execute(context.Background(), Options{
		Model:       "codex",
		OS:          "auto",
		Skill:       "example",
		Destination: destination,
		Owner:       "raywall",
		Repository:  "raysouz-ai-skills",
		Ref:         "main",
	})
	if err != nil {
		t.Fatalf("Execute() error = %v", err)
	}
	if !source.called {
		t.Fatal("skill source was not called")
	}
	data, err := os.ReadFile(filepath.Join(destination, "example", "SKILL.md"))
	if err != nil {
		t.Fatalf("read installed skill: %v", err)
	}
	if string(data) != source.content {
		t.Fatalf("installed content = %q, want %q", data, source.content)
	}
}

func TestServiceInstallDryRun(t *testing.T) {
	t.Parallel()

	source := &fakeSkillSource{}
	destination := filepath.Join(t.TempDir(), "skills")
	service := NewService(source, io.Discard)

	err := service.Execute(context.Background(), Options{
		Model:       "codex",
		OS:          "auto",
		Skill:       "example",
		Destination: destination,
		DryRun:      true,
	})
	if err != nil {
		t.Fatalf("Execute() error = %v", err)
	}
	if source.called {
		t.Fatal("skill source was called during dry run")
	}
	if _, err := os.Stat(destination); !os.IsNotExist(err) {
		t.Fatalf("destination was created during dry run: %v", err)
	}
}

func TestServiceConfigure(t *testing.T) {
	workingDirectory := t.TempDir()
	previous, err := os.Getwd()
	if err != nil {
		t.Fatalf("get working directory: %v", err)
	}
	if err := os.Chdir(workingDirectory); err != nil {
		t.Fatalf("change working directory: %v", err)
	}
	t.Cleanup(func() {
		if err := os.Chdir(previous); err != nil {
			t.Errorf("restore working directory: %v", err)
		}
	})

	service := NewService(nil, io.Discard)
	if err := service.Execute(context.Background(), Options{Config: "devin", OS: "auto"}); err != nil {
		t.Fatalf("Execute() error = %v", err)
	}
	data, err := os.ReadFile(filepath.Join(".devin", "config.json"))
	if err != nil {
		t.Fatalf("read config: %v", err)
	}
	if !strings.Contains(string(data), `"model": "devin"`) {
		t.Fatalf("config does not contain model: %s", data)
	}
}
