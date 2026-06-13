APP := rayskills
GOOS := $(shell go env GOOS)
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo dev)
LDFLAGS := -s -w -X main.version=$(VERSION)

ifeq ($(GOOS),windows)
	BINARY := bin/$(APP).exe
	INSTALL_ROOT := $(USERPROFILE)\rayskills
	INSTALL_BIN := $(INSTALL_ROOT)\bin
	INSTALL_APP := $(INSTALL_BIN)\$(APP).exe
else
	BINARY := bin/$(APP)
	INSTALL_ROOT := $(HOME)/rayskills
	INSTALL_BIN := $(INSTALL_ROOT)/bin
	INSTALL_APP := $(INSTALL_BIN)/$(APP)
	PATH_LINE := export PATH="$$HOME/rayskills/bin:$$PATH"
	ifeq ($(GOOS),darwin)
		PROFILE_FILES := $(HOME)/.zshrc $(HOME)/.profile
	else
		PROFILE_FILES := $(HOME)/.bashrc $(HOME)/.profile
	endif
endif

.PHONY: help build install uninstall test clean

help:
	@echo "Available targets:"
	@echo "  make build      Build $(APP) inside bin/"
	@echo "  make install    Build, install in ~/rayskills/bin, and add it to PATH"
	@echo "  make uninstall  Remove the installed binary and generated PATH entries"
	@echo "  make test       Run tests with the race detector"
	@echo "  make clean      Remove build artifacts"

build:
ifeq ($(GOOS),windows)
	@if not exist bin mkdir bin
	go build -ldflags "$(LDFLAGS)" -o "$(BINARY)" .
else
	@mkdir -p bin
	go build -ldflags "$(LDFLAGS)" -o "$(BINARY)" .
endif
	@echo "Built $(BINARY)"

install: build
ifeq ($(GOOS),windows)
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install.ps1 -Source "$(BINARY)"
else
	@mkdir -p "$(INSTALL_BIN)"
	@cp "$(BINARY)" "$(INSTALL_APP)"
	@chmod +x "$(INSTALL_APP)"
	@for profile in $(PROFILE_FILES); do \
		touch "$$profile"; \
		grep -Fqx '$(PATH_LINE)' "$$profile" || printf '\n%s\n' '$(PATH_LINE)' >> "$$profile"; \
	done
	@echo "Installed $(APP) at $(INSTALL_APP)"
	@echo "Open a new terminal or run: export PATH=\"$$HOME/rayskills/bin:$$PATH\""
endif

uninstall:
ifeq ($(GOOS),windows)
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/uninstall.ps1
else
	@rm -f "$(INSTALL_APP)"
	@for profile in $(PROFILE_FILES); do \
		if [ -f "$$profile" ]; then \
			sed '/^export PATH="[$$]HOME\/rayskills\/bin:[$$]PATH"$$/d' "$$profile" > "$$profile.tmp"; \
			mv "$$profile.tmp" "$$profile"; \
		fi; \
	done
	@echo "Uninstalled $(APP)"
endif

test:
	go test -race ./...

clean:
ifeq ($(GOOS),windows)
	@if exist bin rmdir /s /q bin
else
	rm -rf bin
endif
