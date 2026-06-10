package app

// Options contains the command-line inputs accepted by the application.
type Options struct {
	Model       string
	OS          string
	Skill       string
	Config      string
	Destination string
	Owner       string
	Repository  string
	Ref         string
	Force       bool
	DryRun      bool
	ListSkills  bool
}
