# 🏗️ ARQUITECTURA DE BASE DE DATOS - PAQUETEX

## 🎯 PRINCIPIO FUNDAMENTAL

**NO EXISTE BASE DE DATOS LOCAL**

Todas las instancias (desarrollo local, staging, producción) se conectan a **AWS RDS**.

---

## 📊 ARQUITECTURA ACTUAL

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS RDS (us-east-1)                         │
│                 ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  📦 paqueteria_v4 (PRODUCCIÓN)                             │    │
│  │  ├─ Datos: Reales de clientes                              │    │
│  │  ├─ Acceso: Solo servidor producción (puerto 80)           │    │
│  │  └─ Modificación: Solo desde producción                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  🧪 paqueteria_staging (STAGING/DESARROLLO)                │    │
│  │  ├─ Datos: Pruebas y desarrollo                            │    │
│  │  ├─ Acceso: Servidor staging + Desarrollo local            │    │
│  │  └─ Modificación: Desde staging y local                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                    ↑                              ↑
                    │                              │
        ┌───────────┴──────────┐    ┌────────────┴─────────────┐
        │                      │    │                           │
┌───────┴────────┐   ┌─────────┴────────┐   ┌──────────────────┴──────┐
│  PRODUCCIÓN    │   │  SERVIDOR        │   │  DESARROLLO LOCAL       │
│  (Puerto 80)   │   │  STAGING         │   │  (Puerto 8000/8001)     │
│                │   │  (Puerto 8001)   │   │                         │
│  .env.prod     │   │  .env.staging    │   │  CODE/.env              │
│  ↓             │   │  ↓               │   │  ↓                      │
│  paqueteria_v4 │   │  paqueteria_     │   │  paqueteria_staging     │
│                │   │  staging         │   │                         │
└────────────────┘   └──────────────────┘   └─────────────────────────┘
```

---

## 🔧 CONFIGURACIÓN POR AMBIENTE

### **1. Desarrollo Local (Tu Máquina)**

**Archivo:** `CODE/.env`

```bash
# Conecta a paqueteria_staging en AWS RDS
DATABASE_URL=postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_staging
ENVIRONMENT=development
DEBUG=True
PORT=8000
S3_PREFIX=staging/
```

**Características:**
- ✅ Usa `paqueteria_staging` en AWS RDS
- ✅ NO hay base de datos local
- ✅ Comparte BD con servidor staging
- ✅ Datos de prueba, no afecta producción
- ✅ Prefijo S3: `staging/`

**Cómo levantar:**
```bash
cd CODE
uvicorn src.main:app --reload --port 8000
# O con Docker:
docker-compose -f docker-compose.dev.yml up
```

---

### **2. Servidor Staging**

**Archivo:** `CODE/.env.staging`

```bash
# Conecta a paqueteria_staging en AWS RDS
DATABASE_URL=postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_staging
ENVIRONMENT=staging
DEBUG=True
PORT=8000  # Interno del contenedor
S3_PREFIX=staging/
```

**Características:**
- ✅ Usa `paqueteria_staging` en AWS RDS
- ✅ Mismo BD que desarrollo local
- ✅ Puerto expuesto: 8001
- ✅ Datos de prueba compartidos con local
- ✅ Prefijo S3: `staging/`

**Cómo levantar:**
```bash
docker-compose -f docker-compose.staging.yml up -d
```

---

### **3. Producción**

**Archivo:** `.env.production`

```bash
# Conecta a paqueteria_v4 en AWS RDS
DATABASE_URL=postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_v4
ENVIRONMENT=production
DEBUG=False
PORT=8000  # Interno del contenedor
S3_PREFIX=  # Sin prefijo (raíz del bucket)
```

**Características:**
- ✅ Usa `paqueteria_v4` en AWS RDS
- ✅ BD separada de staging/desarrollo
- ✅ Puerto expuesto: 80
- ✅ Datos reales de clientes
- ✅ Sin prefijo S3 (raíz del bucket)

**Cómo levantar:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 FLUJO DE TRABAJO

### **Desarrollo Local:**

```bash
# 1. Clonar repositorio
git clone <repo>
cd PAQUETEX

# 2. Verificar CODE/.env (ya configurado)
cat CODE/.env | grep DATABASE_URL
# Debe mostrar: ...paqueteria_staging

# 3. Instalar dependencias
cd CODE
pip install -r requirements.txt

# 4. Levantar servidor
uvicorn src.main:app --reload --port 8000

# 5. Acceder
# http://localhost:8000
```

**Resultado:** Conectado a `paqueteria_staging` en AWS RDS

---

### **Deploy a Staging:**

```bash
# 1. En servidor staging
git pull origin main

# 2. Levantar contenedor
docker-compose -f docker-compose.staging.yml up -d

# 3. Verificar
docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
# Debe mostrar: ...paqueteria_staging

# 4. Acceder
# http://servidor-staging:8001
```

**Resultado:** Conectado a `paqueteria_staging` en AWS RDS

---

### **Deploy a Producción:**

```bash
# 1. En servidor producción
git pull origin main

# 2. Levantar contenedor
docker-compose -f docker-compose.prod.yml up -d

# 3. Verificar
docker-compose -f docker-compose.prod.yml exec app env | grep DATABASE_URL
# Debe mostrar: ...paqueteria_v4

# 4. Acceder
# http://servidor-produccion
```

**Resultado:** Conectado a `paqueteria_v4` en AWS RDS

---

## 🔒 SEGURIDAD Y AISLAMIENTO

### **Separación de Datos:**

| Ambiente | Base de Datos | Datos | Acceso |
|----------|---------------|-------|--------|
| **Desarrollo Local** | `paqueteria_staging` | Pruebas | Lectura/Escritura |
| **Servidor Staging** | `paqueteria_staging` | Pruebas | Lectura/Escritura |
| **Producción** | `paqueteria_v4` | Reales | Lectura/Escritura |

### **Garantías:**

✅ **Desarrollo y Staging comparten BD:**
- Puedes probar localmente
- Los cambios se ven en staging
- Facilita el desarrollo colaborativo

✅ **Producción está aislada:**
- Datos reales protegidos
- No se ve afectada por desarrollo
- BD separada físicamente

✅ **No hay BD local:**
- No hay problemas de sincronización
- No hay datos desactualizados
- No hay consumo de recursos locales

---

## 📦 ALMACENAMIENTO S3

### **Prefijos por Ambiente:**

```
elclub-paqueteria (bucket)
├── staging/                    # Desarrollo + Staging
│   ├── provider-pdfs/
│   ├── dian-pdfs/
│   └── uploads/
│
└── (raíz)                      # Producción
    ├── provider-pdfs/
    ├── dian-pdfs/
    └── uploads/
```

**Configuración:**

| Ambiente | S3_PREFIX | Archivos |
|----------|-----------|----------|
| Desarrollo Local | `staging/` | Pruebas |
| Servidor Staging | `staging/` | Pruebas |
| Producción | `` (vacío) | Reales |

---

## 🛠️ HERRAMIENTAS DE GESTIÓN

### **Verificar Conexión:**

```bash
# Desde cualquier ambiente
python3 -c "
from CODE.src.app.database import check_db_connection, get_db_info
print('Conexión:', '✅' if check_db_connection() else '❌')
print('Info:', get_db_info())
"
```

### **Ver Estadísticas:**

```bash
# Desde cualquier ambiente
python3 -c "
from CODE.src.app.database import get_db_stats
print(get_db_stats())
"
```

### **Listar Bases de Datos:**

```bash
# Usando script
python3 scripts/staging/list_databases.py
```

---

## 🚨 IMPORTANTE: NO CREAR BD LOCAL

### **❌ NO HACER:**

```bash
# NO instalar PostgreSQL localmente
sudo apt install postgresql  # ❌ NO

# NO crear contenedor de PostgreSQL
docker run -d postgres  # ❌ NO

# NO usar SQLite
DATABASE_URL=sqlite:///local.db  # ❌ NO
```

### **✅ HACER:**

```bash
# Usar CODE/.env con DATABASE_URL de AWS RDS
DATABASE_URL=postgresql://...@...amazonaws.com:5432/paqueteria_staging  # ✅ SÍ

# Verificar que apunta a AWS
echo $DATABASE_URL | grep amazonaws  # ✅ SÍ
```

---

## 📊 RESUMEN DE CONEXIONES

### **Todas las Instancias → AWS RDS:**

```
┌─────────────────┐
│ Desarrollo      │
│ Local           │──┐
└─────────────────┘  │
                     │
┌─────────────────┐  │    ┌──────────────────────┐
│ Servidor        │  ├───→│  AWS RDS             │
│ Staging         │──┘    │  paqueteria_staging  │
└─────────────────┘       └──────────────────────┘

┌─────────────────┐       ┌──────────────────────┐
│ Servidor        │──────→│  AWS RDS             │
│ Producción      │       │  paqueteria_v4       │
└─────────────────┘       └──────────────────────┘
```

### **Ventajas:**

✅ **Centralización:** Todos los datos en un solo lugar  
✅ **Consistencia:** No hay desincronización  
✅ **Backup:** AWS RDS maneja backups automáticos  
✅ **Escalabilidad:** AWS RDS escala según necesidad  
✅ **Seguridad:** AWS RDS maneja seguridad y encriptación  
✅ **Simplicidad:** No hay que mantener BD local  

---

## 🔍 VERIFICACIÓN RÁPIDA

### **¿Estoy conectado a la BD correcta?**

```bash
# Ver DATABASE_URL actual
echo $DATABASE_URL

# O desde Python
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('CODE/.env')
url = os.getenv('DATABASE_URL')
if 'paqueteria_staging' in url:
    print('✅ Conectado a STAGING')
elif 'paqueteria_v4' in url:
    print('✅ Conectado a PRODUCCIÓN')
else:
    print('❌ Configuración incorrecta')
print(f'URL: {url}')
"
```

---

**Fecha:** 2026-01-29  
**Versión:** 1.0.0  
**Principio:** NO BASE DE DATOS LOCAL - TODO EN AWS RDS
