package app

import (
	"path/filepath"
	"runtime"
	"testing"
)

func TestInstallationDirectory(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name      string
		model     string
		targetOS  string
		override  string
		want      string
		wantError bool
	}{
		{name: "codex", model: "codex", targetOS: runtime.GOOS, want: filepath.Join("/home/user", ".codex", "skills")},
		{name: "case insensitive model", model: "Claude", targetOS: "auto", want: filepath.Join("/home/user", ".claude", "skills")},
		{name: "unsupported model", model: "unknown", targetOS: runtime.GOOS, wantError: true},
		{name: "unsupported operating system", model: "codex", targetOS: "plan9", wantError: true},
		{name: "foreign operating system without destination", model: "codex", targetOS: foreignOS(), wantError: true},
		{name: "foreign operating system with destination", model: "codex", targetOS: foreignOS(), override: "./custom", want: absolutePath(t, "./custom")},
	}

	for _, tc := range tests {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			got, err := installationDirectory(tc.model, tc.targetOS, "/home/user", tc.override)
			if tc.wantError {
				if err == nil {
					t.Fatal("expected error")
				}
				return
			}
			if err != nil {
				t.Fatalf("installationDirectory() error = %v", err)
			}
			if got != tc.want {
				t.Fatalf("installationDirectory() = %q, want %q", got, tc.want)
			}
		})
	}
}

func foreignOS() string {
	if runtime.GOOS == "windows" {
		return "linux"
	}
	return "windows"
}

func absolutePath(t *testing.T, path string) string {
	t.Helper()
	absolute, err := filepath.Abs(path)
	if err != nil {
		t.Fatalf("filepath.Abs() error = %v", err)
	}
	return absolute
}
