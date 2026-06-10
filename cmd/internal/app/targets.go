package app

import (
	"fmt"
	"path/filepath"
	"runtime"
	"strings"
)

var modelDirectories = map[string]string{
	"claude":   ".claude",
	"codex":    ".codex",
	"copilot":  ".copilot",
	"cursor":   ".cursor",
	"devin":    ".devin",
	"gemini":   ".gemini",
	"windsurf": ".windsurf",
}

func normalizeModel(model string) (string, error) {
	model = strings.ToLower(strings.TrimSpace(model))
	if _, ok := modelDirectories[model]; !ok {
		return "", fmt.Errorf("%w: unsupported model %q", ErrInvalidOptions, model)
	}
	return model, nil
}

func normalizeOS(targetOS string) (string, error) {
	targetOS = strings.ToLower(strings.TrimSpace(targetOS))
	if targetOS == "" || targetOS == "auto" {
		return runtime.GOOS, nil
	}
	switch targetOS {
	case "darwin", "linux", "windows":
		return targetOS, nil
	default:
		return "", fmt.Errorf("%w: unsupported operating system %q", ErrInvalidOptions, targetOS)
	}
}

func installationDirectory(model, targetOS, home, override string) (string, error) {
	if override != "" {
		return filepath.Abs(override)
	}
	resolvedOS, err := normalizeOS(targetOS)
	if err != nil {
		return "", err
	}
	if resolvedOS != runtime.GOOS {
		return "", fmt.Errorf("%w: --os %s requires --destination when running on %s", ErrInvalidOptions, resolvedOS, runtime.GOOS)
	}
	model, err = normalizeModel(model)
	if err != nil {
		return "", err
	}
	return filepath.Join(home, modelDirectories[model], "skills"), nil
}
