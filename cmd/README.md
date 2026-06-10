# rayskills

CLI em Go para instalar skills da pasta
`github.com/raywall/raysouz-ai-skills/tree/main/skills` no diretório global do
modelo alvo.

## Uso

```bash
go run . --model codex --skill go-clean-architecture
go run . --list-skills
go run . --model claude --skill ddd-context-mapping --os darwin
go run . --model devin --skill workflow-architecture --force
go run . --config devin
```

`--list-skills` consulta a pasta `skills/` da referência informada por `--ref`
e lista apenas as skills disponíveis no repositório. A instalação aceita
somente skills existentes nessa pasta.

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
e macOS, nas arquiteturas `amd64` e `arm64`.

O fluxo de promoção funciona assim:

1. Um push em `develop` executa testes, vet e builds multiplataforma.
2. Após sucesso, `.github/workflows/promote-develop.yml` cria ou atualiza o PR
   de `develop` para `main` e ativa o auto-merge.
3. O PR aguarda a aprovação obrigatória e o check `Promote develop / Validate tool`.
4. O auto-merge integra o PR somente depois da aprovação e dos checks.
5. Depois do merge confirmado na `main`, `.github/workflows/release.yml`
   publica automaticamente a nova pre-release `v0.0.0-main.<run-number>`.

Para esse fluxo funcionar, habilite nas configurações de Actions do
repositório a opção `Allow GitHub Actions to create and approve pull requests`.
Também habilite auto-merge e configure a proteção da branch `main` com:

- pull request obrigatório antes do merge;
- pelo menos uma aprovação;
- check obrigatório `Promote develop / Validate tool`;
- merge queue habilitada, se disponível no plano do repositório.

Para criar manualmente uma release estável:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Os arquivos compactados e o `checksums.txt` serão anexados à GitHub Release.
O workflow também pode ser executado manualmente para republicar uma tag
existente.
