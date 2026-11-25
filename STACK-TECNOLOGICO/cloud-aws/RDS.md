---
titulo: "RDS"
categoria:
  - "8. Cloud / AWS"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "cloud-aws"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[Terraform]]"
  - "[[Backups y recovery]]"
  - "[[VPC]]"
  - "[[IAM]]"
  - "[[PostgreSQL]]"
  - "[[SQL]]"
  - "[[Aurora]]"
  - "[[DocumentDB]]"
  - "[[DynamoDB]]"
  - "[[ElastiCache]]"
  - "[[Neptune]]"
  - "[[Redshift]]"
  - "[[Timestream]]"
---

# RDS — Guía completa ☁️🗄️

> ⭐ Núcleo imprescindible. Objetivo: saber **qué administra AWS y qué seguimos administrando nosotros**, crear una instancia con red y seguridad correctas, conectarse, hacer backup/restore y diagnosticar rendimiento o disponibilidad.

## 1. Mentalidad: qué es RDS (y qué NO es)

Amazon Relational Database Service es un **motor relacional administrado**. AWS maneja hardware, SO, parcheo del motor, failover y backups automáticos. Vos seguís responsable del esquema, las consultas, los índices, los usuarios, los parámetros y el dimensionamiento.

> Frase para entrevista: *"RDS no es una base en una EC2: es un servicio administrado con responsabilidad compartida; AWS gestiona infraestructura, yo gestiono datos y acceso"*.

| Idea errónea | Realidad |
|---|---|
| "Es como instalar PostgreSQL en una EC2" | No tenés shell ni raíz del filesystem |
| "El backup resuelve mi DR" | Hay backups, pero hay que probar el restore y definir RTO/RPO |
| "Multi-AZ protege de un `DROP TABLE`" | Es HA, **no** protección contra errores lógicos |
| "Escala solo" | Escalás verticalmente o con read replicas; Aurora Serverless es aparte |
| "Es igual a Aurora" | [[Aurora]] es otro motor con storage distribuido; ver su nota |
| "Sirve para todo" | Clave-valor: [[DynamoDB]]; caché: [[ElastiCache]]; grafo: [[Neptune]]; analítica: [[Redshift]]; series: [[Timestream]] |

| Capa | AWS | Vos |
|---|---|---|
| Hardware / SO / parcheo | ✅ | Elegir ventana de mantenimiento |
| Motor y upgrades mayores | ✅ lo ejecuta | Vos los decidís |
| Failover Multi-AZ | ✅ | App con reconexión y retry |
| Backups automáticos | ✅ | Retención, snapshots manuales, probar restore |
| Red | Configura el endpoint | Security groups, subnets, [[VPC]] |
| Identidad | — | [[IAM]], roles y credenciales |
| Datos | — | Esquema, índices, consultas, cifrado, auditoría |

Motores: PostgreSQL (esta nota), MySQL/MariaDB, [[Aurora]], Oracle, SQL Server, [[DocumentDB]], [[Neptune]].

## 2. Instalación y primeros pasos (AWS CLI)

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
aws --version && aws configure
aws sts get-caller-identity          # confirmar identidad [[IAM]]
```

> En producción usá roles de [[IAM]] (instancias, SSO, CI) en vez de claves de largo plazo.

Prerequisitos de red ([[VPC]]):

```bash
aws ec2 describe-subnets --query 'Subnets[*].[SubnetId,AvailabilityZone,CidrBlock]' --output table
export VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=main" \
  --query 'Vpcs[0].VpcId' --output text)

aws rds create-db-subnet-group --db-subnet-group-name tienda-subnets \
  --db-subnet-group-description "Subnets privadas para RDS" --subnet-ids subnet-aaa subnet-bbb

aws ec2 create-security-group --group-name rds-tienda-sg \
  --description "Acceso a RDS desde app" --vpc-id "$VPC_ID"
export SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=rds-tienda-sg" \
  --query 'SecurityGroups[0].GroupId' --output text)

# Solo desde el SG de la app, nunca 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
  --protocol tcp --port 5432 --source-group sg-APP_ID
```

Crear la instancia:

```bash
aws rds create-db-instance \
  --db-instance-identifier tienda-dev --db-instance-class db.t3.medium \
  --engine postgres --engine-version 16.3 \
  --master-username appadmin --master-user-password 'CambiaEstePassword123!' \
  --allocated-storage 20 --storage-type gp3 \
  --db-subnet-group-name tienda-subnets --vpc-security-group-ids "$SG_ID" \
  --db-name tienda --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "sun:04:05-sun:04:35" \
  --auto-minor-version-upgrade --deletion-protection \
  --tags Key=Environment,Value=dev

aws rds wait db-instance-available --db-instance-identifier tienda-dev
aws rds describe-db-instances --db-instance-identifier tienda-dev \
  --query 'DBInstances[0].[DBInstanceIdentifier,DBInstanceStatus,Engine,Endpoint.Address,Endpoint.Port,MultiAZ,StorageEncrypted]' \
  --output table
```

Conectar (desde EC2 con acceso, o por túnel):

```bash
export RDS_HOST=$(aws rds describe-db-instances --db-instance-identifier tienda-dev \
  --query 'DBInstances[0].Endpoint.Address' --output text)
psql "host=$RDS_HOST port=5432 dbname=tienda user=appadmin sslmode=require" -c "SELECT version();"

# Desde la laptop con bastión
ssh -L 5432:$RDS_HOST:5432 ec2-user@bastion -N
psql "host=localhost port=5432 dbname=tienda user=appadmin sslmode=require"
```

Verificación mínima con [[SQL]]:

```sql
SELECT current_database(), current_user, version();
CREATE TABLE health (id SERIAL PRIMARY KEY, ok BOOLEAN NOT NULL DEFAULT true);
INSERT INTO health DEFAULT VALUES;
SELECT * FROM health;
```

> `sslmode=require` cifra pero no valida el certificado. En producción: `sslmode=verify-full` y `rds.force_ssl=1`.

## 3. Cheat sheet

| Comando | Qué hace |
|---|---|
| `aws rds describe-db-instances` | Lista instancias |
| `aws rds describe-db-instances --db-instance-identifier X` | Detalle |
| `aws rds wait db-instance-available --db-instance-identifier X` | Esperar a `available` |
| `aws rds modify-db-instance --db-instance-identifier X --apply-immediately ...` | Modificar |
| `aws rds reboot-db-instance --db-instance-identifier X [--failover]` | Reiniciar / failover |
| `aws rds stop-db-instance` / `start-db-instance` | Ahorro en dev |
| `aws rds delete-db-instance --db-instance-identifier X --skip-final-snapshot` | ⚠️ Borrar sin snapshot |
| `aws rds list-tags-for-resource --resource-name ARN` | Tags |
| `aws rds describe-db-logs --db-instance-identifier X` | Logs del motor |

Seguridad y parámetros:

```bash
aws rds describe-db-security-groups
aws rds modify-db-instance --db-instance-identifier tienda-dev \
  --vpc-security-group-ids "$SG_ID" --apply-immediately

# IAM database authentication (tokens de 15 min)
aws rds modify-db-instance --db-instance-identifier tienda-dev \
  --enable-iam-database-authentication --apply-immediately
aws rds generate-db-auth-token --hostname "$RDS_HOST" --port 5432 \
  --region us-east-1 --username appadmin

aws rds describe-db-parameters --db-parameter-group-name default.postgres16 \
  --query 'Parameters[?IsModifiable==`true`]'
aws rds create-db-parameter-group --db-parameter-group-name tienda-pg16 \
  --db-parameter-group-family postgres16 --description "Parámetros de tienda"
aws rds modify-db-parameter-group --db-parameter-group-name tienda-pg16 \
  --parameters "ParameterName=work_mem,ParameterValue=16384,ApplyMethod=pending-reboot" \
              "ParameterName=log_min_duration_statement,ParameterValue=500,ApplyMethod=immediate"
aws rds modify-db-instance --db-instance-identifier tienda-dev \
  --db-parameter-group-name tienda-pg16 --apply-immediately
```

> `immediate` aplica parámetros dinámicos; los estáticos (`shared_buffers`) quedan `pending-reboot`.

Backups, restore y réplicas:

```bash
aws rds describe-db-instances --db-instance-identifier tienda-dev \
  --query 'DBInstances[0].[BackupRetentionPeriod,LatestRestorableTime,PreferredBackupWindow]'
aws rds create-db-snapshot --db-instance-identifier tienda-dev \
  --db-snapshot-identifier tienda-dev-pre-migracion-20261124
aws rds describe-db-snapshots --db-snapshot-identifier tienda-dev-pre-migracion-20261124
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier tienda-restore \
  --db-snapshot-identifier tienda-dev-pre-migracion-20261124 --db-instance-class db.t3.medium

# PITR
aws rds restore-db-instance-to-point-in-time --source-db-instance-identifier tienda-dev \
  --target-db-instance-identifier tienda-pitr --restore-time 2026-11-24T10:30:00Z

# Exportar a S3
aws rds start-export-task --export-task-identifier export-tienda-20261124 \
  --source-arn "arn:aws:rds:us-east-1:123456789012:snapshot:tienda-dev-pre-migracion-20261124" \
  --s3-bucket-name mi-bucket-backups \
  --iam-role-arn arn:aws:iam::123456789012:role/RDSExportRole

# Alta disponibilidad y escalado de lectura
aws rds modify-db-instance --db-instance-identifier tienda-dev --multi-az --apply-immediately
aws rds create-db-instance-read-replica --db-instance-identifier tienda-read-1 \
  --source-db-instance-identifier tienda-dev --db-instance-class db.t3.medium
aws rds promote-read-replica --db-instance-identifier tienda-read-1
```

Monitoreo:

```bash
aws rds describe-db-log-files --db-instance-identifier tienda-dev
aws rds download-db-log-file-portion --db-instance-identifier tienda-dev \
  --log-file-name error/postgresql.log.2026-11-24-00 --output text
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=tienda-dev \
  --start-time 2026-11-23T00:00:00Z --end-time 2026-11-24T00:00:00Z \
  --period 3600 --statistics Average,Maximum
```

## 4. Flujo diario / ejemplo mínimo

```bash
aws rds describe-db-instances --db-instance-identifier tienda-dev \
  --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address,MultiAZ,DBInstanceClass]' --output table
export RDS_HOST=$(aws rds describe-db-instances --db-instance-identifier tienda-dev \
  --query 'DBInstances[0].Endpoint.Address' --output text)
psql "host=$RDS_HOST dbname=tienda user=appadmin sslmode=require" -c "
  SELECT count(*) AS clientes FROM public.clientes;
  SELECT query, calls, mean_exec_time FROM pg_stat_statements
  ORDER BY total_exec_time DESC LIMIT 5;"

# Antes de migrar: snapshot
aws rds create-db-snapshot --db-instance-identifier tienda-dev \
  --db-snapshot-identifier tienda-dev-pre-cambio-$(date +%Y%m%d)
psql "host=$RDS_HOST dbname=tienda user=appadmin sslmode=require" \
  -v ON_ERROR_STOP=1 -f migrations/001_nueva_columna.sql

# Después: medir
aws cloudwatch get-metric-statistics --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=tienda-dev \
  --start-time 2026-11-24T09:00:00Z --end-time 2026-11-24T10:00:00Z \
  --period 300 --statistics Average
```

**Checklist:** estado → conexión TLS → queries lentas → snapshot → migración con `ON_ERROR_STOP` → CPU/conexiones/latencia → rollback documentado.

## 5. Profundidad: arquitectura y comparativas

```text
RDS API → control plane → aprovisiona ENI en tu [[VPC]] → elige AZ (o dos si Multi-AZ)
        → lanza host administrado → configura backups y SG → expone endpoint DNS estable
```

El endpoint DNS es clave: en un failover Multi-AZ el nombre no cambia, AWS redirige el CNAME. Los sockets se cortan: la app debe **reconectar con retry**.

| Modo | Protege ante | No protege ante |
|---|---|---|
| Backup automático | Falla de instancia, error lógico vía PITR | Región completa |
| Multi-AZ | Caída de AZ/host/motor (60–120 s) | `DELETE` accidental |
| Read replica | Escalar `SELECT`, DR regional | Escrituras |
| Snapshot manual | Cambios planeados, cumplimiento | — |

Storage gp2/gp3/io1 es replicado dentro de la AZ por EBS. Multi-AZ = réplica **síncrona** en otra AZ (standby no acepta queries). Read replicas son **asíncronas**. Backups = snapshot diario + WAL → PITR desde `LatestRestorableTime` (retención 1–35 días).

| Familia | Perfil | Uso |
|---|---|---|
| `db.t3 / db.t4g` | Burstable, créditos CPU | Dev (⚠️ se agotan) |
| `db.m6g / db.m7g` | General purpose (Graviton) | OLTP equilibrado |
| `db.r6g / db.r7g` | Memory optimized | Joins grandes, caché |
| `db.c*` | Compute optimized | Cálculo intensivo |

En [[PostgreSQL]] local editás `postgresql.conf`; en RDS usás **parameter groups**:

| Parámetro | RDS típico | Comentario |
|---|---|---|
| `shared_buffers` | ≈25% RAM | No cambiable en clases chicas |
| `work_mem` | 4 MB | Subir para sorts, con cuidado |
| `max_connections` | Según clase | Usá RDS Proxy antes que subirlo |
| `rds.force_ssl` | 0 | Poner 1 en producción |
| `statement_timeout` | 0 | Recomendado 30–60 s |
| `autovacuum_*` | Activo | Ajustar en tablas con rotación |

Red: instancia **privada** (`PubliclyAccessible=false`), dos subnets en AZ distintas, ingress solo desde el SG de la app. RDS Proxy agrupa conexiones y mejora failover. Acceso externo: VPN, Direct Connect o bastion.

Costos: instancia por hora (Multi-AZ ≈ 2×), storage por GB-mes, IOPS, backup gratis hasta el 100% del storage, transferencia de salida.

```bash
aws ce get-cost-and-usage --time-period Start=2026-11-01,End=2026-11-24 \
  --granularity MONTHLY --metrics BlendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Relational Database Service"]}}'
```

| Servicio | Tipo | Cuándo |
|---|---|---|
| **RDS** | Relacional administrado | [[SQL]] transaccional |
| [[Aurora]] | Relacional cloud-native | HA, escalado de lectura, serverless |
| [[DynamoDB]] | Clave-valor | Escala masiva por key |
| [[DocumentDB]] | Documentos | Compatibilidad MongoDB |
| [[ElastiCache]] | Caché | Bajar latencia y carga de DB |
| [[Neptune]] / [[Redshift]] / [[Timestream]] | Grafo / OLAP / series | Según el dato |

Infraestructura como código con [[Terraform]]:

```hcl
resource "aws_db_instance" "tienda" {
  identifier            = "tienda-dev"
  engine                = "postgres"
  engine_version        = "16.3"
  instance_class        = "db.t3.medium"
  allocated_storage     = 20
  storage_type          = "gp3"
  storage_encrypted     = true
  db_name               = "tienda"
  username              = "appadmin"
  password              = var.db_password
  db_subnet_group_name  = aws_db_subnet_group.tienda.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  backup_retention_period = 7
  multi_az              = true
  deletion_protection   = true
  skip_final_snapshot   = false
  final_snapshot_identifier = "tienda-dev-final"
}
```

```bash
terraform init && terraform plan && terraform apply
```

## 6. Configuración avanzada y rendimiento

| Métrica | Umbral | Acción |
|---|---|---|
| `CPUUtilization` > 80% sostenido | Alto | Índices, optimizar queries, escalar a `m6g` |
| `DBLoad` con `WaitEvent: CPU` | Workload pesado | `pg_stat_statements` |
| `ReadLatency`/`WriteLatency` > 10 ms | Storage lento | Más IOPS gp3 o io2 |
| `FreeStorageSpace` cayendo | Bloat/crecimiento | Limpiar, ampliar storage |
| `DatabaseConnections` cerca del máximo | Sin pool | RDS Proxy |
| `ReplicaLag` creciendo | Réplica chica/locks | Escalar, `statement_timeout` |

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;
SELECT calls, round(total_exec_time::numeric,1) AS total_ms, left(query,90)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;
```

Escalado y upgrades:

```bash
aws rds modify-db-instance --db-instance-identifier tienda-dev \
  --db-instance-class db.m6g.large --apply-immediately
aws rds modify-db-instance --db-instance-identifier tienda-dev \
  --allocated-storage 100 --apply-immediately
aws rds reboot-db-instance --db-instance-identifier tienda-dev --failover   # prueba de DR
aws rds describe-db-engine-versions --engine postgres \
  --query 'DBEngineVersions[*].EngineVersion' --output text | tr '\t' '\n' | sort -V | tail
aws rds create-blue-green-deployment --blue-green-deployment-name tienda-pg15-a-pg16 \
  --source-arn "arn:aws:rds:us-east-1:123456789012:db:tienda-dev" \
  --target-engine-version 16.3 --target-db-parameter-group-name tienda-pg16
```

Buenas prácticas de operación: `deletion_protection=true`, `skip_final_snapshot=false`, retención ≥ 7 días, snapshot manual antes de migrar, probar restore trimestralmente ([[Backups y recovery]]), ventana de mantenimiento fuera de pico, suscripción a eventos:

```bash
aws rds create-event-subscription --subscription-name rds-tienda-events \
  --sns-topic-arn arn:aws:sns:us-east-1:123456789012:rds-alerts \
  --event-categories "failover" "maintenance" "backup" "configuration-change"
```

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `psql: Connection timed out` | SG o ruta | Revisar ingress desde SG de app y route table |
| `FATAL: password authentication failed` | Password rotada | Secret; `modify-db-instance --master-user-password` |
| `database "tienda" does not exist` | Olvidaste `--db-name` | `CREATE DATABASE tienda;` |
| `SSL connection required` | `rds.force_ssl=1` sin TLS | `sslmode=require`/`verify-full` |
| `DBInstanceStatus: starting` mucho tiempo | Aprovisionamiento | `describe-db-instances` + eventos |
| `subnet group needs 2 AZ` | Solo una subnet | Agregar subnet de otra AZ |
| `Parameter group incompatible` | Family `postgres15` vs `16` | Crear grupo `postgres16` |
| Parámetro no aplica | `pending-reboot` | `reboot-db-instance --failover` |
| CPU al 100% | Queries/índices o créditos t3 agotados | `pg_stat_statements`, escalar a m6g |
| `ReplicaLag` creciente | Réplica chica o locks | Escalar, revisar `pg_stat_replication` |
| `no space left on device` | Storage lleno | Ampliar storage, revisar `autovacuum` |
| `restore: instance already exists` | Nombre duplicado | Cambiar `--target-db-instance-identifier` |
| PITR no disponible | Fuera de `LatestRestorableTime` | Aumentar retención / snapshot manual |
| Failover ~2 min | Esperado | Retry + reconexión en la app |
| Snapshot export failed | Rol sin permiso S3 | Verificar `iam-role-arn` y bucket policy |
| Endpoint inalcanzable desde laptop | Sin VPN/bastion | Tunnel SSH, VPN, Direct Connect |
| Costo inesperado | Multi-AZ, réplicas, transferencia | Cost Explorer + tags |

```bash
aws rds describe-events --source-identifier tienda-dev --duration 60 \
  --event-categories failover maintenance backup
aws rds describe-db-instance-automated-backups --db-instance-identifier tienda-dev
aws rds describe-db-snapshots --db-instance-identifier tienda-dev \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' --output table
```

## 8. Seguridad y buenas prácticas

Checklist: `PubliclyAccessible=false` y subnets privadas; SG con ingress solo desde la app; `StorageEncrypted=true` (se define al crear); `rds.force_ssl=1` + `sslmode=verify-full`; credenciales en secret manager con rotación; IAM auth si querés tokens de 15 min; `deletion_protection` y `skip_final_snapshot=false`; logs a CloudWatch con alertas; least privilege en [[IAM]]; `pgAudit` si hay requisitos regulatorios; backups cifrados y copia cross-region.

```bash
TOKEN=$(aws rds generate-db-auth-token --hostname "$RDS_HOST" --port 5432 \
  --region us-east-1 --username appadmin)
PGPASSWORD="$TOKEN" psql "host=$RDS_HOST port=5432 dbname=tienda user=appadmin sslmode=verify-full"
```

> El token expira en 15 minutos: generarlo justo antes de conectar. Para pools persistentes, RDS Proxy.

Política [[IAM]] mínima para operar:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["rds:DescribeDBInstances","rds:DescribeDBSnapshots","rds:ListTagsForResource"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["rds:CreateDBSnapshot","rds:ModifyDBInstance"],
      "Resource": "arn:aws:rds:us-east-1:123456789012:db:tienda-*" }
  ]
}
```

## 9. Ejercicios para dominarlo

1. Creá un DB subnet group con dos AZ y una instancia `db.t3.micro` con `PubliclyAccessible=false`; verificá el endpoint con `describe-db-instances`.
2. Intentá conectar desde la laptop sin VPN (confirmá el timeout), agregá una regla de SG desde tu IP, conectate con `psql` y retirá la regla.
3. Ejecutá `CREATE TABLE`, `INSERT` y `SELECT` con [[SQL]] usando `sslmode=require`.
4. Hacé un `create-db-snapshot`, borrá una fila y restaurá una instancia nueva; verificá que la fila volvió.
5. Probá PITR: insertá una marca, esperá minutos, restaurá a un `--restore-time` anterior y compará `COUNT(*)`.
6. habilitá `multi-az`, corré `reboot-db-instance --failover` y medí el tiempo hasta `available`; documentá el error que vio la app.
7. Creá un parameter group con `log_min_duration_statement=500` y `statement_timeout=30000`; verificá con `SHOW`.
8. Creá una read replica, dirigile un `SELECT` y confirmá que un `INSERT` falla; promovela y repetí.
9. Definí el mismo recurso con [[Terraform]], cambiá `backup_retention_period` y compará el `plan`.
10. Usá Cost Explorer para medir el costo de la instancia y cuánto sumarían Multi-AZ y una réplica.

## 10. Relaciones

[[RDS]] · [[PostgreSQL]] · [[SQL]] · [[VPC]] · [[IAM]] · [[Terraform]] · [[Backups y recovery]] · [[Aurora]] · [[DynamoDB]] · [[DocumentDB]] · [[ElastiCache]] · [[Neptune]] · [[Redshift]] · [[Timestream]]
