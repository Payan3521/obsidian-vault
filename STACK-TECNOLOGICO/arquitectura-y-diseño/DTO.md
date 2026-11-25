---
titulo: "DTO"
categoria:
  - "15. Arquitectura y diseño"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "arquitectura-y-diseño"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[OpenAPI - Swagger]]"
  - "[[Pydantic]]"
  - "[[Active Record vs Data Mapper]]"
  - "[[Controller]]"
  - "[[DAO]]"
  - "[[Dependency Injection]]"
  - "[[Interceptor - Filter]]"
  - "[[Mapper]]"
  - "[[Middleware]]"
  - "[[Model - Entity]]"
  - "[[Repository]]"
  - "[[Service]]"
---

# DTO — Guía completa 🧱

> ⭐ Núcleo imprescindible. Objetivo: usar DTOs para **definir el contrato entre capas**, validar en la frontera y evitar que el dominio (o la base) filtre hacia afuera.

## 1. Mentalidad: qué es (y qué NO es) un DTO

Un **DTO (Data Transfer Object)** es un objeto simple cuyo único trabajo es **transportar datos entre límites**. No decide, no aplica reglas de negocio, no persiste: es un *sobre* con una forma acordada.

- ✅ Es un **contrato explícito** de entrada/salida (request, response, evento, mensaje).
- ✅ Es **estructura + validación de forma**: tipos, rangos, formatos, longitudes.
- ✅ Es **inmutable por diseño** cuando representa una respuesta.
- ❌ No es tu [[Model - Entity]]: la entidad representa el dominio; el DTO es una foto para un consumidor concreto.
- ❌ No es un `dict` suelto: sin forma, el error aparece en producción.
- ❌ No es lógica de negocio ([[Service]]) ni acceso a datos ([[Repository]] / [[DAO]]).

> Frase para entrevista: *"El DTO protege el dominio de los cambios de la API y protege la API de los cambios del dominio"*.

```text
 HTTP / JSON
     │
[[Middleware]] → [[Interceptor - Filter]] → [[Controller]]
     │                          RequestDTO (validación de forma)
     │                                  ▼
     │                           [[Service]]  ← reglas de negocio
     │                                  ▼
     │                [[Mapper]] → [[Model - Entity]]
     │                                  ▼
     │            [[Repository]] → [[DAO]] → BD
     │                   [[Unit of Work]] (transacción)
     ▼
 ResponseDTO  → documentado en [[OpenAPI - Swagger]]
```

| Objeto | Pregunta que responde | Lógica |
|---|---|---|
| **DTO (Request)** | "¿Qué me mandó el cliente?" | Validación de forma |
| **DTO (Response)** | "¿Qué le devuelvo?" | Solo serialización |
| [[Model - Entity]] | "¿Qué es en mi dominio?" | Invariantes de negocio |
| [[DAO]] | "¿Cómo leo/escribo una fila?" | SQL |
| [[Repository]] | "¿Dónde busco agregados?" | Consultas + [[Unit of Work]] |
| [[Mapper]] | "¿Cómo paso de uno a otro?" | Transformación pura |

Con [[Active Record vs Data Mapper]] el DTO es más importante todavía: es lo único que separa la API del esquema de la BD.

---

## 2. Instalación y primeros pasos

Trabajamos con [[Pydantic]] v2 sobre un framework HTTP cualquiera (los ejemplos usan `FastAPI`, en texto plano).

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install "pydantic>=2" email-validator fastapi "uvicorn[standard]"
python -c "import pydantic; print(pydantic.VERSION)"
```

### DTO de request

```python
# app/schemas/user.py
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Name = Annotated[str, Field(min_length=2, max_length=80, pattern=r"^[\w .'-]+$")]
Password = Annotated[str, Field(min_length=12, max_length=128)]

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    name: Name
    password: Password
    accept_terms: bool = False

    @field_validator("accept_terms")
    @classmethod
    def must_accept(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Debés aceptar los términos")
        return value
```

### DTO de salida (nunca exponas el password)

```python
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: int
    email: EmailStr
    name: str
    created_at: datetime
```

`from_attributes=True` permite construirlo desde un objeto ORM sin copiar campo por campo: es la forma más común de [[Mapper]] en la salida.

### DTO de actualización parcial (PATCH)

```python
class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = None
    email: EmailStr | None = None

    def to_changes(self) -> dict:
        return self.model_dump(exclude_unset=True, exclude_none=True)
```

### [[Mapper]] manual (donde sí hay lógica)

```python
# app/mappers/user.py
from app.schemas.user import UserCreate, UserRead

def to_entity(data: UserCreate, *, password_hash: str):
    return User(email=str(data.email), name=data.name, password_hash=password_hash)

def to_read(user) -> UserRead:
    return UserRead.model_validate(user)   # from_attributes hace el mapeo
```

### [[Controller]] mínimo

```python
# app/api/users.py
from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import UserService
from app.db.session import get_session     # provisto por [[Dependency Injection]]

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db=Depends(get_session)) -> UserRead:
    return UserService(db).register(payload)

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db=Depends(get_session)) -> UserRead:
    return UserService(db).update(user_id, payload.to_changes())
```

`response_model` garantiza que **solo** los campos de `UserRead` salgan hacia afuera. Además, el framework publica el esquema en [[OpenAPI - Swagger]] en `/docs`.

```bash
uvicorn app.main:app --reload --port 8000
curl -X POST http://localhost:8000/users -H 'Content-Type: application/json' \
  -d '{"email":"ana@example.com","name":"Ana","password":"superSegura123!","accept_terms":true}'
# → 201 {"id":1,"email":"ana@example.com","name":"Ana","created_at":"..."}
```

---

## 3. Cheat sheet

| Concepto / API | Uso |
|---|---|
| `BaseModel` | Clase base de un DTO en [[Pydantic]] |
| `Field(...)` | `default`, `min_length`, `ge`, `le`, `pattern`, `description` |
| `EmailStr` / `HttpUrl` / `UUID4` | Tipos con validación de formato |
| `Annotated[T, Field(...)]` | Reutilizar restricciones en varios DTOs |
| `ConfigDict(extra="forbid")` | Rechazar campos no declarados (anti over-posting) |
| `ConfigDict(from_attributes=True)` | Mapear desde atributos de una entidad |
| `ConfigDict(frozen=True)` | DTO inmutable (response) |
| `ConfigDict(strict=True)` | Sin coercion silenciosa (`"7"` no es `7`) |
| `ConfigDict(validate_assignment=True)` | Validar también al asignar (más lento) |
| `@field_validator("campo")` | Validación de un campo |
| `@model_validator(mode="after")` | Validación que cruza campos |
| `model_validate(obj)` | Construir DTO desde dict u objeto |
| `model_validate_json(text)` | Parsear + validar JSON en un paso |
| `model_dump()` / `model_dump(mode="json")` | DTO → dict / dict serializable |
| `model_dump(exclude_unset=True)` | Solo campos enviados (PATCH) |
| `model_dump(by_alias=True)` | Serializar con alias (`userId`) |
| `model_copy(update={...})` | Copia sin revalidar |
| `TypeAdapter(list[UserRead])` | Validar colecciones sin wrapper |
| `response_model=...` | Filtra la salida en el [[Controller]] |
| [[Middleware]] / [[Interceptor - Filter]] | Logging, CORS, tamaño, validación transversal |
| [[OpenAPI - Swagger]] | Contrato visible y clientes generados |

---

## 4. Flujo diario / ejemplo mínimo

1. Escribí el **contrato** (DTO de request) con sus restricciones.
2. Escribí el **DTO de salida** con solo lo público.
3. Escribí el **mapper** (función pura) hacia la entidad.
4. El [[Service]] recibe el DTO válido y aplica reglas de negocio.
5. El [[Repository]] persiste dentro de [[Unit of Work]].
6. El [[Controller]] devuelve el DTO de salida y lo documenta en [[OpenAPI - Swagger]].

```python
# app/services/user.py
class UserService:
    def __init__(self, db):                 # db inyectado por [[Dependency Injection]]
        self.db = db

    def register(self, payload: UserCreate) -> UserRead:
        # 1) regla de negocio: unicidad (no es validación de forma)
        if self.db.users.exists(email=str(payload.email)):
            raise ValueError("Email ya registrado")

        # 2) mapeo: el DTO no sabe cómo se hashea un password
        entity = to_entity(payload, password_hash=hash_password(payload.password))

        # 3) persistencia detrás de [[Repository]] / [[DAO]]
        saved = self.db.users.add(entity)
        self.db.commit()                    # [[Unit of Work]]
        return to_read(saved)
```

```python
# Prueba rápida sin levantar el servidor
from pydantic import ValidationError

try:
    UserCreate(email="malo", name="A", password="corta", accept_terms=False)
except ValidationError as exc:
    print(exc.errors(include_url=False)[0])
    # {'type': 'value_error', 'loc': ('accept_terms',), 'msg': '...'}
```

> Regla de oro: **validación de forma en el DTO, reglas en el [[Service]], integridad en la BD**.

---

## 5. Profundidad: validación y mapeo entre capas

### 5.1 Los tres niveles

| Nivel | Dónde | Qué valida | Ejemplo |
|---|---|---|---|
| Forma | DTO (frontera) | Tipos, rangos, formato | `age: ge=0` |
| Negocio | [[Service]] | Invariantes del dominio | "email único", "saldo suficiente" |
| Integridad | BD / [[Repository]] | Unicidad, FK, NOT NULL | `UNIQUE(email)` |

No es redundancia: el DTO da feedback inmediato, el servicio protege reglas aunque el llamador sea interno y la BD es la última línea de defensa.

### 5.2 Validadores que cruzan campos

```python
from pydantic import BaseModel, model_validator

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def检查(self) -> "PasswordChange":
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas nuevas no coinciden")
        if self.new_password == self.current_password:
            raise ValueError("Debe ser distinta de la actual")
        return self
```

### 5.3 Alias: nombre interno vs contrato

```python
from pydantic import BaseModel, ConfigDict, Field

class OrderDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: int = Field(alias="userId", serialization_alias="userId")

dto = OrderDTO.model_validate({"userId": 7})
dto.user_id                    # 7 (Python)
dto.model_dump(by_alias=True)  # {'userId': 7} (contrato)
```

### 5.4 Estrategias de [[Mapper]]

| Estrategia | Ventaja | Riesgo |
|---|---|---|
| Función manual | Explícita y testeable | Más código |
| `model_validate(obj)` con `from_attributes` | Cero boilerplate | Acopla DTO a entidad |
| Clase [[Mapper]] inyectada | Centraliza variantes | Más indirección |
| Librería automática | Rápido al inicio | Magia: errores silenciosos |

Recomendación: mapeo **manual en entrada** (hash, normalización) y **`from_attributes` en salida**. Inyectá el [[Mapper]] con [[Dependency Injection]] si hay variantes por tenant o versión.

### 5.5 Versionado sin romper clientes

```python
class UserReadV1(BaseModel):
    id: int
    name: str

class UserReadV2(UserReadV1):
    email: EmailStr
    created_at: datetime

# El [[Controller]] elige el DTO según la ruta
@router.get("/v1/users/{user_id}", response_model=UserReadV1)
@router.get("/v2/users/{user_id}", response_model=UserReadV2)
```

Nunca agregues un campo obligatorio a un DTO publicado sin crear una versión nueva.

---

## 6. Configuración avanzada y rendimiento

```python
class StrictDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, frozen=True,
        validate_assignment=True, str_strip_whitespace=True,
        populate_by_name=True,
    )
    value: int
```

| Opción | Coste | Cuándo |
|---|---|---|
| `strict=True` | Neutral | Contratos exactos |
| `validate_assignment=True` | Más lento al escribir | Solo modelos mutables |
| `extra="forbid"` | Muy leve | Siempre en request |
| `frozen=True` | Neutral | Responses y claves de caché |

**Validar JSON en un paso** (el parser de Rust de [[Pydantic]] evita dicts intermedios):

```python
import json, timeit
from pydantic import TypeAdapter

class Event(BaseModel):
    id: int
    type: str

raw = '{"id":1,"type":"created"}'
Event.model_validate(json.loads(raw))   # ❌ dos pasos
Event.model_validate_json(raw)          # ✅ un paso
TypeAdapter(list[Event]).validate_json('[{"id":1,"type":"created"}]')
```

**Evitá la doble validación**: pasá el DTO ya validado al [[Service]]; si transformás, usá `model_copy(update=...)`. Medí con `timeit` sobre payloads reales: el [[Middleware]] de logging suele costar más que la validación si serializa el body completo.

Paginación con tope obligatorio:

```python
class PageParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
```

---

## 7. Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `extra fields not permitted` | Cliente envía campo no declarado | Revisá el contrato; `extra="ignore"` solo si es compatible |
| Password en la respuesta | Falta `response_model` | Devolvé el DTO de salida, nunca el ORM |
| `"7"` se convierte a `7` | Coercion por defecto | `ConfigDict(strict=True)` |
| Alias no coincide | Nombre Python vs alias | `populate_by_name=True` / `by_alias=True` |
| PATCH borra campos | `model_dump()` sin `exclude_unset` | Usá `payload.to_changes()` |
| ORM no mapea al DTO | Falta `from_attributes=True` | Agregalo o usá [[Mapper]] manual |
| Errores 500 en el [[Service]] | DTO no validado en frontera | Validá en el [[Controller]] |
| Schema en [[OpenAPI - Swagger]] sin docs | Sin `Field(description=...)` | Documentá cada campo público |
| Over-posting (`role`修改) | DTO universal con campos privados | DTOs por operación + `extra="forbid"` |
| Validación lenta en bulk | `model_validate` por item | `TypeAdapter(list[...]).validate_json()` |
| Stack trace filtrado en 422 | Excepción cruda | `exc.errors(include_url=False)` |

---

## 8. Seguridad y buenas prácticas

- **`extra="forbid"`** en todo DTO de entrada (anti mass assignment).
- **DTOs por operación**: `UserCreate`, `UserUpdate`, `AdminUpdate`, nunca un `UserDTO` con `is_admin`.
- **Lista blanca de salida**: el `response_model` define exactamente lo público.
- **Límites**: `max_length`, `ge/le`, `limit <= 100`, tamaño máximo de body en [[Middleware]].
- **Normalizá antes de validar**: `str_strip_whitespace`, normalización Unicode.
- **Secretos fuera del DTO**: password/token nunca en response, logs ni ejemplos de [[OpenAPI - Swagger]].
- **Errores sin filtración**: devolvé `loc` y `msg`, no el valor ni queries.

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    safe = [
        {"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]}
        for e in exc.errors(include_url=False)
        if e["loc"] and e["loc"][0] != "password"
    ]
    return JSONResponse(status_code=422, content={"errors": safe})
```

Checklist antes de mergear:

- [ ] ¿Request con `extra="forbid"` y response sin secretos?
- [ ] ¿Límites de longitud y paginación?
- [ ] ¿El [[Mapper]] no copia campos sensibles?
- [ ] ¿Hay test de payload inválido y de campo extra?
- [ ] ¿Test del schema público (`assert "password" not in UserRead.model_json_schema()["properties"]`)?

Reglas: un DTO = un propósito; inmutable en respuestas; tipar en los tres niveles; el [[Mapper]] es puro; versionar el contrato, no el dominio.

---

## 9. Ejercicios para dominarlo

1. Creá `ProductCreate`, `ProductUpdate` y `ProductRead` con `extra="forbid"`, `Field(ge=0)` y un validador de nombre no vacío.
2. Implementá `to_entity` que normalice el nombre y hashee el password; probalo con payload inválido y válido.
3. Hacé que un PATCH con `{"name":"Nuevo"}` no setee `email` a `None` (`exclude_unset=True`) y escribí el test.
4. Definí una unión discriminada `Payment` con campo `kind` y verificá el `oneOf` en `model_json_schema()`.
5. Medí con `timeit` `model_validate(json.loads(x))` vs `model_validate_json(x)` sobre 1000 elementos.
6. Armá un [[Controller]] con `response_model` y comprobá en [[OpenAPI - Swagger]] que el password no aparece; después quitá el `response_model` y confirmá la fuga.

---

## 10. Relaciones

[[OpenAPI - Swagger]] · [[Pydantic]] · [[Controller]] · [[Service]] · [[Repository]] · [[DAO]] · [[Model - Entity]] · [[Mapper]] · [[Middleware]] · [[Interceptor - Filter]] · [[Dependency Injection]] · [[Unit of Work]] · [[Active Record vs Data Mapper]] · [[DTO]]
