---
titulo: "Docker"
categoria:
  - "6. Contenerización y orquestación"
  - "19. Sistemas operativos (lo que deberías saber hoy)"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "contenerización-y-orquestación"
  - "sistemas-operativos-lo-que-deberías-saber-hoy"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[Traefik]]"
  - "[[Husky]]"
  - "[[Fargate]]"
  - "[[Capabilities - setuid]]"
  - "[[Docker Compose]]"
  - "[[Docker Hub]]"
  - "[[Dockerfile multi-stage]]"
  - "[[ECR]]"
  - "[[Healthchecks]]"
  - "[[Kernel vs userspace - libc - glibc - musl - ABI]]"
  - "[[Kubernetes]]"
  - "[[Namespaces (PID, mount, network, user, IPC, UTS, cgroup)]]"
  - "[[Portainer]]"
---

# Docker — Guía completa 🐳

> ⭐ Núcleo imprescindible. Objetivo: instalarlo, entender **qué es un contenedor de verdad**, usar sus comandos sin buscarlos, escribir Dockerfiles decentes y saber depurar cuando "no arranca".

## 1. Mentalidad: qué es (y qué NO es) un contenedor

Un contenedor **no es una máquina virtual**. Es un **proceso normal de Linux** al que el kernel le puso límites y aislamiento:

- [[Namespaces (PID, mount, network, user, IPC, UTS, cgroup)]] → *"ves solo tus procesos, tu red, tus montajes"*.
- [[cgroups]] → *"no podés usar más de X CPU/RAM"*.
- [[Capabilities - setuid]], [[seccomp - AppArmor - SELinux]], [[chroot]] → *"no podés hacer ciertas llamadas al kernel"*.

Todo eso nace del [[Kernel vs userspace - libc - glibc - musl - ABI]] del **host**. Por eso un contenedor Linux no "trae su kernel": comparte el del anfitrión (en macOS/Windows, Docker corre una VM Linux liviana con [[WSL]] / Hyper-V).

| Concepto | Definición rápida |
|---|---|
| **Imagen** | Plantilla inmutable, apilada en capas (layers). Es un *archivo*. |
| **Contenedor** | Instancia en ejecución de una imagen. Es un *proceso*. |
| **Layer** | Cada `RUN`/`COPY` del Dockerfile genera una capa reutilizable en caché. |
| **Registry** | Donde se guardan imágenes: [[Docker Hub]], [[ECR]], GitHub Container Registry. |
| **Tag** | `python:3.12-slim` → `repositorio:versión`. `latest` es el default (evítalo en producción). |
| **Digest** | Hash SHA256 inmutable: `python@sha256:abcd...`. Lo más seguro para deploys. |
| **Runtime** | `containerd` + `runc` por debajo de Docker Engine. |

> Frase para entrevista: *"Contenedor = proceso + namespaces + cgroups + filesystem por capas; no es virtualización de hardware"*.

---

## 2. Instalación

### Linux (Docker Engine)

```bash
# 1) Quitar versiones viejas
sudo apt remove docker docker-engine docker.io containerd runc 2>/dev/null

# 2) Preparar repositorio oficial
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3) Instalar
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4) Permitir usar docker sin sudo (¡cierra sesión y vuelve a entrar!)
sudo usermod -aG docker $USER
newgrp docker

# 5) Verificar
docker version
docker run hello-world
systemctl status docker
sudo systemctl enable --now docker
```

En Fedora/RHEL: `sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`.
En Arch: `sudo pacman -S docker docker-compose-plugin && sudo systemctl enable --now docker`.

> ⚠️ Agregar a un usuario al grupo `docker` es equivalente a darle **root** (ver [[Usuario root - UID - GID - sudo]]). En servidores, mejor usar `sudo docker` con `sudoers` restringido o rootless Docker.

### macOS

```bash
# Opción recomendada: Homebrew
brew install --cask docker

# O descargar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop/
```

Abrí Docker Desktop → *Settings → Resources* (CPU/RAM/Disco) → aplicar. Verificá con `docker run hello-world`.

### Windows

```powershell
winget install --id Docker.DockerDesktop
# O: https://www.docker.com/products/docker-desktop/
```

Requiere **WSL2** habilitado:

```powershell
wsl --install
wsl --set-default-version 2
docker info   # debe mostrar "Operating System: Docker Desktop" y WSL2
```

> En Windows trabajá siempre desde **WSL2** (`ubuntu` terminal) para que los volúmenes montados y los permisos de archivos se comporten como en Linux. Ver [[WSL]] y [[WSL]].

### Comprobación rápida

```bash
docker --version              # versión del CLI
docker info                   # servidor, drivers, CPUs, memoria, runtime
docker version                # cliente + servidor
docker run --rm hello-world   # prueba end-to-end
```

---

## 3. Comandos esenciales (cheat sheet)

### Imágenes

| Comando | Qué hace |
|---|---|
| `docker images` / `docker image ls` | Lista imágenes locales |
| `docker pull python:3.12-slim` | Descarga imagen del registry |
| `docker pull python@sha256:...` | Descarga por digest (inmutable) |
| `docker build -t miapp:1.0 .` | Construye desde Dockerfile |
| `docker build --no-cache -t miapp:1.0 .` | Sin caché |
| `docker build --build-arg VERSION=1.2 -t miapp .` | Pasa `ARG` |
| `docker tag miapp:1.0Usuario/e miapp:latest` | Renombra/etiqueta |
| `docker push usuario/miapp:1.0` | Sube a [[Docker Hub]] |
| `docker rmi imagen` / `docker image prune -a` | Borra imagen / huérfanas |
| `docker history miapp:1.0` | Muestra capas y tamaños |
| `docker inspect miapp:1.0` | JSON completo de metadatos |
| `docker save miapp:1.0 -o miapp.tar` | Exporta imagen (tar) |
| `docker load -i miapp.tar` | Importa imagen |
| `docker search nginx` | Busca en Docker Hub |

### Contenedores

| Comando | Qué hace |
|---|---|
| `docker run nginx` | Crea + arranca ( Primer arranque ) |
| `docker run -d --name web -p 8080:80 nginx` | Detach, nombre, publicar puerto |
| `docker run -it --rm ubuntu bash` | Interactivo, se borra al salir |
| `docker run --env KEY=val --env-file .env ...` | Variables de entorno |
| `docker run -v /host:/container ...` | Bind mount |
| `docker run -v datos:/var/lib/postgresql/data ...` | Named volume |
| `docker run --tmpfs /tmp ...` | tmpfs (memoria) |
| `docker run --network mi-red ...` | Conecta a red custom |
| `docker run --restart unless-stopped ...` | Política de reinicio |
| `docker run --memory=512m --cpus=1 ...` | Límites ([[cgroups]]) |
| `docker ps` / `docker ps -a` | Contenedores activos / todos |
| `docker logs -f --tail 100 web` | Logs en vivo ([[Logs estructurados]]) |
| `docker exec -it web bash` | Entrar a un contenedor activo |
| `docker exec -u 0 web whoami` | Entrar como root (solo debug) |
| `docker cp web:/etc/nginx/nginx.conf ./` | Copiar archivos dentro/fuera |
| `docker stop web` / `docker start web` / `docker restart web` | Ciclo de vida |
| `docker kill web` | Envía SIGKILL |
| `docker pause web` / `docker unpause web` | Congela procesos |
| `docker rm web` / `docker rm -f web` | Borra (fuerza si está activo) |
| `docker commit web miapp:debug` | ⚠️ Crea imagen desde un contenedor (no es reproducible) |
| `docker inspect web` | Config, IP, mounts, estado |
| `docker stats` | CPU/RAM/red en vivo |
| `docker top web` | Procesos dentro del contenedor |
| `docker port web` | Mapeo de puertos |
| `docker wait web` | Espera a que termine y devuelve exit code |
| `docker diff web` | Cambios en el filesystem vs imagen |
| `docker update --memory=1g web` | Cambia límites en caliente |

### Limpieza (¡con cuidado!)

```bash
docker container prune          # contenedores detenidos
docker image prune              # imágenes dangling
docker image prune -a           # todas las imágenes sin contenedor
docker volume prune             # volúmenes sin uso (¡puede borrar datos!)
docker network prune
docker system prune             # todo lo anterior (salvo volúmenes)
docker system prune -a --volumes  # ⚠️ RESET TOTAL
docker system df                # cuánto espacio usa Docker
```

> Antes de `prune` en producción: `docker ps -a` y `docker volume ls`. Los volúmenes con datos de [[PostgreSQL]]/[[RDS]] no se tocan sin backup ([[Backups y recovery]]).

---

## 4. Tu primer contenedor (paso a paso)

```bash
# 1) Descargar y arrancar un servidor web
docker run -d --name mi-nginx -p 8080:80 nginx:1.27-alpine

# 2) Verificar
docker ps
curl http://localhost:8080

# 3) Ver logs
docker logs -f mi-nginx

# 4) Entrar y modificar algo (solo para aprender)
docker exec -it mi-nginx sh
echo "<h1>Hola</h1>" > /usr/share/nginx/html/index.html
exit
curl http://localhost:8080

# 5) Limpiar
docker rm -f mi-nginx
```

**Explicación de `-p 8080:80`**: puerto `8080` del host → puerto `80` del contenedor. Sin `-p`, el contenedor solo es accesible desde la red interna de Docker.

---

## 5. Dockerfile: de cero a producción

### Instrucciones clave

| Instrucción | Uso |
|---|---|
| `FROM` | Imagen base (siempre primera) |
| `WORKDIR` | Directorio de trabajo (equivale a `cd`) |
| `COPY` / `ADD` | Copiar archivos (`ADD` además descomprime/URL; preferí `COPY`) |
| `RUN` | Ejecuta en **build time** (crea capa) |
| `ENV` | Variable de entorno persistente |
| `ARG` | Variable solo en build (`--build-arg`) |
| `EXPOSE` | Documenta el puerto (no lo publica) |
| `CMD` | Comando default (se puede sobrescribir con `docker run imagen cmd`) |
| `ENTRYPOINT` | Comando fijo (los args de `docker run` se le agregan) |
| `USER` | Cambia a usuario no-root |
| `HEALTHCHECK` | Define chequeo de salud ([[Healthchecks]]) |
| `VOLUME` | Marca un punto de montaje |
| `LABEL` | Metadatos (`org.opencontainers.image.*`) |
| `SHELL` | Cambia el shell (ej. `["/bin/bash","-c"]`) |
| `ONBUILD` | Instrucción diferida (evitar en lo posible) |

### Ejemplo: API Python bien armada

```dockerfile
# ---- Etapa 1: build ----
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --user -r requirements.txt

# ---- Etapa 2: runtime (multi-stage) ----
FROM python:3.12-slim AS runtime
RUN groupadd --system app && useradd --system --gid app --uid 10001 app
WORKDIR /app
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Es el patrón [[Dockerfile multi-stage]]: la etapa `builder` tiene compiladores y dependencias de desarrollo; la final solo lo necesario. Resultado: imagen mucho más chica y con menor superficie de ataque (AppSec). Ver también [[Python]] y [[FastAPI]].

### `.dockerignore` (importante para builds rápidos y secretos)

```dockerignore
.git
.github
.venv
__pycache__
*.py[cod]
.env
.env.*
*.log
*.tar
node_modules
tests/
README.md
.DS_Store
```

> Sin `.dockerignore`, el `COPY . .` mete tu `.git` y tu `.env` en la imagen. Equivale a filtrar secretos ([[Gestión de secretos]], [[OWASP Top 10]]).

### `CMD` vs `ENTRYPOINT`

```dockerfile
CMD ["python", "app.py"]                 # se puede reemplazar entero
ENTRYPOINT ["python", "app.py"]          # los args se añaden: docker run img --debug
ENTRYPOINT ["python"]                    # + CMD ["app.py"] → patrón flexible
docker run --entrypoint sh img -c 'echo hola'   # sobrescribe entrypoint
```

### Buenas prácticas rápidas

1. **Imagen base pequeña y fija**: `python:3.12-slim` o `alpine`, nunca `latest`. Mejor por digest.
2. **Ordena por frecuencia de cambio**: `COPY requirements.txt` + `pip install` **antes** que `COPY . .` → el caché se reutiliza.
3. **Un proceso por contenedor** (si necesitas varios, usá [[Docker Compose]]).
4. **No root**: `USER 10001` o `USER app` ([[Usuario root - UID - GID - sudo]]).
5. **Sin secretos en la imagen**: usa `--secret` de BuildKit o secrets de Compose/ECS ([[AWS Secrets Manager]]).
6. **Healthcheck** + `depends_on: condition: service_healthy`.
7. **Escaneá la imagen**: `docker scan img` / `trivy image img` / [[ECR]] scan.
8. **Firma**: `cosign sign` / Docker Content Trust ([[KMS]]).

```bash
# BuildKit + secrets (no se queda en la capa)
DOCKER_BUILDKIT=1 docker build --secret id=npmrc,src=$HOME/.npmrc -t miapp .
# dentro del Dockerfile:
# RUN --mount=type=secret,id=npmrc npm ci --registry=...
```

---

## 6. Docker Compose (multi-contenedor)

Compose ya viene como plugin (`docker compose`, con espacio; el viejo `docker-compose` con guion es el binario legacy).

### `compose.yaml` completo

```yaml
name: mi-stack

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        VERSION: "1.0"
    image: miapp:dev
    container_name: api
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
      REDIS_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./code:/app/code          # bind mount para desarrollo
      - static:/app/static        # named volume
    networks:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD:?falta DB_PASSWORD}
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      retries: 5

  cache:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]
    networks:
      - backend

  proxy:
    image: traefik:v3.0
    command:
      - --providers.docker=true
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - backend

volumes:
  pgdata:
  static:

networks:
  backend:
    driver: bridge
```

> `depends_on` **no espera a que el servicio esté listo** salvo que uses `condition: service_healthy`. Es el error clásico "connection refused" al arrancar. Ver [[PostgreSQL]], [[Redis]], [[Traefik]].

### Comandos Compose

```bash
docker compose config                  # valida y muestra YAML resuelto
docker compose up                      # foreground (ver logs)
docker compose up -d                   # background
docker compose up -d --build           # rebuild imágenes
docker compose up -d --scale api=3     # escalar (sin swarm)
docker compose ps
docker compose logs -f api
docker compose exec db psql -U app
docker compose run --rm api pytest     # comando puntual
docker compose restart api
docker compose stop / start / down
docker compose down -v                 # ⚠️ borra volúmenes (datos)
docker compose pull                    # actualiza imágenes
docker compose images
docker compose top
```

**Perfiles** (servicios opcionales):

```yaml
services:
  mailhog:
    image: mailhog/mailhog
    profiles: ["dev"]
```
```bash
docker compose --profile dev up -d
```

---

## 7. Redes

```bash
docker network ls
docker network create --driver bridge mi-red
docker network create --subnet 172.20.0.0/16 --gateway 172.20.0.1 mi-red
docker network inspect mi-red
docker network connect mi-red contenedor
docker network disconnect mi-red contenedor
docker network rm mi-red
docker network prune
```

| Driver | Uso |
|---|---|
| `bridge` | Default. Red privada con NAT hacia el host. |
| `host` | Comparte la red del host (Linux; más rendimiento, menos aislamiento). |
| `none` | Sin red. |
| `overlay` | Entre hosts (Docker Swarm). |
| `macvlan` | IP propia en la LAN (dispositivos IoT, legado). |

- Dentro de una red custom, los contenedores se resuelven **por nombre de servicio** (DNS interno: `db`, `cache`). En la `bridge` default, **no** (solo por IP).
- `-p 8080:80` publica al host; `--expose 80` solo documenta.
- `docker run --add-host=host.docker.internal:host-gateway ...` para llegar al host desde Linux (en Docker Desktop ya existe `host.docker.internal`).
- Ver [[TCP-IP]], [[DNS]], [[VPC]], [[Load Balancer (ALB-NLB)]].

---

## 8. Volúmenes y persistencia

```bash
docker volume create datos
docker volume ls
docker volume inspect datos
docker volume rm datos

# named volume (recomendado para datos)
docker run -d -v pgdata:/var/lib/postgresql/data postgres:16

# bind mount (desarrollo / archivos del host)
docker run -d -v "$(pwd)/config:/etc/app/config:ro" miapp

# tmpfs (datos volátiles en RAM)
docker run --tmpfs /tmp:rw,noexec,nosuid,size=64m miapp
```

| Tipo | Ventaja | Inconveniente |
|---|---|---|
| **named volume** | Gestionado por Docker, portable, buen rendimiento | Hay que buscarlo con `docker volume ls` |
| **bind mount** | editable desde el host | Depende de rutas y permisos del host (UID/GID) |
| **tmpfs** | rápido, se borra al parar | No persiste; consume RAM |

**Backup de un volumen**:

```bash
docker run --rm -v pgdata:/data -v "$(pwd):/backup" alpine \
  tar czf /backup/pgdata-$(date +%F).tar.gz -C /data .
# Restaurar: tar xzf ... -C /data
```

> Un contenedor se borra, un volumen **no**. Si haces `docker rm -f db` sin volumen, pierdes la base. Ver [[Backups y recovery]], [[AWS Backup]], [[S3 (bucket)]].

---

## 9. Registry: Docker Hub y ECR

```bash
# Docker Hub
docker login
docker tag miapp:1.0 tuition/miapp:1.0
docker push tuusuario/miapp:1.0
docker pull tuusuario/miapp:1.0

# Amazon ECR (necesitas AWS CLI + IAM permisos ecr:*)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
aws ecr create-repository --repository-name miapp --region us-east-1
docker tag miapp:1.0 123456789012.dkr.ecr.us-east-1.amazonaws.com/miapp:1.0
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/miapp:1.0

# Inspeccionar capas sin descargar
docker buildx imagetools inspect tuusuario/miapp:1.0
```

Relaciones: [[Docker Hub]], [[ECR]], [[IAM]], AWS CLI, [[Fargate]], [[ECS]], [[Terraform]].

---

## 10. Seguridad (mindset AppSec)

```dockerfile
FROM gcr.io/distroless/python3-debian12   # o imagen -slim, sin shell
USER 65532:65532                          # no-root
```

```bash
#_flags en runtime
docker run --read-only --cap-drop ALL \
  --security-opt no-new-privileges \
  --security-opt seccomp=seccomp.json \
  --tmpfs /tmp --memory=256m --pids-limit 100 \
  miapp:1.0

# Escanear
trivy image miapp:1.0
docker scan miapp:1.0        # legacy

# Verificar usuario real dentro
docker exec miapp id
docker inspect --format '{{.Config.User}}' miapp
```

Checklist:

- [ ] Imagen fijada por **digest**, no `:latest`.
- [ ] `USER` no-root con UID > 0 ([[Usuario root - UID - GID - sudo]]).
- [ ] `--cap-drop ALL` y solo `--cap-add` lo imprescindible ([[Capabilities - setuid]]).
- [ ] `--read-only` + `tmpfs` para lo que necesite escribir.
- [ ] `no-new-privileges` y seccomp/AppArmor/SELinux ([[seccomp - AppArmor - SELinux]]).
- [ ] Sin secretos en `ENV`, `COPY` ni historial de capas (`docker history`).
- [ ] `docker.sock` **nunca** montado en contenedores no confiables (es root del host).
- [ ] Imagen escaneada en CI ([[GitHub Actions]]) y en registro ([[ECR]]).
- [ ] Minimal: distroless/scratch cuando sea posible (menos CVEs).
- [ ] Logs JSON con rotación ([[Logs estructurados]]).

---

## 11. Troubleshooting (errores reales)

| Síntoma | Causa | Solución |
|---|---|---|
| `Cannot connect to the Docker daemon` | Daemon apagado o permisos | `sudo systemctl start docker`; `newgrp docker`; `docker info` |
| `permission denied while trying to connect to /var/run/docker.sock` | Usuario no está en grupo | `sudo usermod -aG docker $USER` + relogin |
| `Error starting userland proxy: listen tcp 0.0.0.0:8080: bind: address already in use` | Puerto ocupado | `ss -ltnp | grep 8080`; cambiar a `-p 8081:80` |
| El contenedor arranca y se muere | `CMD` termina rápido / error en app | `docker logs contenedor`; `docker inspect --format '{{.State.ExitCode}}'` |
| `OCI runtime exec failed: executable file not found` | Imagen alpine no tiene `bash` | Usar `sh` |
| `OOMKilled` | Pasó el límite de RAM | `docker inspect` → `State.OOMKilled`; subir `--memory` o arreglar leak |
| `connection refused` a `db:5432` | DB aún no lista | `depends_on: condition: service_healthy` + `pg_isready` |
| `no space left on device` | Disco lleno de capas | `docker system df`; `docker system prune -a` (cuidado con volúmenes) |
| `exec format error` | Imagen arm64 en host amd64 (o viceversa) | `docker buildx build --platform linux/amd64 ...` |
| DNS no resuelve en contenedor | `/etc/resolv.conf` o red custom | `docker run --dns 8.8.8.8`; `docker network inspect` |
| Build lento / reinstala todo | `COPY . .` antes de `pip install` | Reordenar Dockerfile; `.dockerignore`; `--no-cache` solo para debug |
| `docker: command not found` en Windows | WSL sin Docker Desktop integrado | Docker Desktop → Settings → WSL Integration |
| Cambios en bind mount no aparecen (Windows) | filesystemdrv | Usar WSL2 en lugar de /mnt/c |
| `Error response from daemon: conflict: container named "x" is already in use` | Nombre duplicado | `docker rm -f x` o cambiar `--name` |

### Comandos forenses

```bash
docker inspect --format '{{json .State}}' web | jq
docker events --since 1h --filter container=web
docker logs --timestamps --tail 200 web 2>&1 | grep -i error
docker diff web                    # qué cambió respecto a la imagen
docker export web | tar tv | head  # filesystem del contenedor
docker debug web                   # Docker Desktop (shell en imagen distinta)
```

---

## 12. Del contenedor a producción (siguiente escalón)

Cuando necesitás **muchos contenedores en varias máquinas**, Docker solo se queda corto:

- [[Docker Compose]] → varios contenedores en **un** host (dev / staging chico).
- [[Kubernetes]] → orquestación, autoscaling, self-healing, multi-host.
- [[Fargate]] / [[ECS]] → contenedores serverless en AWS (sin nodos que administrar).
- [[Traefik]] / [[API Gateway]] → reverse proxy e ingress.
- [[Portainer]] → UI para administrar Docker/K8s.
- [[GitHub Actions]] → build, scan y push en CI/CD.
- [[Terraform]] → infraestructura como código.

> Regla: **Docker resuelve "corre mi app igual en todos lados"**. Kubernetes resuelve *"corre 200 copias, reinicia las que mueren y reparte tráfico"*. No saltes a K8s si Compose te alcanza.

---

## 13. Ejercicios para dominarlo

1. Instalá Docker, corré `hello-world`, `docker info` y explicá cada línea con tus palabras.
2. Escribí un Dockerfile para una app Python con multi-stage, `USER` no-root y healthcheck; compará tamaños con `docker images`.
3. Armá un `compose.yaml` con API + [[PostgreSQL]] + [[Redis]] + [[Traefik]]; hacé que la API espere a que la DB esté *healthy*.
4. Generá un conflicto de puerto a propósito y resolvelo con `ss -ltnp`.
5. Hacé `docker rm -f` de la DB **sin** volumen, perdé los datos, y después repetí con named volume + backup ([[Backups y recovery]]).
6. Escaneá tu imagen con `trivy`, encontrá un CVE y actualizá la base.
7. Subí la imagen a [[Docker Hub]] y a [[ECR]], y verificá el digest con `buildx imagetools inspect`.

---

## 14. Relaciones

[[Docker Compose]] · [[Dockerfile multi-stage]] · [[Docker Hub]] · [[ECR]] · [[Kubernetes]] · [[Fargate]] · [[ECS]] · [[Portainer]] · [[Traefik]] · [[Healthchecks]] · [[cgroups]] · [[Namespaces (PID, mount, network, user, IPC, UTS, cgroup)]] · [[Capabilities - setuid]] · [[seccomp - AppArmor - SELinux]] · [[chroot]] · [[Kernel vs userspace - libc - glibc - musl - ABI]] · [[Usuario root - UID - GID - sudo]] · [[Syscalls (open-read-write-fork-exec-mmap)]] · [[WSL]] · [[Kernel]] · [[PostgreSQL]] · [[Redis]] · [[Logs estructurados]] · [[GitHub Actions]] · [[Terraform]] · [[AWS Secrets Manager]] · [[Gestión de secretos]] · [[OWASP Top 10]] · [[Backups y recovery]] · [[S3 (bucket)]] · [[Husky]]
