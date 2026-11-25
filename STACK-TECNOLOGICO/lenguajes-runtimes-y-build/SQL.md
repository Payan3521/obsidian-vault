---
titulo: "SQL"
categoria:
  - "3. Lenguajes, runtimes y build"
  - "9. Bases de datos"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "lenguajes-runtimes-y-build"
  - "bases-de-datos"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[.NET - C Sharp]]"
  - "[[Bash - Shell]]"
  - "[[Bun]]"
  - "[[Deno]]"
  - "[[Go]]"
  - "[[HTML - CSS]]"
  - "[[JVM]]"
  - "[[Java]]"
  - "[[JavaScript]]"
  - "[[Kotlin]]"
---

# SQL — Guía completa 🧠

> ⭐ Núcleo imprescindible. Objetivo: pensar en **conjuntos**, escribir consultas correctas sin buscar la sintaxis, entender **qué hace el motor por dentro** y diagnosticar una query lenta.

## 1. Mentalidad: qué es SQL (y qué NO es)

SQL es un **lenguaje declarativo**: describís *qué resultado querés* y el motor decide *cómo obtenerlo*. No es imperativo (no hay bucles ni "leé fila por fila"), ni es un lenguaje de programación de bases de datos: la lógica procedural (PL/pgSQL, T-SQL) es una extensión del motor.

> Frase para entrevista: *"SQL es declarativo y se basa en álgebra relacional; el optimizador elige el plan, no yo"*.

| Mentalidad imperativa (❌) | Mentalidad SQL (✅) |
|---|---|
| "Recorro pedidos y sumo importes" | `SELECT SUM(total) FROM pedidos` |
| "Si el cliente existe, actualizo" | `UPDATE ... WHERE id = ...` (0 filas es válido) |
| "Hago un `for` para traer cada detalle" | Un `JOIN` trae todo de una vez |

Las consultas devuelven **conjuntos** (bags: hay duplicados). Preguntate siempre: ¿`UNION` o `UNION ALL`? ¿`DISTINCT` o estás tapando un bug de join?

| Sublenguaje | Comandos | Para qué |
|---|---|---|
| **DQL** | `SELECT` | Leer |
| **DDL** | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | Estructura |
| **DML** | `INSERT`, `UPDATE`, `DELETE`, `MERGE` | Datos |
| **DCL** | `GRANT`, `REVOKE` | Permisos |
| **TCL** | `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` | Transacciones |

Orden lógico de evaluación (distinto del orden de escritura):

```text
FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT/OFFSET
```

Por eso `WHERE` no ve aliases de `SELECT` pero `ORDER BY` sí, y por eso `HAVING COUNT(*) > 3` filtra grupos mientras `WHERE` filtra filas.

Es estándar ANSI/ISO, pero hay dialectos: `LIMIT` (PostgreSQL, SQLite en texto plano) vs `TOP` (SQL Server) vs `FETCH FIRST` (Oracle). Acá usamos sintaxis PostgreSQL-compatible.

## 2. Instalación y primeros pasos

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y postgresql postgresql-client
# Fedora / RHEL
sudo dnf install -y postgresql-server postgresql-contrib && sudo postgresql-setup --initdb
# macOS
brew install postgresql@16 && brew services start postgresql@16

sudo systemctl enable --now postgresql
pg_isready                       # "accepting connections"
psql --version
```

Sin servidor (para practicar consultas):

```bash
sudo apt install sqlite3
sqlite3 :memory:
sqlite3 tienda.db < crear_tablas.sql
```

Con contenedor:

```bash
docker run -d --name pg-dev -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app \
  -e POSTGRES_DB=tienda -p 5432:5432 -v pgdata:/var/lib/postgresql/data postgres:16-alpine
docker exec -it pg-dev psql -U app -d tienda
```

> El contenedor se borra; el volumen `pgdata` no. Nunca hagas `docker compose down -v` sin backup.

Conectar y moverse en `psql`:

```bash
psql -h localhost -p 5432 -U app -d tienda
psql postgresql://app:app@localhost:5432/tienda
```

```text
\conninfo     # ver conexión actual      \dt          # listar tablas
\d pedidos    # describir tabla          \du          # roles
\df           # funciones                \x on        # salida vertical
\timing on    # medir cada sentencia     \i archivo.sql # ejecutar script
\q            # salir
```

Primer esquema copiable:

```sql
CREATE TABLE clientes (
  id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre     TEXT NOT NULL,
  email      TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE pedidos (
  id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cliente_id BIGINT NOT NULL REFERENCES clientes(id),
  total      NUMERIC(12,2) NOT NULL CHECK (total >= 0),
  estado     TEXT NOT NULL DEFAULT 'pendiente'
             CHECK (estado IN ('pendiente','pagado','enviado','cancelado')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO clientes (nombre, email) VALUES ('Ana','ana@example.com'),('Beto','beto@example.com');
INSERT INTO pedidos (cliente_id, total, estado) VALUES
  (1,120.50,'pagado'), (1,30.00,'pendiente'), (2,99.90,'enviado');
SELECT * FROM pedidos ORDER BY created_at DESC;
```

## 3. Cheat sheet

| Sintaxis | Qué hace |
|---|---|
| `SELECT col AS alias FROM t` | Proyección con alias |
| `SELECT DISTINCT col FROM t` | Sin duplicados |
| `WHERE col = 5` / `<>` / `BETWEEN 1 AND 9` / `IN (1,2)` | Filtros |
| `WHERE col IS NULL` | Nulos (**nunca** `= NULL`) |
| `WHERE nombre ILIKE '%ana%'` | Like case-insensitive |
| `ORDER BY col DESC NULLS LAST` / `LIMIT 10 OFFSET 20` | Orden y paginación |
| `COUNT(*)`, `COUNT(col)`, `COUNT(DISTINCT col)` | Todas / sin nulos / únicas |
| `SUM`, `AVG`, `MIN`, `MAX` + `GROUP BY` + `HAVING COUNT(*) > 3` | Agregación |
| `COALESCE(col,0)` / `NULLIF(a,b)` | Default / evita división por cero |
| `CASE WHEN ... THEN ... ELSE ... END` | Condicional |
| `CAST(col AS INT)` / `col::int` | Conversión |

JOINs (dominarlos es obligatorio):

| Tipo | Resultado |
|---|---|
| `INNER JOIN` | Solo filas con match en ambas |
| `LEFT JOIN` | Todas las de la izquierda + matches (`NULL` si no hay) |
| `RIGHT JOIN` / `FULL OUTER JOIN` | Inverso / todas de ambas |
| `CROSS JOIN` | Producto cartesiano (n×m) |
| `LATERAL JOIN` | Subconsulta por fila (top-N por grupo) |

```sql
SELECT c.nombre, p.id AS pedido_id, p.total
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id
ORDER BY c.nombre, p.id;
```

| Comando | Uso |
|---|---|
| `CREATE TEMP TABLE ...` / `ALTER TABLE t ADD COLUMN c TEXT` / `DROP TABLE t` | DDL |
| `TRUNCATE t` | Vaciar rápido (no loguea filas) |
| `INSERT INTO t (a,b) VALUES (1,2),(3,4)` | Multi-fila |
| `INSERT ... ON CONFLICT (email) DO UPDATE SET ...` | Upsert |
| `UPDATE t SET col=1 WHERE id=5` / `DELETE FROM t WHERE id=5` | ⚠️ sin `WHERE` afecta todo |
| `MERGE INTO t USING s ON ... WHEN MATCHED ...` | Upsert estándar |
| `BEGIN; ... COMMIT;` / `ROLLBACK;` / `SAVEPOINT s1;` | Transacciones |
| `RETURNING *` | Ver filas afectadas |
| `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` | Plan real |

## 4. Flujo diario / ejemplo mínimo

```bash
psql -U app -d tienda
```

```sql
-- 1) Mirá siempre el esquema primero
\d pedidos
-- 2) Reporte: total por cliente con JOIN, filtro y agregación
SELECT c.id, c.nombre, COUNT(p.id) AS pedidos, COALESCE(SUM(p.total),0) AS facturado
FROM clientes c JOIN pedidos p ON p.cliente_id = c.id
WHERE p.estado = 'pagado' AND p.created_at >= now() - INTERVAL '30 days'
GROUP BY c.id, c.nombre HAVING COUNT(p.id) > 0
ORDER BY facturado DESC;
-- 3) Top 3 pedidos por cliente (window function)
SELECT nombre, pedido_id, total, rn FROM (
  SELECT c.nombre, p.id AS pedido_id, p.total,
         ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY p.total DESC) AS rn
  FROM clientes c JOIN pedidos p ON p.cliente_id = c.id
) s WHERE rn <= 3;
-- 4) Upsert transaccional
BEGIN;
INSERT INTO clientes (nombre,email) VALUES ('Ana','ana@example.com')
ON CONFLICT (email) DO UPDATE SET nombre = EXCLUDED.nombre
RETURNING id, nombre;
COMMIT;
```

```bash
# 5) Versioná los scripts (automatizá con [[Bash - Shell]])
mkdir -p sql && psql -U app -d tienda -v ON_ERROR_STOP=1 -f sql/crear_tablas.sql > /tmp/sql.out 2>&1
grep -i error /tmp/sql.out || echo "OK"
```

**Checklist:** aliases claros → probar con `BEGIN` + `ROLLBACK` → verificar filas afectadas → `COMMIT` → si es lenta, `EXPLAIN ANALYZE`.

## 5. Profundidad: cómo piensa el motor

```text
SQL → Parser (AST) → Analyzer (nombres, tipos, permisos) → Rewriter (vistas, RLS)
    → Planner/Optimizer (estimaciones → plan) → Executor (Seq Scan, Hash Join, Sort...)
    → Storage (heap + índices + WAL)
```

El optimizador usa estadísticas (`ANALYZE`, `pg_stats.n_distinct`, histogramas). Con estadísticas viejas elige mal el plan: un `ANALYZE` resuelve misterios de rendimiento.

**Almacenamiento y MVCC:** la tabla es un heap de páginas de 8 KB con tuplas que tienen `xmin`/`xmax`. Un `UPDATE` crea una **nueva versión** y marca la vieja; los lectores ven una snapshot sin bloquear writers. Por eso hay que limpiar con `VACUUM` (autovacuum en PostgreSQL). El **WAL** registra cada cambio antes de aplicarlo: base de durabilidad y backups point-in-time.

| Índice | Ideal para |
|---|---|
| **B-tree** (default) | Igualdad, rangos, `ORDER BY`, `LIKE 'prefijo%'` |
| **Hash** | Solo `=` |
| **GIN** | Arrays, JSONB, full-text |
| **GiST / BRIN** | Geometría/rangos / tablas gigantes por fecha |
| **Partial** `WHERE estado='pagado'` | Subconjunto frecuente |
| **Expression** `(lower(email))` | Búsquedas con función |
| **Covering** `INCLUDE (col)` | Index-only scan |
| Normalización 1FN/2FN/3FN | Celdas atómicas / dependencia de clave / sin transitivas |
| Transacciones ACID | Atomicidad, Consistencia, Aislamiento, Durabilidad |

Un índice acelera lecturas pero encarece escrituras: no indexes "por si acaso". En OLTP normalizá; en analítica desnormalizá (tabla de hechos + resúmenes).

| Nivel de aislamiento | Permite |
|---|---|
| `READ COMMITTED` (default) | Non-repeatable read, phantom |
| `REPEATABLE READ` | Phantom (no en Postgres) |
| `SERIALIZABLE` | Nada; requiere reintentar si SQLSTATE `40001` |

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE; SELECT ...; COMMIT;
```

CTE y `EXISTS`:

```sql
WITH ventas AS (SELECT cliente_id, SUM(total) AS total FROM pedidos GROUP BY 1)
SELECT c.nombre, v.total FROM clientes c JOIN ventas v ON v.cliente_id = c.id;
-- Postgres 12+: WITH ventas AS MATERIALIZED | NOT MATERIALIZED
-- EXISTS suele ser mejor que NOT IN: NOT IN con NULL devuelve 0 filas
```

## 6. Configuración avanzada y rendimiento

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM pedidos WHERE cliente_id = 1;
```

```text
Index Scan using idx_pedidos_cliente on pedidos  (cost=0.29..8.31 rows=3 width=44)
  (actual time=0.012..0.018 rows=3 loops=1)
  Index Cond: (cliente_id = 1)
  Buffers: shared hit=4
Execution Time: 0.042 ms
```

Leé de abajo hacia arriba y de adentro hacia afuera:

| Señal | Significado | Acción |
|---|---|---|
| `cost=.. rows=..` | Estimación del planner | Comparar con `actual rows` |
| `Seq Scan` en tabla grande | Leyó todo | ¿Falta índice? |
| `Buffers: shared hit/read` | Caché vs disco | Muchos `read` = lento |
| `Sort Method: external merge Disk` | `work_mem` bajo | Subirlo |
| `rows` estimados ≪ `actual rows` | Stats viejas | `ANALYZE` |

```sql
ANALYZE pedidos;
VACUUM (VERBOSE, ANALYZE) pedidos;
REINDEX TABLE pedidos;
CREATE INDEX CONCURRENTLY idx_pedidos_c_e ON pedidos (cliente_id, estado)
  WHERE estado = 'pagado';
SET work_mem = '32MB';
SET enable_seqscan = off;   -- SOLO para diagnosticar, nunca en prod
```

| Parámetro | Controla | Síntoma de valor bajo |
|---|---|---|
| `shared_buffers` | Caché (≈25% RAM) | Muchos `shared read` |
| `work_mem` | Sort/hash por operación | `external merge Disk` |
| `effective_cache_size` | Caché del SO para el planner | Planes pesimistas |
| `random_page_cost` | I/O aleatorio (SSD: 1.1) | Subestima índices |
| `max_connections` | Conexiones (usá pooler) | `too many clients` |

Optimizaciones concretas:

```sql
-- 1) Filtrar temprano; evitar funciones sobre columnas indexadas
-- ❌ WHERE created_at::date = '2026-11-24'
-- ✅
WHERE created_at >= '2026-11-24' AND created_at < '2026-11-25';
-- 2) Paginación por cursor en vez de OFFSET grande
SELECT id, total FROM pedidos WHERE id > :ultimo_id ORDER BY id LIMIT 20;
-- 3) Particionado por fecha
CREATE TABLE eventos (id BIGINT, fecha DATE NOT NULL, dato JSONB) PARTITION BY RANGE (fecha);
CREATE TABLE eventos_2026_01 PARTITION OF eventos
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

```bash
# 4) Batch writes con COPY (mucho más rápido que INSERT fila por fila)
psql -U app -d tienda -c "\copy pedidos(cliente_id,total) FROM 'pedidos.csv' CSV HEADER"
# 5) Medir
pgbench -i -s 10 tienda && pgbench -c 10 -j 2 -T 60 tienda
```

```sql
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `column "x" does not exist` | Typo, alias o mayúsculas sin comillas | Revisar `\d tabla` |
| `relation "pedidos" does not exist` | `search_path` o schema | `SET search_path TO public;` / `\dt *.*` |
| `violates not-null constraint` | Falta valor o `DEFAULT` | Completar o agregar default |
| `duplicate key value violates unique constraint` | Falta upsert / race | `ON CONFLICT ... DO UPDATE` |
| `syntax error at or near "select"` | Falta `;` o `(` | `\errverbose` en psql |
| `UPDATE` tocó todas las filas | Falta `WHERE` | `ROLLBACK` + reescribir |
| `NOT IN` devuelve 0 filas | Hay `NULL` | Usar `NOT EXISTS` |
| `division by zero` | Denominador 0 | `NULLIF(den,0)` |
| Query de repente lenta | Stats/bloat/plan | `ANALYZE`, `VACUUM`, `EXPLAIN ANALYZE` |
| `too many clients already` | Sin pool | pgbouncer + bajar `max_connections` |
| `deadlock detected` | Locks en orden distinto | Ordenar acceso a tablas; reintentar |
| `current transaction is aborted` | Error previo en `BEGIN` | `ROLLBACK` o `SAVEPOINT` |
| `permission denied for table` | Rol sin `GRANT` | `GRANT SELECT ON tabla TO rol` |
| Resultados duplicados tras join | Join 1:N mal interpretado | `DISTINCT` o `GROUP BY` |

```sql
SELECT pid, state, wait_event, left(query,80) FROM pg_stat_activity WHERE state <> 'idle';
SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;
```

## 8. Seguridad y buenas prácticas

```text
-- ❌ NUNCA concatenar input: ' OR '1'='1 devuelve TODOS los usuarios
query = "SELECT * FROM usuarios WHERE email = '" + email + "'"
```

```python
# ✅ Parámetros: los datos viajan separados del código
cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
```

```java
// ✅ Desde [[Java]] (JDBC)
PreparedStatement ps = con.prepareStatement("SELECT * FROM usuarios WHERE email = ?");
ps.setString(1, email);
```

```javascript
// ✅ Desde [[JavaScript]] (node-postgres)
await client.query('SELECT * FROM usuarios WHERE email = $1', [email]);
```

```sql
CREATE ROLE app_reader LOGIN PASSWORD '...';
GRANT CONNECT ON DATABASE tienda TO app_reader;
GRANT USAGE ON SCHEMA public TO app_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_reader;
REVOKE ALL ON TABLE clientes FROM PUBLIC;
```

Checklist: parámetros siempre; menor privilegio; TLS (`sslmode=require`/`verify-full`); contraseñas en secret manager; backups con restore probado; migraciones versionadas y reversibles; `statement_timeout`; auditoría de tablas sensibles; sin secretos en el historial de psql (`\set HISTFILE /dev/null`).

| Necesidad | PostgreSQL | SQL Server | Oracle | SQLite (texto plano) |
|---|---|---|---|---|
| Autoincrement | `IDENTITY` | `IDENTITY(1,1)` | `SEQUENCE` | `INTEGER PRIMARY KEY` |
| Upsert | `ON CONFLICT` | `MERGE` | `MERGE` | `ON CONFLICT` |
| Limitar | `LIMIT n` | `TOP n` | `FETCH FIRST n ROWS` | `LIMIT n` |
| Hoy | `CURRENT_DATE` | `GETDATE()` | `SYSDATE` | `date('now')` |

## 9. Ejercicios para dominarlo

1. Creá `clientes` y `pedidos` y cargá 5 clientes con 3 pedidos cada uno; verificá con `COUNT(*)`.
2. Total facturado y número de pedidos por cliente, **solo** para quienes tengan más de 2 (`GROUP BY` + `HAVING`).
3. `LEFT JOIN` que liste todos los clientes aunque no tengan pedidos; explicá por qué `INNER JOIN` no los muestra.
4. `UPDATE pedidos SET total = 0;` dentro de `BEGIN`, mirá el resultado y hacé `ROLLBACK`. Repetí con `WHERE id = 1` y `COMMIT`.
5. `EXPLAIN (ANALYZE, BUFFERS)` antes y después de crear un índice; compará `Seq Scan` vs `Index Scan` y `Buffers`.
6. Upsert por `email` con `ON CONFLICT` que actualice `nombre` y devuelva `id` con `RETURNING`.
7. `ROW_NUMBER()` para los 2 pedidos más caros por cliente; comparalo con `ORDER BY ... LIMIT` por cliente.
8. Escribí una query vulnerable por concatenación y reescribila con parámetros en [[Python]], [[Java]] o [[JavaScript]].

## 10. Relaciones

[[SQL]] · [[Java]] · [[JVM]] · [[Kotlin]] · [[JavaScript]] · [[TypeScript]] · [[Node.js]] · [[Deno]] · [[Bun]] · [[Python]] · [[.NET - C Sharp]] · [[Go]] · [[Rust]] · [[Bash - Shell]] · [[HTML - CSS]]
