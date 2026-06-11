package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
)

// ErrInvalidOptions indicates invalid or incomplete command-line options.
var ErrInvalidOptions = errors.New("invalid options")

var validSkillName = regexp.MustCompile(`^[a-zA-Z0-9][a-zA-Z0-9._-]*$`)

// SkillSource downloads a skill directory from a repository.
type SkillSource interface {
	DownloadSkill(ctx context.Context, owner, repository, ref, skill, destination string) error
	ListSkills(ctx context.Context, owner, repository, ref string) ([]string, error)
}

// Service executes skill installation and model configuration use cases.
type Service struct {
	source SkillSource
	out    io.Writer
}

// NewService creates a command application service.
func NewService(source SkillSource, out io.Writer) *Service {
	return &Service{source: source, out: out}
}

// Execute validates options and runs either configuration or skill installation.
func (s *Service) Execute(ctx context.Context, opts Options) error {
	if opts.ListSkills {
		return s.listSkills(ctx, opts)
	}
	if opts.Config != "" {
		return s.configure(opts)
	}
	return s.install(ctx, opts)
}

func (s *Service) listSkills(ctx context.Context, opts Options) error {
	skills, err := s.source.ListSkills(ctx, opts.Owner, opts.Repository, opts.Ref)
	if err != nil {
		return err
	}
	if len(skills) == 0 {
		return errors.New("no skills found under the repository skills/ directory")
	}
	fmt.Fprintf(s.out, "Available skills in github.com/%s/%s/tree/%s/skills:\n", opts.Owner, opts.Repository, opts.Ref)
	for _, skill := range skills {
		fmt.Fprintf(s.out, "%s\n", skill)
	}
	return nil
}

func (s *Service) install(ctx context.Context, opts Options) error {
	if opts.Model == "" || opts.Skill == "" {
		return fmt.Errorf("%w: --model and --skill are required for installation", ErrInvalidOptions)
	}
	skillName := opts.Skill
	if opts.Local {
		var err error
		skillName, err = localSkillName(opts.Skill)
		if err != nil {
			return err
		}
	} else if !validSkillName.MatchString(skillName) {
		return fmt.Errorf("%w: invalid skill name %q", ErrInvalidOptions, skillName)
	}

	home, err := os.UserHomeDir()
	if err != nil {
		return fmt.Errorf("resolve user home: %w", err)
	}
	destination, err := installationDirectory(opts.Model, opts.OS, home, opts.Destination)
	if err != nil {
		return err
	}
	skillDestination := filepath.Join(destination, skillName)
	if exists(skillDestination) && !opts.Force {
		return fmt.Errorf("skill already exists at %s; use --force to replace it", skillDestination)
	}

	fmt.Fprintf(s.out, "Installing %s for %s at %s\n", skillName, opts.Model, skillDestination)
	if opts.DryRun {
		return nil
	}

	parent := filepath.Dir(destination)
	if err := os.MkdirAll(parent, 0o755); err != nil {
		return fmt.Errorf("create destination parent: %w", err)
	}
	temp, err := os.MkdirTemp(parent, ".rayskills-*")
	if err != nil {
		return fmt.Errorf("create temporary directory: %w", err)
	}
	defer os.RemoveAll(temp)

	staged := filepath.Join(temp, skillName)
	if opts.Local {
		if err := copyLocalSkill(opts.Skill, staged); err != nil {
			return err
		}
	} else {
		if err := s.source.DownloadSkill(ctx, opts.Owner, opts.Repository, opts.Ref, opts.Skill, staged); err != nil {
			return err
		}
	}
	if err := os.MkdirAll(destination, 0o755); err != nil {
		return fmt.Errorf("create destination: %w", err)
	}
	if opts.Force {
		if err := os.RemoveAll(skillDestination); err != nil {
			return fmt.Errorf("replace existing skill: %w", err)
		}
	}
	if err := os.Rename(staged, skillDestination); err != nil {
		return fmt.Errorf("install skill: %w", err)
	}
	fmt.Fprintf(s.out, "Installed %s\n", skillDestination)
	return nil
}

func localSkillName(source string) (string, error) {
	info, err := os.Stat(source)
	if err != nil {
		return "", fmt.Errorf("%w: access local skill directory %q: %v", ErrInvalidOptions, source, err)
	}
	if !info.IsDir() {
		return "", fmt.Errorf("%w: local skill path %q is not a directory", ErrInvalidOptions, source)
	}
	skillFile, err := os.Stat(filepath.Join(source, "SKILL.md"))
	if err != nil || !skillFile.Mode().IsRegular() {
		return "", fmt.Errorf("%w: local skill directory %q must contain SKILL.md", ErrInvalidOptions, source)
	}
	absolute, err := filepath.Abs(source)
	if err != nil {
		return "", fmt.Errorf("%w: resolve local skill directory %q: %v", ErrInvalidOptions, source, err)
	}
	name := filepath.Base(filepath.Clean(absolute))
	if !validSkillName.MatchString(name) {
		return "", fmt.Errorf("%w: invalid local skill directory name %q", ErrInvalidOptions, name)
	}
	return name, nil
}

func copyLocalSkill(source, destination string) error {
	if err := os.CopyFS(destination, os.DirFS(source)); err != nil {
		return fmt.Errorf("copy local skill %q: %w", source, err)
	}
	return nil
}

func (s *Service) configure(opts Options) error {
	model, err := normalizeModel(opts.Config)
	if err != nil {
		return err
	}
	if _, err := normalizeOS(opts.OS); err != nil {
		return err
	}
	configDir := "." + string(filepath.Separator) + modelDirectories[model]
	configPath := filepath.Join(configDir, "config.json")
	if exists(configPath) && !opts.Force {
		return fmt.Errorf("config already exists at %s; use --force to replace it", configPath)
	}

	fmt.Fprintf(s.out, "Creating %s configuration at %s\n", model, configPath)
	if opts.DryRun {
		return nil
	}
	if err := os.MkdirAll(configDir, 0o755); err != nil {
		return fmt.Errorf("create config directory: %w", err)
	}
	config := struct {
		Model       string `json:"model"`
		SkillsDir   string `json:"skillsDir"`
		GeneratedBy string `json:"generatedBy"`
	}{
		Model:       model,
		SkillsDir:   filepath.ToSlash(filepath.Join(modelDirectories[model], "skills")),
		GeneratedBy: "rayskills",
	}
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal config: %w", err)
	}
	data = append(data, '\n')
	if err := os.WriteFile(configPath, data, 0o644); err != nil {
		return fmt.Errorf("write config: %w", err)
	}
	fmt.Fprintf(s.out, "Created %s\n", configPath)
	return nil
}

func exists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
