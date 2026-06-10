# rayskills

CLI em Go para instalar skills de `github.com/raywall/raysouz-ai-skills` no
diretório global do modelo alvo. O layout novo `skills/<nome>` e o layout
legado `<nome>` na raiz são suportados.

## Uso

```bash
go run . --model codex --skill go-clean-architecture
go run . --model claude --skill ddd-context-mapping --os darwin
go run . --model devin --skill workflow-architecture --force
go run . --config devin
```

Modelos suportados: `codex`, `claude`, `devin`, `cursor`, `gemini`, `windsurf`
e `copilot`. Por padrão, uma skill é instalada em `~/.<model>/skills/<skill>`.

O modo `--config <model>` cria `./.<model>/config.json` no projeto atual.

Use `--destination` para substituir o diretório de instalação, `--ref` para
baixar outra branch/tag/commit, `--dry-run` para apenas exibir as ações e
`GITHUB_TOKEN` para acessar repositórios privados ou evitar limites anônimos.
Ao informar um `--os` diferente do sistema em execução, informe também
`--destination`, pois o diretório home do outro sistema não pode ser inferido.

## Build

```bash
go build -o rayskills .
go test -race ./...
```

## Releases

O workflow `.github/workflows/release.yml` publica binários para Linux, Windows
e macOS, nas arquiteturas `amd64` e `arm64`. Para criar uma release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Os arquivos compactados e o `checksums.txt` serão anexados à GitHub Release.
O workflow também pode ser executado manualmente para republicar uma tag
existente.
