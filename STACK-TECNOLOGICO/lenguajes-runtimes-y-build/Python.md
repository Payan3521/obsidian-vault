---
titulo: "Python"
categoria:
  - "3. Lenguajes, runtimes y build"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "lenguajes-runtimes-y-build"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[.NET - C Sharp]]"
  - "[[Alembic]]"
  - "[[Bash - Shell]]"
  - "[[Bun]]"
  - "[[Deno]]"
  - "[[Django]]"
  - "[[FastAPI]]"
  - "[[Flask]]"
  - "[[GitHub Actions]]"
  - "[[Go]]"
---

# Python — Guía completa 🐍

> ⭐ Núcleo imprescindible. Objetivo: instalarlo bien, entender **qué pasa de verdad** (GIL, importes, typing, empaquetado), escribir código testeable y saber explicar cada decisión.

## 1. Mentalidad: qué es (y qué NO es) Python

Python es un **lenguaje interpretado, dinámico y de tipado fuerte en runtime**. "Dinámico" no significa "sin tipos": los tipos se resuelven al ejecutar y una variable puede cambiar de tipo. `1 + "1"` falla con `TypeError`, igual que en [[.NET - C Sharp]] o [[Go]], solo que más tarde.

No es:

- **Lento por definición**. CPython puro sí es lento en bucles; el ecosistema serio (NumPy, hashlib, regex, [[Pydantic]]) delega en C/Rust. El cuello suele estar en tu código.
- **Un runtime único**. `python` suele ser CPython; están también PyPy (JIT), Jython e IronPython ([[.NET - C Sharp]]). [[Bun]] y [[Deno]] son otros ecosistemas, no Python. Especificá siempre *implementación + versión*.
- **Sin estructura**. Un script de 20 líneas y un paquete publicado son disciplinas distintas: entornos aislados, tipos, tests y `pyproject.toml`.
- **Sincronía obligatoria**. Existe `async`/`await` desde 3.5 y los builds sin GIL (PEP 703, *free-threaded*) desde 3.13/3.14.

| Capa | Qué es | Dónde vive |
|---|---|---|
| Lenguaje | Sintaxis, objetos, protocolos | PEPs e intérprete |
| Intérprete | CPython 3.x (el estándar) | `python3` en el PATH |
| Entorno | `venv` / `uv` aislado | `.venv/` |
| Dependencias | `pyproject.toml` + lockfile | Repo |
| Ejecución | script, `python -m`, servidor ASGI/WSGI | CLI / [[Uvicorn - Gunicorn]] |

> Frase para entrevista: *"Python es dinámico pero fuerte; CPython usa GIL, resuelve nombres en runtime y su unidad de distribución es el paquete, no el archivo suelto"*.

En el mapa, [[Python]] es la base de [[FastAPI]], [[Flask]], [[Django]], [[pytest]] y de la automatización que corre en [[GitHub Actions]].

---

## 2. Instalación y primeros pasos (comandos copiables)

```bash
# Linux (Debian/Ubuntu)
sudo apt update && sudo apt install -y python3 python3-venv python3-pip python3-dev build-essential
# Fedora/RHEL: sudo dnf install -y python3 python3-pip python3-devel gcc
# Arch:        sudo pacman -S python python-pip base-devel
# macOS:       xcode-select --install && brew install python@3.12 uv
# Windows:     winget install --id Python.Python.3.12 -e
python3 --version
python3 -c "import sys; print(sys.executable, sys.version_info)"
```

> Nunca borres el `python3` del sistema: muchas distros lo usan internamente (`apt`, `dnf`). Usá entornos aislados. En Windows, el lanzador `py -3.12` es tu mejor amigo; ver [[Bash - Shell]] para WSL.

### uv, el gestor moderno (recomendado)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # Windows: irm https://astral.sh/uv/install.ps1 | iex
uv --version
uv python install 3.12
uv python list
```

### Tres formas de arrancar

```bash
# A) uv: crea pyproject.toml, venv y lock
mkdir mi-app && cd mi-app && uv init
uv add pydantic httpx
uv run python -c "import pydantic, httpx; print(pydantic.__version__)"
uv lock && uv sync --frozen

# B) venv + pip (siempre disponible)
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install "pydantic>=2,<3" httpx
python -m pip freeze > requirements.txt
deactivate

# C) script suelto con dependencias embebidas (PEP 723)
cat > reporte.py <<'PY'
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27"]
# ///
import httpx
print(httpx.get("https://httpbin.org/get").status_code)
PY
uv run reporte.py                     # entorno efímero, sin venv permanente
```

### Verificación que vale oro

```bash
which python python3 pip pip3
python3 -c "import sys; print(sys.prefix, sys.path)"
python3 -m pip --version             # el pip correcto es el de ESTE intérprete
python3 -c "import pydantic; print(pydantic.__file__)"
python3 -X importtime -c "import django" 2>&1 | tail -20
```

> Usá siempre `python -m pip`, nunca `pip` suelto: así instalás en el intérprete que después ejecutás.

---

## 3. Cheat sheet

| Comando / sintaxis | Qué hace |
|---|---|
| `python3 --version` | Versión del intérprete |
| `python3 -m venv .venv` | Entorno aislado |
| `source .venv/bin/activate` | Activa venv (Windows: `.venv\Scripts\activate`) |
| `python -m pip install -e ".[dev]"` | Paquete editable + extras |
| `python -m pip check` / `pip list --outdated` | Dependencias rotas / desactualizadas |
| `uv init` / `uv add <pkg>` / `uv sync --frozen` | Flujo moderno con lockfile |
| `uv run <cmd>` | Ejecuta dentro del entorno del proyecto |
| `python -m paquete` | Ejecuta `__main__.py` (recomendado) |
| `python -c "..."` / `python - <<'PY'` | Una línea / heredoc |
| `python -i script.py` | Ejecuta y abre REPL con el estado |
| `python -X dev` | Modo desarrollo: warnings extra |
| `python -m pytest -q` | Tests con [[pytest]] |
| `python -m ruff check .` / `ruff format .` | Lint y formato |
| `python -m mypy .` | Chequeo estático de tipos |
| `python -m build` | Construye `sdist` + `wheel` |
| `python -m pip show <pkg>` | Metadatos y ubicación |
| `python -m pdb script.py` | Debugger interactivo |
| `python -m cProfile -s cumtime script.py` | Perfilado de CPU |
| `python -m pip-audit` | CVEs en dependencias |

| Expresión | Uso |
|---|---|
| `x if cond else y` | Expresión condicional |
| `[f(x) for x in xs if p(x)]` | List comprehension |
| `first, *rest = xs` | Starred unpacking |
| `with open(...) as f:` | Context manager |
| `try / except / else / finally` | Manejo de errores |
| `match x: case 1: ...` | Pattern matching (3.10+) |
| `f"{x=:>10}"` | F-string con debug y formato |
| `def f(x: int, /, y: str, *, z=1.0) -> None:` | Positional-only / keyword-only |
| `from __future__ import annotations` | Anotaciones diferidas |
| `dataclass(slots=True)` | Clase de datos compacta |
| `type Alias = int \| str` | Alias de tipo (3.12+) |

---

## 4. Flujo diario / ejemplo mínimo real

API pequeña con [[FastAPI]], [[Pydantic]] y [[pytest]]:

```bash
mkdir -p mi_app tests
cat > pyproject.toml <<'TOML'
[project]
name = "mi-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.110", "uvicorn[standard]>=0.29", "pydantic>=2.6"]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.5", "mypy>=1.10", "httpx>=0.27"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["mi_app*"]

[tool.pytest.ini_options]
addopts = "-q --strict-markers"
testpaths = ["tests"]

[tool.mypy]
strict = true
python_version = "3.12"
TOML

cat > mi_app/__init__.py <<'PY'
"""Mi aplicación."""
PY

cat > mi_app/schemas.py <<'PY'
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class PedidoIn(BaseModel):
    sku: str = Field(min_length=3, pattern=r"^[A-Z0-9-]+$")
    cantidad: int = Field(gt=0, le=1000)
    creado: datetime | None = None

    @field_validator("sku")
    @classmethod
    def normalizar(cls, v: str) -> str:
        return v.strip().upper()
PY

cat > mi_app/main.py <<'PY'
from fastapi import FastAPI
from mi_app.schemas import PedidoIn

app = FastAPI(title="mi-app", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/pedidos", status_code=201)
def crear(pedido: PedidoIn) -> dict[str, object]:
    # Persistencia con [[SQLAlchemy - Django ORM]] en un proyecto real.
    return {"sku": pedido.sku, "cantidad": pedido.cantidad}
PY

cat > tests/test_pedidos.py <<'PY'
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from mi_app.main import app
from mi_app.schemas import PedidoIn

client = TestClient(app)

def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}

def test_crear() -> None:
    r = client.post("/pedidos", json={"sku": "abc-1", "cantidad": 2})
    assert r.status_code == 201 and r.json()["sku"] == "ABC-1"

def test_invalido() -> None:
    with pytest.raises(ValidationError):
        PedidoIn(sku="ABC-1", cantidad=0)
PY

source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m ruff check . && python -m mypy mi_app
python -m pytest --cov=mi_app --cov-report=term-missing
uvicorn mi_app.main:app --reload --port 8000
curl -s http://127.0.0.1:8000/openapi.json | jq .info
```

Ese `openapi.json` alimenta [[OpenAPI - Swagger]] y [[Postman - Newman]]: el contrato nace del código.

---

## 5. Profundidad: lo que separa a un usuario de un dominador

### GIL y concurrencia

El **GIL** (*Global Interpreter Lock*) de CPython permite **un solo hilo ejecutando bytecode Python a la vez**. Protege la memoria de los objetos y simplifica las extensiones C.

- **CPU-bound**: los hilos no escalan → `ProcessPoolExecutor`, nativo (NumPy) o Rust.
- **I/O-bound**: los hilos sí ayudan, porque el GIL se libera durante la espera.
- `sleep`, sockets y DB liberan el GIL.

```python
import concurrent.futures as cf
def trabajo(n: int) -> int:
    return sum(i * i for i in range(n))
with cf.ProcessPoolExecutor() as ex:      # CPU: procesos, no hilos
    print(list(ex.map(trabajo, [2_000_000] * 4)))
```

```python
import asyncio, httpx
async def main() -> None:
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=10)) as c:
        rs = await asyncio.gather(*(c.get("https://httpbin.org/get") for _ in range(20)))
    print({r.status_code for r in rs})
asyncio.run(main())
```

**Free-threaded CPython** (PEP 703): builds sin GIL, experimentales en 3.13 y de primer nivel en 3.14. Cuesta ~5-15% en un solo hilo y exige extensiones preparadas: `uv python install 3.14t` y `PYTHON_GIL=0 python -c "import sys; print(sys._is_gil_enabled())"`. Medí antes de adoptarlo.

### async: cuándo sí y cuándo no

`async def` no acelera nada si no awaitás algo realmente asíncrono; un cómputo pesado dentro bloquea el event loop.

| Situación | Herramienta |
|---|---|
| Muchas peticiones HTTP concurrentes | `asyncio` + httpx |
| Servidor con muchas conexiones | [[Uvicorn - Gunicorn]] + [[FastAPI]] |
| Cómputo pesado | Procesos / nativo |
| DB sin driver async | Hilos o sync, sin fingir async |
| Tareas en segundo plano | `create_task`, cola (Celery/RQ) |

`asyncio.run()` se llama **una vez** por entrypoint; nunca `time.sleep` ni `requests` dentro de async; guardá la referencia de `create_task` para que no sea recolectada.

### Typing que aporta

```python
from typing import Any, Protocol, TypeAlias, TypeVar

UserId: TypeAlias = int | str
T = TypeVar("T")

class Repositorio(Protocol):
    def get(self, id: UserId) -> dict[str, Any] | None: ...

def primero(xs: list[T]) -> T | None:
    return xs[0] if xs else None
```

Usá `str | None`, `list[int]` (PEP 604/585). Cada `Any` es un agujero en el chequeo: preferí `object` + `isinstance` o un `Protocol`. `cast()` no verifica nada. Corré `mypy --strict` en CI; sin chequeo, las anotaciones son decoración.

### Testing que sobrevive refactors

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from mi_app.main import app

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
```

```bash
python -m pytest -x --lf            # para en el primero, rerun de fallidos
python -m pytest --cov=mi_app --cov-fail-under=80
```

Muchos tests unitarios rápidos, menos de integración (DB con testcontainers), pocos end-to-end. Usá `monkeypatch` antes que mocking complejo y testeá comportamiento, no implementación. Verificá que `upgrade` y `downgrade` de [[Alembic]] funcionen con datos reales.

### Empaquetado

```bash
python -m pip install build twine
python -m build                       # dist/*.tar.gz + *.whl
python -m twine check dist/*
unzip -l dist/*.whl
python -m twine upload --repository testpypi dist/*
```

`pyproject.toml` es la fuente de verdad (PEP 621); `requirements.txt` reproduce entornos. Extras separan `dev`/`test`; `__main__.py` habilita `python -m mi_app`; `entry_points` crea ejecutables. Versión SemVer `0.1.0`, tag `v0.1.0`, publicación con [[GitHub Actions]].

---

## 6. Configuración avanzada y rendimiento

```bash
set -a && source .env && set +a       # cargar .env desde [[Bash - Shell]]
python -c "import os; print(os.environ['LOG_LEVEL'])"
```

```python
import os
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str
    log_level: str = "INFO"

cfg = Settings(database_url=os.environ["DATABASE_URL"])  # falla rápido si falta
```

```bash
python -m cProfile -s cumtime script.py | head -40
py-spy top --pid <PID>                 # perfiler en vivo, sin tocar código
python -m pip install py-spy memory_profiler
```

Optimizaciones que sí valen: medir primero; `set`/`dict` para búsquedas; generadores para streams grandes; `dataclass(slots=True)` si creás millones de objetos; `functools.lru_cache` con cuidado de memoria; `PYTHONUNBUFFERED=1` en contenedores; I/O → async/hilos, CPU → procesos o nativo. En CI: `ruff`, `mypy`, `pytest --cov` y `pip-audit` con actions fijadas (ver [[GitHub Actions]]).

---

## 7. Errores comunes: síntoma → causa → solución

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError` | Instalaste con otro intérprete/venv | `which python`; `python -m pip install x` |
| `SyntaxError` en `match` | Python < 3.10 | `python3 --version`; actualizá |
| `IndentationError` | Mezclaste tabs y espacios | Reindental con 4 espacios |
| `AttributeError: 'NoneType' ...` | No verificaste `None` | `if x is not None:` |
| `UnboundLocalError` | Asignás dentro de la función | Inicializá la variable o usá `nonlocal` |
| `RuntimeError: This event loop is already running` | `asyncio.run` dentro de async | `await` la corrutina; `run` solo en el entrypoint |
| `ImportError: cannot import name X` | Circular import o versión distinta | Mové el import dentro de la función; `pip show` |
| `Could not build wheels for <pkg>` | Faltan headers/compilador | `apt install python3-dev build-essential` |
| `pytest: no tests ran` | Nombres o `testpaths` mal puestos | Archivos `test_*.py`, funciones `test_*` |
| `mypy: Library stubs not installed` | Faltan stubs | `pip install types-requests` |
| `ssl.SSLCertVerificationError` | CA/proxy corporativo | Configurá certificados; nunca `verify=False` |
| `pytest --cov` da 0% | Módulo no importado por los tests | Revisá `--cov=mi_app` y la estructura de paquetes |

---

## 8. Seguridad y buenas prácticas

- **Aislamiento**: un venv por proyecto; nunca `sudo pip install`.
- **Dependencias**: lockfile con hashes en aplicaciones, `pip-audit` en CI, `uv lock --upgrade` periódico.
- **Secretos**: variables de entorno o gestor; `.env` en `.gitignore` con `.env.example` como plantilla. Si se filtró, **rotá** la credencial.
- **Entradas**: validá en la frontera con [[Pydantic]]; jamás `eval()`, `exec()` ni `pickle.loads()` con datos externos (RCE).
- **Inyección**: SQL parametrizado; nunca f-strings con datos del usuario ([[SQLAlchemy - Django ORM]]).
- **Paths**: `Path(base) / nombre` y `resolve().is_relative_to(base)`.
- **Logs**: niveles, sin tokens ni PII, separando negocio de técnicos.
- **Excepciones**: no `except Exception: pass`; capturá lo específico y no muestres tracebacks al usuario.
- **Supply chain**: verificá autores, usá `pip install --require-hashes` en entornos sensibles y fijá acciones de CI por SHA.

```bash
python -m pip install pip-audit && python -m pip-audit -r requirements.txt
```

---

## 9. Ejercicios para dominarlo

1. `uv init`, agregá [[Pydantic]] y httpx, generá `uv.lock`, borrá `.venv` y reproducí con `uv sync --frozen`.
2. Medí un script CPU-bound con hilos y con `ProcessPoolExecutor`; explicá la diferencia con el GIL.
3. Implementá la misma API con [[FastAPI]] y [[Flask]]; compará validación y documentación con [[OpenAPI - Swagger]].
4. Escribí tres tests con [[pytest]], lográ ≥80% de cobertura y corré `mypy --strict`.
5. Empaquetá con `python -m build`, instalá el wheel en un venv limpio y ejecutalo con `python -m mi_app`.
6. Armá un workflow de [[GitHub Actions]] con matrix 3.11/3.12/3.13, caché de uv y publicación a TestPyPI solo en tags `v*`.
7. Introducí un `pickle.loads` con datos de usuario, demostrá el riesgo y reemplazalo por `json.loads`.

---

## 10. Relaciones

[[Python]] · [[FastAPI]] · [[Django]] · [[Flask]] · [[Pydantic]] · [[SQLAlchemy - Django ORM]] · [[Alembic]] · [[Uvicorn - Gunicorn]] · [[pytest]] · [[Postman - Newman]] · [[OpenAPI - Swagger]] · [[GitHub Actions]] · [[.NET - C Sharp]] · [[Go]] · [[Bash - Shell]] · [[Bun]] · [[Deno]]
