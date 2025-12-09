# 📦 PAQUETES EL CLUB - Portal de Clientes

Sistema completo de gestión de paquetería con portal de autogestión para clientes.

## 🚀 Características Principales

- **Portal de Clientes:** Autogestión completa con autenticación OTP
- **Sistema OTP Multi-canal:** Códigos de verificación por SMS y Email
- **Gestión de Preferencias:** Control de notificaciones por parte del cliente
- **Notificaciones Inteligentes:** SMS y Email con respeto a preferencias
- **Dashboard Administrativo:** Gestión completa de paquetes y clientes
- **API RESTful:** Endpoints documentados con OpenAPI/Swagger

## 📁 Estructura del Proyecto

```
CODE/
├── src/                    # Código fuente principal
│   ├── app/
│   │   ├── models/        # Modelos de base de datos
│   │   ├── routes/        # Endpoints de la API
│   │   ├── services/      # Lógica de negocio
│   │   ├── schemas/       # Esquemas Pydantic
│   │   └── utils/         # Utilidades
│   ├── templates/         # Templates HTML (Jinja2)
│   └── static/            # Archivos estáticos (CSS, JS, imágenes)
│
├── alembic/               # Migraciones de base de datos
├── tests/                 # Tests unitarios e integración
├── scripts/               # Scripts de utilidad
│   ├── testing/          # Scripts de pruebas
│   ├── debug/            # Scripts de debugging
│   └── database/         # Scripts de base de datos
│
├── docs/                  # Documentación del proyecto
│   ├── analisis/         # Análisis de problemas
│   ├── implementacion/   # Documentación de implementaciones
│   ├── soluciones/       # Soluciones a problemas
│   ├── pruebas/          # Reportes de pruebas
│   └── referencias/      # Material de referencia
│
├── nginx/                 # Configuración Nginx
├── monitoring/            # Scripts de monitoreo
├── requirements.txt       # Dependencias Python
├── package.json          # Dependencias Node.js (Tailwind)
└── docker-compose.yml    # Configuración Docker (raíz del proyecto)
```

## 🛠️ Tecnologías

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Alembic** - Migraciones de base de datos
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y sesiones

### Frontend
- **Jinja2** - Motor de templates
- **Alpine.js** - Framework JavaScript reactivo
- **Tailwind CSS** - Framework CSS utility-first
- **HTMX** - Interacciones dinámicas

### Servicios Externos
- **Liwa.co** - Envío de SMS
- **SMTP** - Envío de emails

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (para Tailwind)
- Docker y Docker Compose (opcional)

### Instalación Local

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd CODE
```

2. **Crear entorno virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
npm install  # Para Tailwind CSS
```

4. **Configurar variables de entorno:**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones:**
```bash
alembic upgrade head
```

6. **Compilar Tailwind CSS:**
```bash
bash build-tailwind.sh
```

7. **Iniciar servidor:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Instalación con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

## 🧪 Pruebas

### Ejecutar todas las pruebas:
```bash
python3 scripts/testing/test_sistema_completo_final.py
```

### Ejecutar pruebas específicas:
```bash
pytest tests/
```

### Verificar cobertura:
```bash
pytest --cov=src tests/
```

## 📚 Documentación

### Documentación de la API
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Documentación del Proyecto
- **Verificación Completa:** `docs/pruebas/VERIFICACION_CODIGO_COMPLETA.md`
- **Resumen de Pruebas:** `docs/pruebas/RESUMEN_PRUEBAS_SISTEMA.md`
- **Instrucciones de Pruebas:** `docs/pruebas/INSTRUCCIONES_PRUEBAS.md`
- **Documentación de Scripts:** `scripts/README.md`

## 🔐 Seguridad

- Autenticación JWT para usuarios administrativos
- Autenticación OTP para clientes
- Tokens con expiración automática
- Rate limiting en endpoints sensibles
- Validación de datos con Pydantic
- Sanitización de inputs

## 🌐 Despliegue

### Staging
```bash
# Conectar al servidor
ssh ubuntu@staging.jemavi.co

# Actualizar código
git pull origin main

# Reiniciar servicios
docker-compose restart
```

### Producción
Ver `docs/pruebas/CHECKLIST_DESPLIEGUE.md` para el proceso completo.

## 📊 Monitoreo

- **Logs:** `docker-compose logs -f`
- **Métricas:** Disponibles en `/monitoring`
- **Health Check:** `http://localhost:8000/health`

## 🤝 Contribución

1. Crear una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer commit de tus cambios: `git commit -am 'Agregar nueva funcionalidad'`
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Crear un Pull Request

## 📝 Changelog

Ver `docs/pruebas/RESUMEN_CAMBIOS_PRODUCCION.md` para el historial de cambios.

## 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en `/docs`
2. Consultar los logs del servidor
3. Contactar al equipo de desarrollo

## 📄 Licencia

Propietario: PAQUETES EL CLUB  
Todos los derechos reservados.

## 👥 Equipo

- **Desarrollo:** Equipo de Desarrollo PAQUETES EL CLUB
- **Versión:** 1.0.0
- **Última actualización:** 2025-12-09
