---
titulo: "Git"
categoria:
  - "5. Control de versiones y flujo de código"
  - "17. IA — nueva era (sección ampliada)"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "control-de-versiones-y-flujo-de-código"
  - "ia-nueva-era-sección-ampliada"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[Husky]]"
  - "[[GitHub Actions]]"
  - "[[Agent Development Environment (ADE)]]"
  - "[[BYO agent (Claude Code-Codex-OpenCode)]]"
  - "[[Bitbucket]]"
  - "[[GitFlow]]"
  - "[[GitHub]]"
  - "[[GitHub Flow]]"
  - "[[GitLab]]"
  - "[[MCP (Model Context Protocol)]]"
  - "[[OpenCode]]"
  - "[[Orca Bots (Slack-Linear-GitHub)]]"
---

# Git — Guía completa 🧰

> ⭐ Núcleo imprescindible. Objetivo: que puedas usar Git con soltura, entender **qué pasa internamente** y saber **recuperarte de un desastre** sin pánico.

## 1. Qué es Git (mentalidad correcta)

Git es un **controlador de versiones distribuido**: cada clon es un repositorio completo con todo el historial. No es "un Dropbox con commits": es una **base de datos de snapshots** con punteros (HEAD, ramas, tags).

Olvídate de "guardar archivos": en Git **haces commits de estados completos del proyecto**.

### Las 4 zonas (clave para no confundirte)

```text
 Working directory  ──git add──▶  Staging (Índice)  ──git commit──▶  Repositorio local (.git)
        ▲                                                                    │
        └────────────── git checkout / git restore ◀──────────────────────────┘
                                                                             │
                              push ◀────────── Remote (GitHub/GitLab) ◀───────┘ pull/fetch
```

- **Working directory**: lo que ves y editas.
- **Staging / índice**: lo que *vas* a incluir en el próximo commit.
- **Repositorio local**: historial de commits (`.git/`).
- **Remote**: copia compartida en [[GitHub]], [[GitLab]] o [[Bitbucket]].

### Objeto interno (por si te preguntan en entrevista)

Commit → árbol → blobs. Cada objeto tiene un hash SHA-1 (ej. `3f8a9c2…`). Un commit guarda: árbol, padres, autor, mensaje y timestamp. Las ramas son solo **punteros móviles a commits**; `HEAD` apunta a la rama actual.

---

## 2. Instalación

### Linux

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install git -y

# Fedora / RHEL
sudo dnf install git -y

# Arch
sudo pacman -S git

# Verificar
git --version
```

### macOS

```bash
xcode-select --install        # instala git (Apple)
brew install git              # recomendado (más actualizado)
```

### Windows

```powershell
winget install --id Git.Git -e
# o descargar desde https://git-scm.com/download/win
```

> En Windows usa **Git Bash** o WSL para tener `~/.bashrc`, `ssh`, `chmod`, etc. (ver [[WSL]]).

---

## 3. Configuración inicial (hazla una sola vez)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"      # o vim / nano
git config --global pull.rebase false              # o true, pero decide uno
git config --global core.autocrlf input            # Linux/macOS
git config --global core.autocrlf true             # Windows sin WSL
git config --global cred.helper store              # ⚠️ solo en local de confianza

# Ver toda tu config y de dónde viene cada valor
git config --list --show-origin
```

### Firmar commits (opcional, recomendado)

```bash
gpg --gen-key
gpg --list-secret-keys --keyid-format LONG
git config --global user.signingkey TU_KEY_ID
git config --global commit.gpgsign true
```

Relación: [[Firma GPG]].

---

## 4. Comandos esenciales (cheat sheet)

| Comando | Qué hace |
|---|---|
| `git init` | Crea repo vacío en `.git/` |
| `git clone <url>` | Clona repo remoto (incluye historial) |
| `git status -s` | Estado corto (`M` modificado, `A` añadido, `??` sin trackear) |
| `git add <archivo>` / `git add .` / `git add -p` | Añadir al staging (`-p` = por partes) |
| `git commit -m "msg"` | Crea commit |
| `git commit -am "msg"` | Añade + commitea archivos **ya trackeados** |
| `git commit --amend` | Reemplaza el último commit (cuidado si ya hiciste push) |
| `git log --oneline --graph --all` | Historial visual |
| `git show <hash>` | Muestra un commit/diff |
| `git diff` | Cambios sin stage |
| `git diff --staged` | Cambios en stage |
| `git restore <file>` | Descarta cambios en working dir |
| `git restore --staged <file>` | Saca del staging (mantiene cambios) |
| `git reset --soft HEAD~1` | Deshace commit, deja cambios en staging |
| `git reset HEAD~1` | Deshace commit, deja cambios en working dir |
| `git reset --hard HEAD~1` | ⚠️ Borra commit **y** cambios |
| `git revert <hash>` | Crea un commit que invierte otro (seguro en remoto) |
| `git branch` / `git branch -a` | Lista ramas locales / todas |
| `git switch -c feature/x` | Crea y cambia de rama (moderno) |
| `git checkout -b feature/x` | Igual, estilo clásico |
| `git branch -d rama` | Borra rama fusionada (`-D` fuerza) |
| `git merge rama` | Fusiona rama en la actual |
| `git rebase rama` | Reaplica tus commits encima de otra rama |
| `git cherry-pick <hash>` | Trae un commit específico a la rama actual |
| `git stash push -m "wip"` / `git stash pop` | Guarda / recupera trabajo temporal |
| `git tag -a v1.0 -m "release"` | Tag anotado |
| `git push --tags` | Sube tags |
| `git remote -v` | Ver remotos |
| `git remote add origin <url>` | Añadir remoto |
| `git fetch --prune` | Trae refs y limpia ramas borradas |
| `git pull --rebase` | Fetch + rebase (historial lineal) |
| `git push -u origin main` | Push y deja upstream |
| `git clean -fd` | ⚠️ Borra archivos no trackeados |
| `git rm --cached <file>` | Deja de trackear pero no borra el archivo |
| `git mv a b` / `git rm archivo` | Mover / borrar con Git |
| `git blame <file>` | Quién y cuándo tocó cada línea |
| `git bisect` | Búsqueda binaria del commit que introdujo un bug |
| `git reflog` | ⚠️ Tu salvavidas: historial de movimientos de HEAD |
| `git gc` / `git fsck` | Limpieza / integridad del objeto database |

---

## 5. Flujo diario recomendado

```bash
git switch main
git pull --rebase origin main
git switch -c feature/validacion-dto

# ... editas archivos ...

git status
git add -p                      # revisa antes de añadir
git commit -m "feat(auth): valida DTO con Pydantic"

git push -u origin feature/validacion-dto
# → abres Pull Request en [[GitHub]]
```

Antes de commitear, los hooks de [[Husky]] pueden correr `[[lint-staged]]`, [[ESLint - Prettier]] y [[commitlint]] automáticamente.

---

## 6. Ramas y flujos de trabajo

### Comparativa

| Flujo | Ramas | Ideal para |
|---|---|---|
| [[GitFlow]] | `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` | Proyectos con versiones y releases formales |
| [[GitHub Flow]] | `main` + ramas cortas por feature | Web/apps con deploy continuo |
| [[Trunk-based development]] | `main` + ramas de vida muy corta | Equipos maduros, CI fuerte, feature flags |

> Regla práctica: **rama corta, commit pequeño, PR revisado, merge rápido**. Si tu rama vive más de 2–3 días, probablemente haya que dividirla.

### merge vs rebase vs cherry-pick

| | `merge` | `rebase` | `cherry-pick` |
|---|---|---|---|
| Historial | Con ramificaciones (merge commits) | Lineal | Copia un commit puntual |
| Reescribe hashes | No | **Sí** | Sí (nuevo hash) |
| Seguro en ramas compartidas | ✅ | ⚠️ Solo en ramas propias | ✅ con criterio |
| Cuándo | Integrar feature en `main` | Actualizar tu rama antes del PR | Portar un hotfix a otra rama |

```bash
# Rebase interactivo: reordenar, squash, renombrar commits
git rebase -i HEAD~3
# comandos dentro del editor: pick, reword, squash, fixup, drop
```

---

## 7. Resolver conflictos

```bash
git pull --rebase
# CONFLICT (content): Merge conflict en archivo.py

git status                       # archivos en "both modified"
# abres el archivo y ves:
# <<<<<<< HEAD
# tu versión
# =======
# versión incoming
# >>>>>>> branch
# editas, dejas una sola versión y guardas

git add archivo.py
git rebase --continue            # o git commit si fue merge
```

Para abortar: `git rebase --abort` o `git merge --abort`.

---

## 8. Cómo deshacer (tabla salvavidas)

| Situación | Comando |
|---|---|
| Cambié un archivo pero aún no hice `add` | `git restore archivo` |
| Ya hice `add` pero quiero sacarlo | `git restore --staged archivo` |
| Hice commit y quiero rehacer el mensaje | `git commit --amend` |
| Hice commit local y quiero deshacerlo | `git reset --soft HEAD~1` |
| Ya subí el commit a remoto | `git revert <hash>` (nunca `reset --hard` + force push en compartidas) |
| Borré una rama por accidente | `git branch recuperar <hash-del-reflog>` |
| Hice `reset --hard` y perdí trabajo | `git reflog` → `git reset --hard HEAD@{n}` |
| Quiero volver al estado de hace 2 horas | `git reflog` + `git checkout <hash>` |

---

## 9. Remotos y colaboración

```bash
git clone git@github.com:org/repo.git      # SSH (recomendado)
git remote add upstream git@github.com:org-upstream/repo.git

git fetch origin
git pull --rebase origin main
git push origin feature/mi-cambio

# Sincronizar un fork
git fetch upstream
git rebase upstream/main
git push --force-with-lease                # ⚠️ más seguro que --force
```

> `--force-with-lease` falla si alguien hizo cambios en el remoto que tú aún no tienes. Úsalo siempre en lugar de `--force`.

### Pull Request profesional

1. Rama con nombre claro: `feat/`, `fix/`, `docs/`, `refactor/`.
2. Título con [[Conventional Commits]].
3. Descripción: qué, por qué, cómo probarlo.
4. Tests y CI en verde ([[GitHub Actions]]).
5. Un cambio = un propósito. PRs grandes = revisiones malas.

---

## 10. `.gitignore` y secretos

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
.env
*.egg-info/

# Node
node_modules/
dist/
.env.local

# IDE / SO
.vscode/
.idea/
.DS_Store
```

- Si ya subiste un `.env`, sacalo del índice: `git rm --cached .env` y **rotá la credencial** (ver [[Gestión de secretos]]).
- Usá `.env.example` con claves vacías como documentación.
- Nunca commitees llaves AWS, JWTs ni contraseñas ([[OWASP Top 10]], [[KMS]]).

Relación: [[.gitignore]], [[Hooks - pre-commit]].

---

## 11. Commits profesionales

Formato [[Conventional Commits]]:

```text
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional: BREAKING CHANGE, closes #123]
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

```text
feat(auth): añade refresh token con rotación

Implementa blacklist en Redis y expiración corta del access token.

Closes #42
```

Esto habilita versionado automático con [[Semantic Versioning]] y changelogs generados.

---

## 12. Herramientas avanzadas

```bash
# Worktrees: varias ramas trabajadas a la vez (muy usado por Orca)
git worktree add ../repo-hotfix hotfix/login

# Submódulos
git submodule add <url> vendor/lib
git submodule update --init --recursive

# Logs útiles
git log --oneline --graph --decorate --all
git log --author="Payan" --since="2 weeks ago"
git shortlog -sn                      # commits por autor

# Bisect: encontrar el commit malo
git bisect start
git bisect bad
git bisect good v1.2.0
# Git te va moviendo; tú dices good/bad hasta que aparece el culpable
git bisect reset

# Encontrar texto en todo el historial
git log -S"password" --oneline --all
```

Los *worktrees* son exactamente lo que orquesta [[Orca.dev]] — ver [[Worktrees paralelos]] y [[Agent Development Environment (ADE)]].

---

## 13. Recuperación de emergencia (protocolo)

1. **No corras nada destructivo todavía.**
2. `git status` → entendé dónde estás.
3. `git reflog` → buscá el hash antes del desastre.
4. `git reset --hard <hash>` (o creá una rama: `git branch rescate <hash>`).
5. Si no aparece: `git fsck --lost-found` y revisá `git show <dangling>`.
6. Si vas a force push a un remoto compartido, hacé antes un clon fresco en `/tmp` antes de force push.

---

## 14. Ejercicios para dominarlo

1. Creá un repo, hacé 3 commits, usá `rebase -i` para convertirlos en 1.
2. Generá un conflicto a propósito en dos ramas y resolvelo.
3. Perdé un commit con `reset --hard` y recuperalo con `reflog`.
4. Configurá [[Husky]] con `commitlint` y verificá que rechace un mensaje inválido.
5. Hacé un PR con [[Conventional Commits]] y revisá el diff con `git diff --stat`.

---

## 15. Relaciones

[[GitHub]] · [[GitLab]] · [[Bitbucket]] · [[GitFlow]] · [[GitHub Flow]] · [[Trunk-based development]] · [[Husky]] · [[Hooks - pre-commit]] · [[Conventional Commits]] · [[Semantic Versioning]] · [[.gitignore]] · [[GitHub Actions]] · [[Jenkins]] · [[OpenCode]] · [[Orca.dev]] · [[Worktrees paralelos]] · [[Agent Development Environment (ADE)]] · [[MCP (Model Context Protocol)]]
