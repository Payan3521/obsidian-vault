---
titulo: "GitHub Actions"
categoria:
  - "3. Lenguajes, runtimes y build"
  - "7. DevOps, CI/CD e IaC"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "lenguajes-runtimes-y-build"
  - "devops-ci-cd-e-iac"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[Alembic]]"
  - "[[Argo CD]]"
  - "[[Artifacts]]"
  - "[[Blue-green - Canary]]"
  - "[[CircleCI]]"
  - "[[Django]]"
  - "[[FastAPI]]"
  - "[[Feature flags]]"
  - "[[Flask]]"
  - "[[GitLab CI]]"
---

# GitHub Actions — Guía completa ⚙️

> ⭐ Núcleo imprescindible. Objetivo: escribir workflows que pasen a la primera, entender **eventos, jobs, contextos y secretos**, y depurar un pipeline roto sin hacer `re-run` a ciegas.

## 1. Mentalidad: qué es (y qué NO es)

[[GitHub Actions]] es un **orquestador de jobs basado en eventos**, alojado en GitHub. Un evento (push, PR, tag, schedule, manual) dispara un workflow; el workflow contiene jobs; cada job corre en un runner y ejecuta steps secuenciales.

No es:

- **Un reemplazo del Makefile**: la lógica real (`pytest`, `ruff`, `build`) vive en scripts del repo y debe correrse en local.
- **Un servidor que administrás**: los runners hosted son efímeros; cada job arranca limpio.
- **Seguro por defecto**: los secretos se enmascaran en pantalla, pero un `echo`, un `jq` o un proceso hijo pueden filtrarlos.
- **Idéntico a [[GitLab CI]] o [[CircleCI]]** en sintaxis: comparten la idea pipeline → stages → jobs.

```text
EVENTO → WORKFLOW (.github/workflows/*.yml)
           ├─ JOB lint        → runner ubuntu-latest → steps
           ├─ JOB test (matrix 3.11/3.12/3.13) → [[Artifacts]]
           └─ JOB deploy (needs) → environment → OIDC → cloud
```

| Concepto | Definición rápida |
|---|---|
| Workflow | YAML en `.github/workflows/` |
| Job | Unidad con su propio runner |
| Step | Comando o acción dentro de un job |
| Action | Bloque reutilizable `uses: owner/repo@ref` |
| Contexto | `github`, `env`, `secrets`, `inputs`, `steps`, `matrix`, `needs` |
| Expression | `${{ ... }}`: se evalúa **antes** de correr el step |
| Environment | Ámbito con protecciones y secrets propios |

> Frase para entrevista: *"Un workflow es un DAG de jobs disparado por eventos; cada job es un runner efímero y las expressions `${{ }}` se resuelven en el servidor antes del step"*.

El CI de [[Python]] corre [[pytest]]; el deploy puede pasar la posta a [[Argo CD]] y liberar con [[Feature flags]] o [[Blue-green - Canary]].

---

## 2. Instalación y primeros pasos

```bash
sudo apt update && sudo apt install -y gh jq yq actionlint    # Debian/Ubuntu
# Fedora: sudo dnf install gh jq yq actionlint
# macOS:  brew install gh jq yq actionlint
# Windows: winget install --id GitHub.cli -e
gh --version && gh auth login && gh auth status

# Validadores en local
go install github.com/rhysd/actionlint/cmd/actionlint@latest   # alternativa
python -m pip install zizmor                                  # auditoría de seguridad
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
act -l                                                        # lista jobs detectados
```

Primer workflow:

```bash
mkdir -p .github/workflows
cat > .github/workflows/hello.yml <<'YAML'
name: Hola CI
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: read
jobs:
  saludar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Saludar
        run: echo "Hola ${{ github.actor }} desde ${{ github.ref_name }} @ ${{ github.sha }}"
      - id: salida
        run: echo "resultado=ok" >> "$GITHUB_OUTPUT"
YAML

actionlint .github/workflows/hello.yml
git add .github/workflows/hello.yml && git commit -m "ci: primer workflow" && git push
gh run list --workflow=hello.yml --limit 3
gh run view $(gh run list --workflow=hello.yml --limit 1 --json databaseId --jq '.[0].databaseId')
```

> Un workflow nuevo en una rama no dispara `pull_request` hasta que el archivo esté en la rama base; usá `workflow_dispatch` para probarlo.

---

## 3. Cheat sheet

| Expresión / evento | Significado |
|---|---|
| `on: push` / `pull_request` / `workflow_dispatch` / `schedule` / `release` | Disparadores |
| `on: workflow_run` / `repository_dispatch` | Después de otro workflow / vía API |
| `pull_request_target` | ⚠️ Contexto de la base: nunca ejecutes código del fork con secrets |
| `${{ github.sha }}` / `${{ github.ref_name }}` | Commit / rama o tag |
| `${{ github.actor }}` / `${{ github.event_name }}` | Usuario / evento |
| `${{ secrets.NOMBRE }}` / `${{ vars.NOMBRE }}` | Secreto / variable |
| `${{ inputs.x }}` / `${{ matrix.x }}` | Input / valor de matriz |
| `${{ needs.test.outputs.x }}` / `${{ steps.id.outputs.x }}` | Outputs de job / step |
| `${{ hashFiles('**/uv.lock') }}` / `${{ runner.os }}` | Hash para caché / OS |
| `${{ always() }}` / `${{ success() }}` / `${{ failure() }}` | Estado del job |
| `${{ fromJSON() }}` / `${{ toJSON() }}` / `${{ format() }}` | Funciones útiles |

| Escribir a | Uso |
|---|---|
| `echo "KEY=value" >> "$GITHUB_ENV"` | Variable para steps siguientes |
| `echo "k=v" >> "$GITHUB_OUTPUT"` | Output del step/job |
| `echo "### Resumen" >> "$GITHUB_STEP_SUMMARY"` | Markdown en la pestaña del run |
| `echo "::error::mensaje"` / `::warning::` / `::notice::` | Anotaciones en el log |
| `echo "::group::Título"` / `::endgroup::` | Agrupa log |
| `echo "::add-mask::valor"` | Enmascara un valor dinámico |
| `exit 1` | Falla el step y el job |

| CLI `gh` | Qué hace |
|---|---|
| `gh run list --limit 10` / `gh run watch <id>` | Listar / seguir runs |
| `gh run view <id> --log-failed` | Solo el step fallido |
| `gh run rerun <id> --failed` | Reintentar fallidos |
| `gh pr checks` | Chequeos del PR |
| `gh workflow run ci.yml -f env=staging` | Disparo manual con inputs |
| `gh secret set NAME --body valor` | Alta de secreto |
| `gh api repos/:owner/:repo/actions/runs \| jq '.total_count'` | API directa |

---

## 4. Flujo diario: workflow completo de CI

```yaml
name: CI

on:
  pull_request:
    branches: [main]
    paths-ignore: ["docs/**", "**.md"]
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      despliegue:
        description: "entorno"
        type: choice
        default: none
        options: [none, staging, production]

permissions:
  contents: read                     # menor privilegio global

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHONUNBUFFERED: "1"

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: uv sync --frozen --all-extras
      - run: uv run ruff check --output-format=github .
      - run: uv run mypy src

  test:
    name: Tests py${{ matrix.python }}
    runs-on: ubuntu-latest
    needs: lint
    timeout-minutes: 20
    strategy:
      fail-fast: false
      max-parallel: 4
      matrix:
        python: ["3.11", "3.12", "3.13"]
    services:
      db:
        image: postgres:16
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U app -d app_test"
          --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgresql://app:app@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: uv sync --frozen --all-extras
      - run: uv run alembic upgrade head       # ver [[Alembic]]
      - run: uv run pytest --cov=src --cov-report=xml --cov-fail-under=80
      - name: Cobertura (aun si falla)
        if: always() && matrix.python == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: cobertura
          path: coverage.xml
          retention-days: 7
      - name: Resumen
        if: always()
        run: |
          echo "### Tests py${{ matrix.python }}" >> "$GITHUB_STEP_SUMMARY"
          echo "- resultado: ${{ job.status }}" >> "$GITHUB_STEP_SUMMARY"

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/*
          if-no-files-found: error

  deploy:
    runs-on: ubuntu-latest
    needs: [test, build]
    if: github.event_name == 'workflow_dispatch' || github.ref == 'refs/heads/main'
    environment:
      name: ${{ inputs.despliegue == 'production' && 'production' || 'staging' }}
      url: https://api.ejemplo.internal
    permissions:
      contents: read
      id-token: write                 # OIDC
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist
      - env:
          API_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: |
          set -euo pipefail
          test -n "$API_TOKEN"
          ls -l dist
```

Flujo diario:

```bash
actionlint .github/workflows/ci.yml && act -j lint
git switch -c feat/validacion && git push -u origin feat/validacion
gh pr create --fill && gh pr checks
gh run view <ID> --log-failed
git add . && git commit --amend --no-edit && git push --force-with-lease
gh pr merge --squash
```

---

## 5. Profundidad: jobs, matrices, caché y OIDC

### Grafo de jobs y outputs

Los jobs corren **en paralelo** salvo que los encadenes con `needs`:

```yaml
jobs:
  version:
    outputs:
      tag: ${{ steps.calcular.outputs.tag }}
    runs-on: ubuntu-latest
    steps:
      - id: calcular
        run: echo "tag=v$(date +%Y%m%d%H%M)" >> "$GITHUB_OUTPUT"
  publicar:
    needs: version
    runs-on: ubuntu-latest
    steps:
      - run: echo "Publicando ${{ needs.version.outputs.tag }}"
```

Para outputs complejos, heredoc con `jq`:

```bash
{
  echo 'resumen<<EOF'
  jq -c '{total: (.items | length)}' reporte.json
  echo EOF
} >> "$GITHUB_OUTPUT"
```

### Matrices

```yaml
strategy:
  fail-fast: false
  max-parallel: 3
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python: ["3.11", "3.12", "3.13"]
    exclude: [{os: windows-latest, python: "3.13"}]
    include: [{os: ubuntu-latest, python: "3.12", extra: "--cov"}]
```

Cada combinación es un job con su runner. `fail-fast: false` muestra el panorama completo; `max-parallel` controla costo. Es la forma barata de testear versiones de [[Python]], [[Django]] o [[Flask]].

### Caching

```yaml
- uses: actions/cache@v4
  id: cache-deps
  with:
    path: |
      ~/.cache/uv
      .venv
    key: deps-${{ runner.os }}-${{ matrix.python }}-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      deps-${{ runner.os }}-${{ matrix.python }}-
- if: steps.cache-deps.outputs.cache-hit != 'true'
  run: uv sync --frozen --all-extras
```

La clave **debe** incluir el hash del lockfile o cacheás dependencias viejas. `setup-uv` con `enable-cache: true` y Buildx con `cache-from/cache-to: type=gha` lo hacen mejor. Nunca caches secretos ni artefactos de deploy: persisten entre runs.

### OIDC: credenciales sin llaves permanentes

```yaml
permissions:
  contents: read
  id-token: write                    # obligatorio
jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
          aws-region: us-east-1
      - run: aws sts get-caller-identity
```

El runner pide un JWT firmado por GitHub; el cloud valida claims (`repo`, `ref`, `environment`) contra una trust policy y entrega credenciales de corta duración. Ventaja: no hay access keys que rotar y el token está atado a rama/entorno.

### Artifacts, environments y workflows reutilizables

- `upload-artifact@v4` + `download-artifact@v4` pasan archivos entre jobs; para datos chicos usá `outputs`. Los nombres son inmutables: incluí versión o SHA.
- Un `environment` con *required reviewers* pausa el job; puede tener secrets propios (`secrets.DEPLOY_TOKEN` del environment gana sobre el del repo) y `url` visible en el PR.
- `on: workflow_call` define un reusable workflow (jobs completos); `action.yml` con `runs: using: composite` define steps reutilizables. No anides más de un nivel.

```yaml
# .github/workflows/_python-ci.yml
on:
  workflow_call:
    inputs:
      python-version: {type: string, default: "3.12"}
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Probando ${{ inputs.python-version }}"
# Llamada: uses: ./.github/workflows/_python-ci.yml  +  with: {python-version: "3.13"}
```

---

## 6. Configuración avanzada y rendimiento

```yaml
jobs:
  desplegar:
    strategy:
      matrix:
        entorno: [staging, production]
    environment: ${{ matrix.entorno }}
    env:
      API_URL: ${{ vars.API_URL }}
      API_TOKEN: ${{ secrets.API_TOKEN }}   # secret por environment
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsS -H "Authorization: Bearer $API_TOKEN" "$API_URL/health"
```

| Palanca | Efecto |
|---|---|
| `concurrency` con `cancel-in-progress` | Mata runs viejos del mismo PR |
| `paths` / `paths-ignore` | Evita CI por cambios de docs |
| Caché con `hashFiles` | No reinstala dependencias |
| `fail-fast: false` | Más minutos, diagnóstico completo |
| `timeout-minutes` | Evita jobs colgados |
| Matrices / paralelismo | Menos tiempo wall-clock |
| Self-hosted runners | Control, pero vos mantenés el riesgo |

```bash
gh run view <ID> --json event,headBranch,conclusion | jq .
gh api "repos/:owner/:repo/actions/runs?per_page=20" \
  | jq -r '.workflow_runs[] | [.id, .event, .conclusion] | @tsv'
actionlint .github/workflows/*.yml && zizmor .github/workflows/
```

Poné `set -euo pipefail` en cada bloque `run:`. `ACTIONS_STEP_DEBUG` y `ACTIONS_RUNNER_DEBUG` como secrets del repo revelan más detalle (temporales: generan mucho log). Si un step falla "sin razón", reproducilo con `act` o en un contenedor: casi siempre es una variable de entorno o la versión del runner.

---

## 7. Errores comunes: síntoma → causa → solución

| Síntoma | Causa | Solución |
|---|---|---|
| El workflow no aparece | Mal ubicado o YAML inválido | `.github/workflows/`; `actionlint` |
| `Resource not accessible by integration` | Permisos insuficientes | Agregá el permiso mínimo (`contents: write`) |
| `Unrecognized named-value: 'secrets'` en `if:` | Secrets no disponibles en condicionales | Pasalos a `env:` |
| Deploy no arranca | Falta `needs:` o `if:` falso | Revisá el DAG con `gh run view` |
| `${{ needs.foo.outputs.x }}` vacío | El job no declaró `outputs` | Declaralos y escribir con `$GITHUB_OUTPUT` |
| `No such file: dist/` | Falta descargar el artifact | `download-artifact` con el mismo `name` |
| Tests intermitentes por DB | Servicio no healthy | `--health-cmd pg_isready` en `services:` |
| `ModuleNotFoundError` solo en CI | Entorno distinto | Lockfile + `uv sync --frozen`; fijá `python-version` |
| Caché siempre miss | Falta `hashFiles` o la ruta está mal | Revisá `key`, `restore-keys` y `path` |
| OIDC: `token has expired` | Falta `id-token: write` o trust policy | Corregí permisos y claims |
| Secrets vacíos en forks | GitHub no los expone | `workflow_dispatch` / `workflow_run` / environment |
| `Action ... not found` | Tag inexistente | Verificá `owner/repo@ref`; mejor SHA |
| Job `Queued` horas | Sin runners o minutos agotados | Revisá *Settings → Actions* y el plan |
| Código arbitrario vía `${{ github.event.issue.title }}` | Inyección de expressions | Pasá el valor por `env:` y usá `"$VALOR"` |

---

## 8. Seguridad y buenas prácticas

- **Pin de actions**: las actions de terceros corren con tus secretos. Fijalas por SHA (un tag es mutable) y actualizalas con Dependabot (`github-actions`).

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
- uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
```

- **Menor privilegio**: `permissions: {}` arriba y solo lo necesario por job (`contents: read`, `id-token: write`).
- **Secretos**: nunca `echo "$SECRET"` ni los pongas en `run:`. El enmascarado cubre el valor exacto, no transformaciones (`base64`, substring): un hash visible también filtra.
- **PII**: no loguees emails,tokens ni datos de clientes en CI; los logs suelen ser legibles por mucha más gente que la BD. Rotá cualquier credencial expuesta.
- **`pull_request_target`**: nunca hagas checkout del fork y ejecutes su código con secrets; usá `workflow_run`.
- **Artifacts**: `retention-days` corto; pueden contener `.env`, código no publicado o símbolos.
- **OIDC** antes que access keys permanentes; `id-token: write` solo en el job que lo usa.
- **Auditoría**: `zizmor` detecta expressions inyectables, permisos excesivos y `pull_request_target` peligrosos.

```bash
grep -RniE "(password|token|api[_-]?key) *[:=] *['\"][^$]" .github/workflows/ || true
```

Checklist: `actionlint` + `zizmor` en verde · permisos mínimos · actions por SHA · sin `${{ github.event.* }}` en `run:` · secretos vía `secrets`/`vars` · `timeout` y `concurrency` · caché con hash · deploy protegido por environment y OIDC.

---

## 9. Ejercicios para dominarlo

1. Creá `hello.yml` con `workflow_dispatch` e `inputs`; disparalo con `gh workflow run hello.yml -f nombre=TuNombre`.
2. Agregá matrix de [[Python]] 3.11/3.12/3.13 con `fail-fast: false`; hacé fallar un caso y confirmá que los otros terminan.
3. Subí `coverage.xml` con `if: always()` y descargalo en otro job con `needs`, mostrando `sha256sum coverage.xml`.
4. Configurá caché con `hashFiles('**/uv.lock')`, corré dos veces y verificá el `Cache hit` en el log.
5. Introducí `${{ github.event.issue.title }}` en un `run:` y confirmá que `zizmor` lo marca; corregilo vía `env:`.
6. Fijá todas las actions a SHA y pasá de `permissions: write-all` a `permissions: {}` + permisos por job.
7. Reemplazá un access key por OIDC con `id-token: write`, `environment: staging` y compará `aws sts get-caller-identity`.

---

## 10. Relaciones

[[GitHub Actions]] · [[Python]] · [[FastAPI]] · [[Django]] · [[Flask]] · [[Pydantic]] · [[SQLAlchemy - Django ORM]] · [[Alembic]] · [[Uvicorn - Gunicorn]] · [[pytest]] · [[Postman - Newman]] · [[OpenAPI - Swagger]] · [[Artifacts]] · [[Argo CD]] · [[Blue-green - Canary]] · [[Feature flags]] · [[CircleCI]] · [[GitLab CI]]
