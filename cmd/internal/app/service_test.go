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
	skills  []string
}

func (f *fakeSkillSource) DownloadSkill(_ context.Context, _, _, _, _, destination string) error {
	f.called = true
	if err := os.MkdirAll(destination, 0o755); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(destination, "SKILL.md"), []byte(f.content), 0o644)
}

func (f *fakeSkillSource) ListSkills(_ context.Context, _, _, _ string) ([]string, error) {
	f.called = true
	return f.skills, nil
}

func TestServiceListSkills(t *testing.T) {
	t.Parallel()

	source := &fakeSkillSource{skills: []string{"ddd-context-mapping", "go-clean-architecture"}}
	var output strings.Builder
	service := NewService(source, &output)

	err := service.Execute(context.Background(), Options{
		ListSkills: true,
		Owner:      "raywall",
		Repository: "raysouz-ai-skills",
		Ref:        "main",
	})
	if err != nil {
		t.Fatalf("Execute() error = %v", err)
	}
	for _, skill := range source.skills {
		if !strings.Contains(output.String(), skill) {
			t.Fatalf("output does not contain %q: %s", skill, output.String())
		}
	}
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

func TestServiceInstallLocal(t *testing.T) {
	t.Parallel()

	sourceDirectory := filepath.Join(t.TempDir(), "local-example")
	if err := os.MkdirAll(filepath.Join(sourceDirectory, "references"), 0o755); err != nil {
		t.Fatalf("create local skill: %v", err)
	}
	if err := os.WriteFile(filepath.Join(sourceDirectory, "SKILL.md"), []byte("# Local"), 0o644); err != nil {
		t.Fatalf("write local SKILL.md: %v", err)
	}
	if err := os.WriteFile(filepath.Join(sourceDirectory, "references", "info.md"), []byte("info"), 0o644); err != nil {
		t.Fatalf("write local reference: %v", err)
	}

	remoteSource := &fakeSkillSource{}
	destination := t.TempDir()
	service := NewService(remoteSource, io.Discard)

	err := service.Execute(context.Background(), Options{
		Model:       "codex",
		OS:          "auto",
		Skill:       sourceDirectory,
		Local:       true,
		Destination: destination,
	})
	if err != nil {
		t.Fatalf("Execute() error = %v", err)
	}
	if remoteSource.called {
		t.Fatal("remote skill source was called during local installation")
	}
	for _, relative := range []string{"SKILL.md", filepath.Join("references", "info.md")} {
		if _, err := os.Stat(filepath.Join(destination, "local-example", relative)); err != nil {
			t.Fatalf("installed local file %q: %v", relative, err)
		}
	}
}

func TestServiceRejectsLocalDirectoryWithoutSkillFile(t *testing.T) {
	t.Parallel()

	sourceDirectory := filepath.Join(t.TempDir(), "invalid-local")
	if err := os.MkdirAll(sourceDirectory, 0o755); err != nil {
		t.Fatalf("create local directory: %v", err)
	}

	service := NewService(&fakeSkillSource{}, io.Discard)
	err := service.Execute(context.Background(), Options{
		Model: "codex",
		OS:    "auto",
		Skill: sourceDirectory,
		Local: true,
	})
	if err == nil {
		t.Fatal("Execute() error = nil, want invalid options error")
	}
	if !strings.Contains(err.Error(), "must contain SKILL.md") {
		t.Fatalf("Execute() error = %v, want missing SKILL.md explanation", err)
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
