package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/raywall/raysouz-ai-skills/cmd/internal/app"
	"github.com/raywall/raysouz-ai-skills/cmd/internal/github"
)

var version = "dev"

func main() {
	os.Exit(run(context.Background(), os.Args[1:], os.Stdout, os.Stderr))
}

func run(ctx context.Context, args []string, stdout, stderr io.Writer) int {
	flags := flag.NewFlagSet("rayskills", flag.ContinueOnError)
	flags.SetOutput(stderr)

	var opts app.Options
	flags.StringVar(&opts.Model, "model", "", "target model: codex, claude, devin, cursor, gemini, windsurf, or copilot")
	flags.StringVar(&opts.OS, "os", "auto", "target operating system: auto, darwin, linux, or windows")
	flags.StringVar(&opts.Skill, "skill", "", "skill name under the repository skills/ directory")
	flags.StringVar(&opts.Config, "config", "", "create .<model>/config.json in the current project")
	flags.StringVar(&opts.Destination, "destination", "", "override the skills installation directory")
	flags.StringVar(&opts.Owner, "owner", "raywall", "GitHub repository owner")
	flags.StringVar(&opts.Repository, "repository", "raysouz-ai-skills", "GitHub repository name")
	flags.StringVar(&opts.Ref, "ref", "main", "Git ref to download")
	flags.BoolVar(&opts.Force, "force", false, "replace an existing installed skill or config")
	flags.BoolVar(&opts.DryRun, "dry-run", false, "print actions without writing files")
	showVersion := flags.Bool("version", false, "print version")

	flags.Usage = func() {
		fmt.Fprintln(stderr, "Install AI skills from github.com/raywall.")
		fmt.Fprintln(stderr, "\nUsage:")
		fmt.Fprintln(stderr, "  rayskills --model codex --skill go-clean-architecture")
		fmt.Fprintln(stderr, "  rayskills --config devin")
		fmt.Fprintln(stderr, "\nFlags:")
		flags.PrintDefaults()
	}

	if err := flags.Parse(args); errors.Is(err, flag.ErrHelp) {
		return 0
	} else if err != nil {
		return 2
	}
	if *showVersion {
		fmt.Fprintln(stdout, version)
		return 0
	}

	service := app.NewService(github.NewClient(os.Getenv("GITHUB_TOKEN")), stdout)
	if err := service.Execute(ctx, opts); err != nil {
		fmt.Fprintf(stderr, "error: %v\n", err)
		if errors.Is(err, app.ErrInvalidOptions) {
			flags.Usage()
			return 2
		}
		return 1
	}
	return 0
}
