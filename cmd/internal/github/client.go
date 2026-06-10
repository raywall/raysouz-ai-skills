package github

import (
	"archive/tar"
	"compress/gzip"
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"
)

// Client downloads skill folders from GitHub repository tarballs.
type Client struct {
	httpClient *http.Client
	token      string
}

// NewClient creates a GitHub client. The token may be empty for public repositories.
func NewClient(token string) *Client {
	return &Client{
		httpClient: &http.Client{Timeout: 2 * time.Minute},
		token:      token,
	}
}

// DownloadSkill downloads and extracts skills/<skill> from a GitHub repository.
func (c *Client) DownloadSkill(ctx context.Context, owner, repository, ref, skill, destination string) error {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/tarball/%s", owner, repository, ref)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return fmt.Errorf("create GitHub request: %w", err)
	}
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("User-Agent", "rayskills")
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("download repository: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(io.LimitReader(resp.Body, 1024))
		return fmt.Errorf("download repository: GitHub returned %s: %s", resp.Status, strings.TrimSpace(string(body)))
	}
	if err := extractSkill(resp.Body, skill, destination); err != nil {
		return fmt.Errorf("extract skill %q: %w", skill, err)
	}
	return nil
}

func extractSkill(reader io.Reader, skill, destination string) error {
	gz, err := gzip.NewReader(reader)
	if err != nil {
		return fmt.Errorf("open gzip stream: %w", err)
	}
	defer gz.Close()

	found := false
	tr := tar.NewReader(gz)
	for {
		header, err := tr.Next()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			return fmt.Errorf("read tarball: %w", err)
		}

		parts := strings.SplitN(path.Clean(header.Name), "/", 2)
		if len(parts) != 2 {
			continue
		}
		relative, ok := skillRelativePath(parts[1], skill)
		if !ok {
			continue
		}
		target := filepath.Join(destination, filepath.FromSlash(relative))
		if !within(destination, target) {
			return fmt.Errorf("unsafe archive path %q", header.Name)
		}

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, 0o755); err != nil {
				return fmt.Errorf("create directory: %w", err)
			}
			found = true
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
				return fmt.Errorf("create parent directory: %w", err)
			}
			file, err := os.OpenFile(target, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, os.FileMode(header.Mode)&0o755)
			if err != nil {
				return fmt.Errorf("create file: %w", err)
			}
			_, copyErr := io.Copy(file, tr)
			closeErr := file.Close()
			if copyErr != nil {
				return fmt.Errorf("extract file: %w", copyErr)
			}
			if closeErr != nil {
				return fmt.Errorf("close file: %w", closeErr)
			}
			found = true
		}
	}
	if !found {
		return errors.New("skill was not found in repository")
	}
	return nil
}

func skillRelativePath(archivePath, skill string) (string, bool) {
	for _, prefix := range []string{"skills/" + skill, skill} {
		relative, ok := strings.CutPrefix(archivePath, prefix)
		if ok && (relative == "" || strings.HasPrefix(relative, "/")) {
			return strings.TrimPrefix(relative, "/"), true
		}
	}
	return "", false
}

func within(parent, target string) bool {
	relative, err := filepath.Rel(parent, target)
	return err == nil && relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator))
}
