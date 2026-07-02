# DECISIONS.md

## 1. Arquitectura

### Backend - dominio aislado de HTTP y de la base

Capas, de adentro hacia afuera:

```
domain/    reglas puras: máquina de estados, invariantes, overdue, entidad
services/  orquestación: transacciones, optimistic lock, mapeo row↔dominio
data/      SQLAlchemy: modelos, repositorio, sesión, migraciones
routes/    HTTP fino: valida request (Pydantic), llama al service, mapea a HTTP
schemas/   contratos Pydantic + enmascarado en la respuesta
```

El dominio no importa FastAPI, Pydantic ni SQLAlchemy: puro y testeable sin HTTP ni base.
El **service** es el único que toca dominio y persistencia a la vez; el error de dominio →
HTTP se mapea una sola vez, en un handler central (`main.py`).

**Alternativas descartadas:**

- *Entidad rica / Active Record.* Se auto-persiste y lleva las reglas adentro; más difícil
  de testear y razonar. Preferí entidad anémica + funciones puras.
- *Repository abstracto + inyección.* Over-engineering: hay una sola base. Repo concreto
  sobre `Session`; la costura ya está si mañana hiciera falta.

### Frontend - Next.js App Router, sin duplicar el dominio

- **Mutaciones solo vía Server Actions** (`lib/actions/obligations.ts`), nunca
  cliente → API directo: la URL del backend no llega al browser y la revalidación de
  cache vive en un solo lugar.

- **El front no re-deriva reglas**: `overdue`, `allowed_transitions` y `can_submit`
  vienen calculados del backend y la UI solo pinta lo que el API permite. Si se fuerza
  la transición igual, el dominio la rechaza con `422`.

- **i18n es/en** (`lib/i18n/`) con locale por cookie.

---

## 2. Contrato de la API

API REST sobre `/obligations` . 

Dos decisiones a aclarar:

**Decisión: endpoint de transición separado del update genérico.** `PATCH` edita
campos de datos; `POST /transition` es el único camino para cambiar de estado y es el
único que corre `validate_transition` + `assert_document_gate` + optimistic lock. Así
no existe ninguna vía por la que un cambio de estado evite las reglas.

**Modelo de error consistente.** Todos los errores de dominio salen con el mismo
cuerpo estructurado y el código HTTP correcto, armado en un único lugar (`main.py`):

```python
def _error_body(error: DomainError) -> dict:
    return {"error": {"type": type(error).__name__, "message": str(error)}}
```

| Error de dominio | HTTP | Cuándo |
|---|---|---|
| `NotFound` | `404` | la obligación (o el documento) no existe |
| `InvalidTransition` | `409` | la transición no está en el mapa de estados |
| `VersionConflict` | `409` | otro request modificó la fila (optimistic lock) |
| `DocumentRequired` | `422` | mover a `submitted` sin documento requerido |
| validación de request | `422` | Pydantic (campos faltantes, longitudes, enums) |

---

## 3. 

### ¿Dónde vive `overdue`?

En el **dominio**: `domain/rules.is_overdue(obligation, today)`. Regla:
`due_date < today AND status ∉ {submitted, done}`.

- **Es derivado, nunca persistido.** No hay columna `overdue` ni variante en el enum
  `Status`; se computa en cada lectura en el service (`_view`) y se expone como
  `overdue: bool` en la respuesta. El front solo lo renderiza.
- **El reloj se inyecta como dependencia**: `is_overdue` recibe `today` por parámetro en
  vez de leer `date.today()` adentro. Es una función pura y determinista - los tests fijan
  la fecha que quieren y no dependen del entorno de ejecución.
- **Por qué derivado y no un flag persistido por un job:** overdue cambia por el paso del
  tiempo, sin ningún evento que lo dispare, así que un flag persistido está desactualizado
  entre corridas del job por definición. Además contaminaría la máquina de estados con un
  pseudo-estado sin transiciones: `overdue` es una proyección sobre el estado, no un estado.

### Concurrencia - optimistic locking por versión

**Solución implementada:** cada obligación lleva un `version`; el cliente lo recibe al
leer y lo devuelve al pedir el cambio de estado. El backend acepta el cambio **solo si la
versión sigue siendo la que el cliente vio**; si alguien modificó la fila en el medio,
responde `409` y el front ofrece recargar y reintentar.

El chequeo y la escritura pasan en **un solo paso atómico**:

```sql
UPDATE ... SET status=?, version=version+1 WHERE id=? AND version=?
```

Si dos requests compiten con la misma versión, la base deja pasar a uno solo; el otro no
matchea ninguna fila y recibe `409`. Nunca se pierde una escritura ni queda guardada una
transición inválida.

**Descartadas:** lock pesimista (hace esperar a todos por choques que son raros) y sin
control de concurrencia (la última escritura pisa a la anterior en silencio).

*Nota honesta:* el optimistic lock se aplica a `change_state`, que es el camino
crítico. `PATCH` (edición de campos de datos) hoy es last-write-wins; fue una decisión
consciente de scope - extender `version` al PATCH es trivial (mismo patrón) y lo haría
si la edición concurrente de campos fuera un caso real.

### Dato sensible - `companyTaxId`

- **Se guarda completo** en `company_tax_id` (se necesita el valor real).
- **Se devuelve enmascarado en TODAS las lecturas** (`mask_tax_id` → `••••6789`), en el
  schema (`_base_fields`), único armador de respuestas. Ninguna ruta devuelve el valor completo.
- **Fuera de logs**: los errores de dominio no incluyen el tax id y no hay logging que lo toque.

**Por qué en el schema y no en el dominio:** enmascarar es presentación; el dominio necesita
el valor real para validar. Regla: el valor completo lo usa el dominio, el borde lo enmascara,
y nunca sale por una respuesta ni un log.

---

## 4. Trazabilidad (audit trail)

Cada cambio de estado se registra en `audit_entries` con `from_status`, `to_status` y
`timestamp` (UTC). La creación se audita como `null → pending`. El detalle
(`GET /obligations/{id}`) expone el historial ordenado por fecha. El audit se escribe en
la **misma transacción** que el cambio de estado, así no puede haber un cambio sin su
registro (ni un registro sin cambio).

---

## 5. Persistencia y storage

- **PostgreSQL** como store primario vía SQLAlchemy; `docker-compose.yml` levanta db +
  backend + frontend. SQLite queda como fallback local aceptable (mismo código, otro
  `DATABASE_URL`). Migraciones con Alembic, corridas en el `lifespan` del arranque.
- **Documentos**: subida a **Supabase Storage** (`app/integrations/storage.py`), con URLs
  firmadas temporales para descarga. La metadata (nombre, tipo, tamaño, path) vive en la
  tabla `documents`; el binario, en el bucket. El service solo conoce la interfaz
  `DocumentStorage`, sustituible por un stub en tests.

### Decisión: la subida se proxea por el backend (no presigned upload URLs)

El archivo pasa **por el backend** (cliente → Server Action → backend → Supabase): el
backend lo sube al bucket y guarda su metadata en un solo paso - o queda todo, o nada.

La alternativa era que el navegador subiera directo a Supabase. La descarté porque rompe
ese "todo o nada" (pueden quedar archivos sueltos si algo falla) y porque el backend no
llegaría a ver el archivo, que es justo donde se valida. Tiene sentido recién con archivos
grandes o mucho volumen; para documentos de pocos MB no se justifica, y el cambio es
reversible si hiciera falta.

**Validación en el backend.** Antes de subir nada, el backend rechaza archivos vacíos,
demasiado grandes (`MAX_UPLOAD_MB`, default 10) o de un tipo no permitido → `422`. El
chequeo en el cliente es solo comodidad; la fuente de verdad es el backend.

---

## 6. Testing (comportamiento, en ambas capas)

- **Backend** (`pytest`, 49 tests): máquina de estados (todas las transiciones válidas e
  inválidas), invariante doc-gated, derivación de overdue, optimistic lock/concurrencia a
  nivel service, y la API end-to-end (incluye que el tax id sale enmascarado y que una
  transición inválida devuelve `409` sin persistir).
- **Frontend** (`vitest`, 9 tests): formato de fechas/estados, render de la tabla con
  resalte de vencidas, los controles de transición (que solo se ofrecen las permitidas y
  que *submitted* se bloquea sin documento) y un flujo del formulario.

Los tests de dominio corren **sin base de datos** - es la prueba de que el dominio está
aislado.

---

## 7. Uso de IA 

- Configuré el entorno con **hooks y skills de Claude Code** para automatizar convenciones
  y chequeos del repo, algunos:
  - **`guard-edit.py`** (hook PreToolUse sobre ediciones) - corre antes de cada edición
    de archivos y la bloquea si el código nuevo rompe un no-negociable del dominio:
    loguear `companyTaxId`, hardcodear un secreto, usar `any` en TypeScript o guardar
    `overdue` como status.
  - **`format-edit.py`** (hook PostToolUse sobre ediciones) - formatea automáticamente cada
    archivo editado con `ruff format` (Python) o `eslint --fix` (TS/JS), sin bloquear nunca.
  - **`git-conventions`** (skill) - aplica las convenciones de git: branches
    `tipo/issue-id/descripcion` desde `develop` y commits en Conventional Commits en inglés,
    proponiendo siempre antes de ejecutar.
- **La rechacé - over-engineering:** sugerencias de interfaces de repositorio abstractas,
  capa de eventos y un job de "marcar vencidas". Innecesario para el scope y contrario a
  la decisión de mantener `overdue` derivado.

---

## 8. Qué dejé afuera a propósito (y qué haría con más tiempo)

- **Auth**: no hay autenticación/usuarios. `owner` es texto libre. Con más tiempo: auth
  simple + scoping por empresa/usuario.
- **Paginación y búsqueda** en el listado. Lo haría en el **backend** (`limit`/`offset` en
  `GET /obligations`), como el filtrado y el orden que ya viven ahí.
- **Recordatorios / notificaciones** de próximas a vencer: el KPI *upcoming* existe (ventana
  de 30 días), pero no hay envío de recordatorios. Lo haría con un job programado en el
  **backend** reusando esa misma derivación; en el front no puede vivir porque solo corre
  con la app abierta.
- **Logs estructurados y observabilidad**: hay manejo de errores consistente, no logging
  estructurado.
- **CI**: los tests corren local en ambas capas; no configuré pipeline.

