---
titulo: "PostgreSQL"
categoria:
  - "9. Bases de datos"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "bases-de-datos"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[RAG]]"
  - "[[Backups y recovery]]"
  - "[[PostGIS]]"
  - "[[RDS]]"
  - "[[MySQL - MariaDB]]"
  - "[[Oracle]]"
  - "[[SQL]]"
  - "[[SQL Server]]"
  - "[[SQLite]]"
---

# PostgreSQL — Guía completa 🐘

> ⭐ Núcleo imprescindible. Objetivo: instalarlo, entender **MVCC, WAL y el planner**, administrar usuarios y backups, y diagnosticar por qué una query pasó de 20 ms a 20 s.

## 1. Mentalidad: qué es (y qué NO es) PostgreSQL

PostgreSQL es un **SGBD relacional objetal, open source y extensible**. Es un servidor con procesos, memoria compartida, disco y WAL. No es "un MySQL con otro logo", ni reemplaza a [[SQLite]] (embebido, sin servidor), ni es un motor de búsqueda dedicado.

> Frase para entrevista: *"Postgres es MVCC con WAL; escribe versiones nuevas de las filas y por eso necesita VACUUM"*.

| Concepto | Idea clave |
|---|---|
| **MVCC** | Cada transacción ve una snapshot; un `UPDATE` crea una versión nueva |
| **WAL** | Write-Ahead Log: todo cambio se registra antes de aplicarse → durabilidad y PITR |
| **Heap** | Filas en páginas de 8 KB, sin orden físico por índice |
| **Planner** | Estima costos con estadísticas y elige Seq/Index Scan y joins |
| **ACID** | Transacciones completas, incluso con DDL (a diferencia de [[MySQL - MariaDB]]) |

| Escenario | PostgreSQL | Alternativa del mapa |
|---|---|---|
| OLTP con integridad compleja | ✅ | [[Oracle]] enterprise |
| JSON semiestructurado | ✅ `JSONB` + GIN | [[SQLite]] embebido |
| Geoespacial | ✅ [[PostGIS]] | — |
| Data warehouse masivo | ✅ hasta cierto tamaño | Redshift en texto plano |
| Miles de conexiones | ⚠️ con pgbouncer | — |

## 2. Instalación y primeros pasos

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y postgresql postgresql-client postgresql-contrib
sudo systemctl enable --now postgresql
pg_isready && psql --version
sudo -u postgres psql -c "SELECT version();"
# Fedora / RHEL
sudo dnf install -y postgresql-server postgresql-contrib && sudo postgresql-setup --initdb
# macOS
brew install postgresql@16 && brew services start postgresql@16
```

Contenedor para practicar:

```bash
docker run -d --name pg-local -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app \
  -e POSTGRES_DB=demo -p 5432:5432 -v pgdata:/var/lib/postgresql/data postgres:16-alpine
docker exec -it pg-local psql -U app -d demo
```

> ⚠️ Contraseña `app` solo para desarrollo. El contenedor se borra; el volumen `pgdata` tiene los datos (ver [[Backups y recovery]]).

```bash
psql -h localhost -p 5432 -U app -d demo
psql postgresql://app:app@localhost:5432/demo
PGPASSWORD=app psql -h localhost -U app -d demo -c "SELECT 1;"
```

Meta-comandos de `psql`:

```text
\conninfo  # conexión       \dt        # tablas        \d+ pedidos # detalle
\du        # roles          \dn        # schemas       \df         # funciones
\di        # índices        \x on      # vertical      \timing on  # cronómetro
\i arch.sql # script        \o salida.txt # redirect   \errverbose # error completo
\q         # salir
```

Esquema inicial copiable:

```sql
CREATE SCHEMA IF NOT EXISTS tienda;
SET search_path TO tienda, public;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE clientes (
  id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre     TEXT NOT NULL,
  email      CITEXT UNIQUE,
  activo     BOOLEAN NOT NULL DEFAULT true,
  metadata   JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE pedidos (
  id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cliente_id BIGINT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
  total      NUMERIC(12,2) NOT NULL CHECK (total >= 0),
  estado     TEXT NOT NULL DEFAULT 'pendiente',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_pedidos_cliente ON pedidos (cliente_id);
CREATE INDEX idx_pedidos_pendientes ON pedidos (created_at) WHERE estado = 'pendiente';
INSERT INTO clientes (nombre,email,metadata) VALUES
  ('Ana','ana@example.com','{"plan":"pro","region":"ar"}'),('Beto','beto@example.com','{"plan":"free"}');
INSERT INTO pedidos (cliente_id,total,estado) VALUES
  (1,150.00,'pagado'),(1,25.50,'pendiente'),(2,80.00,'pagado');
```

## 3. Cheat sheet

| Comando | Qué hace |
|---|---|
| `CREATE DATABASE demo OWNER app;` / `\l` | Crear / listar bases |
| `CREATE ROLE lector LOGIN PASSWORD '...';` / `\du` | Crear / listar roles |
| `GRANT SELECT ON ALL TABLES IN SCHEMA public TO lector;` | Permisos |
| `SHOW ALL;` / `SHOW work_mem;` | Parámetros |
| `SET work_mem = '32MB';` | Cambiar para la sesión |
| `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...;` | Matar sesión |
| `VACUUM (ANALYZE) pedidos;` / `REINDEX TABLE pedidos;` | Limpieza / índices |
| `CLUSTER pedidos USING idx_pedidos_cliente;` | Reordenar físicamente (una vez) |
| `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;` | Métricas |

```bash
pg_dump -U app -d demo -f demo.sql                    # SQL plano
pg_dump -U app -d demo -Fc -f demo.dump               # custom comprimido
pg_dump -U app -d demo -t clientes -f clientes.sql    # sola tabla
pg_dump -U app -d demo --schema-only -f schema.sql    # solo DDL
pg_dumpall -U app -f todo.sql                         # cluster + roles
pg_restore -U app -d demo_nueva -Fc demo.dump         # restaurar
createdb -U app demo_test && pg_restore -U app -d demo_test demo.dump  # verificar
```

Sintaxis propia de Postgres (sobre [[SQL]] estándar):

| Sintaxis | Uso |
|---|---|
| `JSONB`: `->`, `->>`, `@>`, `?` | Datos indexables con GIN |
| `ARRAY[...]` + `ANY()` / `@>` | Arreglos nativos |
| `INSERT ... ON CONFLICT (col) DO UPDATE` / `DO NOTHING RETURNING id` | Upsert |
| `UPDATE ... FROM ...` / `DELETE ... USING ...` | Escrituras con join |
| `RETURNING *` | Ver filas afectadas |
| `WITH ... AS (...)`, `AS MATERIALIZED` | CTE |
| `ROW_NUMBER()`, `LAG()`, `SUM() OVER (...)` | Window functions |
| `LATERAL JOIN`, `FILTER (WHERE ...)` | Top-N por grupo / agregación condicional |
| `EXPLAIN (ANALYZE, BUFFERS)` | Plan real |
| `pg_stat_*`, `pg_locks`, `pg_stat_activity` | Observabilidad |

## 4. Flujo diario / ejemplo mínimo

```bash
pg_isready -h localhost -p 5432
psql -U app -d demo -c "SELECT count(*) FROM tienda.pedidos;"
```

```sql
\d+ tienda.pedidos
WITH totales AS (
  SELECT cliente_id, SUM(total) AS facturado, COUNT(*) AS n
  FROM tienda.pedidos WHERE estado = 'pagado' GROUP BY cliente_id
)
SELECT c.nombre, c.metadata->>'plan' AS plan, t.facturado, t.n
FROM tienda.clientes c JOIN totales t ON t.cliente_id = c.id
WHERE c.metadata @> '{"region":"ar"}'::jsonb
ORDER BY t.facturado DESC;
BEGIN;
INSERT INTO tienda.clientes (nombre,email,metadata)
VALUES ('Ana','ana@example.com','{"plan":"pro"}')
ON CONFLICT (email) DO UPDATE SET metadata = EXCLUDED.metadata
RETURNING id, nombre, metadata;
COMMIT;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tienda.pedidos WHERE cliente_id = 1;
```

```bash
psql -U app -d demo -v ON_ERROR_STOP=1 -f migrations/001_add_pedidos.sql
```

> El driver de tu lenguaje ([[SQL]] desde Java/JavaScript/Python) usa **prepared statements**: parámetros separados del texto → sin inyección.

## 5. Profundidad: internals y arquitectura

```text
        ┌──────── postgres (postmaster) ────────┐
        │ checkpointer, walwriter, autovacuum, │
        │ bgwriter, stats collector            │
        └────────────────┬──────────────────────┘
  cliente → backend ─────┤ shared_buffers (caché de páginas)
  cliente → backend ─────┤ WAL buffers
  cliente → backend ─────┘ work_mem (por sort/hash/sesión)
```

Cada conexión es un **proceso**, no un thread: por eso `max_connections` alto consume memoria; usá pgbouncer en producción. `work_mem` se reserva **por nodo del plan**, no por sesión: 3 sorts = hasta `3 × work_mem`.

**MVCC por dentro:** cada tupla tiene `xmin`, `xmax`, `ctid` e `infomask`.

```sql
SELECT xmin, xmax, ctid, id, total FROM tienda.pedidos WHERE id = 1;
```

`UPDATE` = nueva versión + marca de la vieja; los índices apuntan a ambas. Sin `VACUUM` queda **bloat** y crece el txid (riesgo de *wraparound*). `autovacuum` hace esto solo; desactivarlo es un error clásico. `VACUUM FULL` bloquea con ACCESS EXCLUSIVE: para producción, `pg_repack`.

**WAL y HA:** `wal_level = replica`, `archive_mode = on`, `archive_command` a S3. PITR = `pg_basebackup` + WAL + `recovery_target_time`. Réplicas **físicas** (streaming, byte a byte) vs **lógicas** (publication/subscription, filtrables por tabla).

```sql
SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
SELECT client_addr, state, sent_lsn, replay_lsn FROM pg_stat_replication;
```

**Planner:** `parse → analyze → rewrite → paths (Seq/Index/Bitmap Scan, Hash/Nested/Merge Join) → elegir el más barato → execute`. `ANALYZE` muestrea con `default_statistics_target` (subilo por columna con `ALTER TABLE ... ALTER COLUMN ... SET STATISTICS 500`).

| | PostgreSQL | [[MySQL - MariaDB]] | [[Oracle]] | [[SQL Server]] | [[SQLite]] |
|---|---|---|---|---|---|
| Licencia | BSD-like | GPL/comercial | Comercial | Comercial | Dominio público |
| DDL transaccional | ✅ | ❌ | Parcial | ✅ | ✅ |
| JSON | `JSONB` + GIN | texto + expresión | `JSON`/`JSONB` | `OPENJSON` | `JSON1` |
| Tipos custom | ✅ | ❌ | ✅ | Parcial | ❌ |
| Índices | B-tree, GIN, GiST, BRIN | B-tree, FULLTEXT | B-tree, bitmap | B-tree, columnstore | B-tree |

Extensiones útiles:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- similitud / LIKE %
CREATE EXTENSION IF NOT EXISTS uuid-ossp;    -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS hstore;       -- key-value
CREATE EXTENSION IF NOT EXISTS postgis;      -- ver [[PostGIS]]
-- gen_random_uuid() ya está en el core desde PG13
```

## 6. Configuración avanzada y rendimiento

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, WAL) SELECT * FROM tienda.pedidos WHERE cliente_id = 1;
```

```text
Bitmap Heap Scan on pedidos  (cost=4.34..12.10 rows=3 width=48)
  (actual time=0.020..0.025 rows=3 loops=1)
  Buffers: shared hit=5
  ->  Bitmap Index Scan on idx_pedidos_cliente  (actual rows=3 loops=1)
        Index Cond: (cliente_id = 1)
Execution Time: 0.048 ms
```

| Señal | Interpretación | Acción |
|---|---|---|
| `Seq Scan` en tabla grande | Sin índice útil | Crear índice / revisar estimaciones |
| `rows=3` vs `actual rows=30000` | Stats viejas | `ANALYZE` |
| `external merge Disk` | `work_mem` bajo | Subirlo |
| `shared read` alto | Poco cacheado | Segunda ejecución; revisar `shared_buffers` |
| `Nested Loop` con millones | Join mal estimado | Índice en la inner |
| `Hash Buckets` + `Batch > 0` | Spill a disco | Subir `work_mem` |

```conf
# postgresql.conf: medí antes y después, nunca copies a ciegas
shared_buffers = 4GB               # ≈25% RAM
effective_cache_size = 12GB        # ~50-75% RAM
work_mem = 16MB
maintenance_work_mem = 512MB
random_page_cost = 1.1             # SSD/NVMe
max_connections = 100              # + pgbouncer
wal_level = replica
max_wal_size = 4GB
checkpoint_timeout = 15min
log_min_duration_statement = 500   # queries > 500 ms
```

```sql
-- Consultas más caras
SELECT calls, round(total_exec_time::numeric,1) AS total_ms, left(query,100)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
-- Bloat potencial
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;
-- Índices que nadie usa
SELECT indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0;
-- Locks bloqueantes
SELECT pid, mode, granted, relation::regclass FROM pg_locks WHERE NOT granted;
```

Patrones:

```sql
-- Paginación por cursor
SELECT id, total FROM tienda.pedidos WHERE id > :ultimo_id ORDER BY id LIMIT 20;
-- Sin función sobre columna indexada
-- ❌ WHERE created_at::date = '2026-11-24'
-- ✅
WHERE created_at >= '2026-11-24' AND created_at < '2026-11-25';
-- Agregación condicional en una pasada
SELECT COUNT(*) AS totales,
       COUNT(*) FILTER (WHERE estado='pagado') AS pagados,
       SUM(total) FILTER (WHERE estado='pagado') AS facturado
FROM tienda.pedidos;
-- Top 2 por cliente con LATERAL
SELECT c.nombre, p.id, p.total FROM tienda.clientes c
CROSS JOIN LATERAL (
  SELECT id, total FROM tienda.pedidos pe WHERE pe.cliente_id = c.id
  ORDER BY pe.total DESC LIMIT 2
) p;
-- Particionado declarativo
CREATE TABLE mediciones (fecha DATE NOT NULL, valor NUMERIC) PARTITION BY RANGE (fecha);
CREATE TABLE mediciones_2026_11 PARTITION OF mediciones
  FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
ALTER TABLE mediciones DETACH PARTITION mediciones_2026_11;
```

```bash
psql -U app -d demo -c "\copy tienda.pedidos(cliente_id,total,estado) FROM 'pedidos.csv' CSV HEADER"
pgbench -i -s 10 tienda && pgbench -c 10 -j 2 -T 60 tienda
```

> Particioná por una clave presente en casi todas las consultas (fecha/tenant). Si no, el planner no poda y solo sumás complejidad.

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `password authentication failed for user "app"` | Password o `pg_hba.conf` | `ALTER ROLE app PASSWORD '...'`; `scram-sha-256` |
| `could not connect: Connection refused` | Servidor caído / `listen_addresses` | `systemctl status postgresql`, `pg_isready` |
| `database "demo" does not exist` | Falta crearla | `\l`, `CREATE DATABASE demo OWNER app;` |
| `relation "pedidos" does not exist` | `search_path`/schema | `SET search_path TO tienda, public;` |
| `permission denied for schema/table` | Rol sin grants | `GRANT USAGE ...`, `GRANT SELECT ...` |
| `duplicate key value violates unique constraint` | Conflicto | `ON CONFLICT ... DO UPDATE` |
| `violates foreign key constraint` | ID inexistente | `SELECT id FROM clientes WHERE id=...` |
| `canceling statement due to conflict with recovery` | Réplica con query larga | `hot_standby_feedback` / acortar query |
| `deadlock detected` | Locks en orden distinto | Ordenar acceso; reintentar |
| `could not serialize access` | `SERIALIZABLE` | Reintentar (SQLSTATE 40001) |
| `out of shared memory` | Muchas particiones / `max_locks_per_transaction` | Subir el parámetro |
| `too many clients already` | Sin pool | pgbouncer; cerrar idle |
| `query suddenly slow` | Stats/bloat/plan | `ANALYZE`, `VACUUM`, `EXPLAIN ANALYZE` |
| `no space left on device` | WAL/bloat | `du -sh $PGDATA/pg_wal`, limpiar slots inactivos |
| `WAL archive failed` | `archive_command` sin permisos | Probar el comando a mano |
| `current transaction is aborted` | Error en `BEGIN` | `ROLLBACK` o `SAVEPOINT` |
| `operator does not exist: text = integer` | Tipos distintos | Castear: `col::int` o `= '5'` |

```bash
tail -n 200 /var/log/postgresql/postgresql-16-main.log
psql -U app -d demo -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

## 8. Seguridad y buenas prácticas

```sql
CREATE ROLE rol_lectura NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA tienda TO rol_lectura;
CREATE ROLE app_svc LOGIN PASSWORD 'secret';
GRANT rol_lectura TO app_svc;
ALTER DATABASE demo OWNER TO app_svc;
REVOKE ALL ON TABLE tienda.clientes FROM PUBLIC;
```

```conf
# pg_hba.conf: nunca "trust" en IP accesible
local  all  all              peer
host   demo app_svc 10.0.0.0/24  scram-sha-256
hostssl all  all    0.0.0.0/0    scram-sha-256
```

Row Level Security:

```sql
ALTER TABLE tienda.pedidos ENABLE ROW LEVEL SECURITY;
CREATE POLICY pedidos_por_tenant ON tienda.pedidos
  USING (cliente_id = current_setting('app.tenant_id')::bigint);
SET app.tenant_id = '1';
SELECT * FROM tienda.pedidos;   -- solo los del tenant
```

Checklist: prepared statements ([[SQL]] seguro); TLS `verify-full`; sin superuser en la app; secrets rotados fuera del repo; backup con restore probado ([[Backups y recovery]]); `autovacuum` activo con alertas; `statement_timeout` e `idle_in_transaction_session_timeout`; logs de queries lentas y locks; migraciones con `ON_ERROR_STOP=1`; auditoría de datos sensibles.

Cuando el motor está administrado ([[RDS]]), no tocás `postgresql.conf`: usás parameter groups. Seguís responsable por roles, esquemas, índices, consultas y backups lógicos.

## 9. Ejercicios para dominarlo

1. Instalá Postgres (o el contenedor), conectate con `psql` y ejecutá `\conninfo`, `\dt`, `SELECT version();`.
2. Creá el esquema del apartado 2 con `ON_ERROR_STOP=1`; agregá un `CHECK` que prohíba totales negativos y comprobá que falle.
3. Cargá 1000 pedidos con `\copy` desde CSV y compará el tiempo contra 1000 `INSERT` individuales.
4. `UPDATE` sobre `pedidos`: mirá `xmin`, `xmax`, `ctid` antes/después; ejecutá `VACUUM (VERBOSE)` y explicá qué cambió.
5. `EXPLAIN (ANALYZE, BUFFERS)` antes y después de `CREATE INDEX`; compará `cost`, `actual rows` y `Buffers`.
6. Activá `pg_stat_statements`, generá carga con `pgbench` y listá el top 5 por `total_exec_time`.
7. `pg_dump -Fc`, borrá una tabla en la base de prueba y restaurá solo esa tabla con `pg_restore -t`.
8. Creá el rol `lector` sin escritura, conectate con él y confirmá que un `INSERT` falla con `permission denied`.
9. Activá RLS, seteá `app.tenant_id` y verificá que dos sesiones vean conjuntos distintos.

## 10. Relaciones

[[PostgreSQL]] · [[SQL]] · [[RDS]] · [[Backups y recovery]] · [[PostGIS]] · [[MySQL - MariaDB]] · [[Oracle]] · [[SQL Server]] · [[SQLite]] · [[RAG]]
