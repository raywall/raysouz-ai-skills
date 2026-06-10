package github

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"os"
	"path/filepath"
	"testing"
)

func TestExtractSkill(t *testing.T) {
	t.Parallel()

	archive := makeArchive(t, map[string]string{
		"raywall-repo/README.md":                         "repo",
		"raywall-repo/skills/example/SKILL.md":           "# Example",
		"raywall-repo/skills/example/references/info.md": "info",
		"raywall-repo/skills/other/SKILL.md":             "# Other",
	})
	destination := filepath.Join(t.TempDir(), "example")

	if err := extractSkill(bytes.NewReader(archive), "example", destination); err != nil {
		t.Fatalf("extractSkill() error = %v", err)
	}
	data, err := os.ReadFile(filepath.Join(destination, "SKILL.md"))
	if err != nil {
		t.Fatalf("read extracted file: %v", err)
	}
	if string(data) != "# Example" {
		t.Fatalf("SKILL.md = %q, want %q", data, "# Example")
	}
	if _, err := os.Stat(filepath.Join(destination, "..", "other", "SKILL.md")); !os.IsNotExist(err) {
		t.Fatalf("unexpected other skill extracted: %v", err)
	}
}

func TestExtractSkillNotFound(t *testing.T) {
	t.Parallel()
	archive := makeArchive(t, map[string]string{"repo/skills/other/SKILL.md": "# Other"})

	if err := extractSkill(bytes.NewReader(archive), "missing", t.TempDir()); err == nil {
		t.Fatal("expected error")
	}
}

func TestExtractSkillFromLegacyRootLayout(t *testing.T) {
	t.Parallel()

	archive := makeArchive(t, map[string]string{
		"raywall-repo/example/SKILL.md": "# Legacy",
	})
	destination := filepath.Join(t.TempDir(), "example")

	if err := extractSkill(bytes.NewReader(archive), "example", destination); err != nil {
		t.Fatalf("extractSkill() error = %v", err)
	}
	data, err := os.ReadFile(filepath.Join(destination, "SKILL.md"))
	if err != nil {
		t.Fatalf("read extracted file: %v", err)
	}
	if string(data) != "# Legacy" {
		t.Fatalf("SKILL.md = %q, want %q", data, "# Legacy")
	}
}

func makeArchive(t *testing.T, files map[string]string) []byte {
	t.Helper()
	var buffer bytes.Buffer
	gz := gzip.NewWriter(&buffer)
	tarWriter := tar.NewWriter(gz)
	for name, content := range files {
		header := &tar.Header{Name: name, Mode: 0o644, Size: int64(len(content)), Typeflag: tar.TypeReg}
		if err := tarWriter.WriteHeader(header); err != nil {
			t.Fatalf("write tar header: %v", err)
		}
		if _, err := tarWriter.Write([]byte(content)); err != nil {
			t.Fatalf("write tar body: %v", err)
		}
	}
	if err := tarWriter.Close(); err != nil {
		t.Fatalf("close tar writer: %v", err)
	}
	if err := gz.Close(); err != nil {
		t.Fatalf("close gzip writer: %v", err)
	}
	return buffer.Bytes()
}
