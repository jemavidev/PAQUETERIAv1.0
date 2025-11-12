# Documentación de Servicios de la Aplicación

## 📋 Descripción General

Este documento describe todos los **servicios** (clases de lógica de negocio) que forman parte de la aplicación **PAQUETERÍA v1.0**. Los servicios están ubicados en `CODE/src/app/services/` y proporcionan la funcionalidad principal del sistema.

---

## 🏗️ Arquitectura de Servicios

Todos los servicios heredan de `BaseService`, que proporciona operaciones CRUD básicas. Cada servicio se especializa en un dominio específico del negocio.

---

## 📦 Servicios Principales

### 1. **PackageService** - Gestión de Paquetes

**Archivo**: `app/services/package_service.py`  
**Modelo**: `Package`

#### ¿Qué hace?
Gestiona todo el ciclo de vida de los paquetes:
- **Creación de paquetes**: Con generación automática de tracking number único
- **Búsqueda y filtrado**: Por estado, cliente, tracking number, fechas
- **Actualización de estados**: Transiciones de estado (recibido → en tránsito → entregado, etc.)
- **Historial**: Registro de todos los cambios de estado
- **Anuncios**: Gestión de anuncios de paquetes a clientes
- **Cálculo de tarifas**: Aplicación automática de tarifas según peso y tipo
- **Estadísticas**: Conteo de paquetes por estado, cliente, período

#### Funcionalidades clave:
- Generación automática de tracking numbers únicos
- Búsqueda o creación automática de clientes
- Validación de transiciones de estado
- Registro de historial completo
- Integración con servicios de notificación (SMS, Email)

#### Métodos principales:
- `create_package()`: Crear nuevo paquete
- `update_package_status()`: Cambiar estado de paquete
- `search_packages()`: Búsqueda avanzada
- `get_package_by_tracking()`: Buscar por tracking number
- `get_package_history()`: Obtener historial completo

---

### 2. **CustomerService** - Gestión de Clientes

**Archivo**: `app/services/customer_service.py`  
**Modelo**: `Customer`

#### ¿Qué hace?
Gestiona la información de clientes:
- **CRUD completo**: Crear, leer, actualizar, eliminar clientes
- **Validación de duplicados**: Por teléfono, email o documento
- **Búsqueda avanzada**: Por nombre, teléfono, email, documento
- **Estadísticas**: Conteo de paquetes por cliente, totales
- **Exportación**: Generación de CSV con datos de clientes
- **Actualización masiva**: Operaciones en lote

#### Funcionalidades clave:
- Prevención de duplicados automática
- Búsqueda flexible (parcial, exacta)
- Estadísticas de actividad por cliente
- Historial de creación y actualización

#### Métodos principales:
- `create_customer()`: Crear nuevo cliente
- `search_customers()`: Búsqueda con múltiples criterios
- `get_customer_stats()`: Estadísticas del cliente
- `export_customers_csv()`: Exportar a CSV
- `bulk_update_customers()`: Actualización masiva

---

### 3. **EmailService** - Envío de Emails

**Archivo**: `app/services/email_service.py`  
**Modelo**: `Notification`

#### ¿Qué hace?
Gestiona el envío de emails mediante SMTP:
- **Envío de emails**: Individual y masivo
- **Templates**: Emails predefinidos con Jinja2 (notificaciones de paquetes, recordatorios)
- **Notificaciones automáticas**: Por eventos de paquetes (recibido, en tránsito, entregado)
- **Registro**: Guarda todas las notificaciones en la base de datos
- **Validación SMTP**: Prueba de conexión al servidor SMTP
- **Manejo de errores**: Reintentos y logging de fallos

#### Funcionalidades clave:
- Templates HTML y texto plano
- Personalización con variables (nombre, tracking, estado, etc.)
- Envío asíncrono vía Celery
- Registro de estado (pendiente, enviado, fallido)
- Soporte para múltiples destinatarios (CC, BCC)

#### Métodos principales:
- `send_email()`: Enviar email individual
- `send_bulk_emails()`: Envío masivo
- `send_email_by_event()`: Enviar por evento de paquete
- `test_smtp_connection()`: Validar configuración SMTP
- `get_email_templates()`: Listar templates disponibles

#### Templates disponibles:
- Notificación de paquete recibido
- Notificación de paquete en tránsito
- Notificación de paquete entregado
- Recordatorios de paquetes pendientes
- Notificaciones administrativas

---

### 4. **SMSService** - Envío de SMS

**Archivo**: `app/services/sms_service.py`  
**Modelo**: `Notification`, `SMSMessageTemplate`, `SMSConfiguration`

#### ¿Qué hace?
Gestiona el envío de SMS mediante integración con **Liwa.co**:
- **Envío de SMS**: Individual y masivo
- **Templates**: Mensajes predefinidos con variables
- **Notificaciones automáticas**: Por eventos de paquetes
- **Configuración**: Gestión de credenciales y configuración de Liwa.co
- **Registro**: Guarda todas las notificaciones SMS en la base de datos
- **Validación**: Prueba de conexión con la API de Liwa.co

#### Funcionalidades clave:
- Integración con API REST de Liwa.co
- Templates personalizables con variables
- Envío asíncrono vía Celery
- Manejo de errores y reintentos
- Estadísticas de envíos (exitosos, fallidos)

#### Métodos principales:
- `send_sms()`: Enviar SMS individual
- `send_bulk_sms()`: Envío masivo
- `send_sms_by_event()`: Enviar por evento de paquete
- `get_sms_config()`: Obtener configuración activa
- `test_sms_connection()`: Validar conexión con Liwa.co
- `get_sms_templates()`: Listar templates disponibles

#### Templates disponibles:
- SMS de paquete recibido
- SMS de paquete en tránsito
- SMS de paquete entregado
- Recordatorios de paquetes pendientes

---

### 5. **NotificationService** - Gestión de Notificaciones

**Archivo**: `app/services/notification_service.py`  
**Modelo**: `Notification`

#### ¿Qué hace?
Gestiona el sistema centralizado de notificaciones:
- **Creación de notificaciones**: Registro de todas las notificaciones (email, SMS, in-app)
- **Estados**: Pendiente, enviado, fallido, leído
- **Prioridades**: Baja, media, alta, urgente
- **Eventos**: Tipos de eventos que generan notificaciones
- **Búsqueda y filtrado**: Por usuario, tipo, estado, prioridad
- **Marcado como leído**: Gestión de notificaciones no leídas

#### Funcionalidades clave:
- Sistema unificado para todos los tipos de notificación
- Historial completo de notificaciones
- Contadores de notificaciones no leídas
- Filtrado avanzado

#### Métodos principales:
- `create_notification()`: Crear nueva notificación
- `send_notification()`: Marcar como enviada
- `get_user_notifications()`: Obtener notificaciones de usuario
- `mark_as_read()`: Marcar como leída
- `get_unread_count()`: Contar no leídas

---

### 6. **S3Service** - Gestión de Archivos en AWS S3

**Archivo**: `app/services/s3_service.py`

#### ¿Qué hace?
Gestiona el almacenamiento de archivos en **AWS S3**:
- **Subida de archivos**: Imágenes, documentos, PDFs
- **Descarga de archivos**: Obtener archivos desde S3
- **Eliminación**: Borrar archivos del bucket
- **URLs firmadas**: Generar URLs temporales para acceso
- **Validación**: Verificar existencia de archivos
- **Organización**: Estructura de carpetas en S3

#### Funcionalidades clave:
- Integración con boto3 (AWS SDK)
- Manejo de diferentes tipos de contenido
- URLs públicas y privadas
- Validación de credenciales AWS
- Manejo de errores de S3

#### Métodos principales:
- `upload_file()`: Subir archivo a S3
- `download_file()`: Descargar archivo desde S3
- `delete_file()`: Eliminar archivo de S3
- `get_file_url()`: Obtener URL del archivo
- `file_exists()`: Verificar existencia
- `list_files()`: Listar archivos en carpeta

#### Estructura en S3:
```
paquetes-recibidos-imagenes/
  ├── packages/
  │   ├── {package_id}/
  │   │   ├── images/
  │   │   └── documents/
  ├── customers/
  └── temp/
```

---

### 7. **FileUploadService** - Gestión de Subida de Archivos

**Archivo**: `app/services/file_upload_service.py`  
**Modelo**: `FileUpload`

#### ¿Qué hace?
Gestiona el registro y procesamiento de archivos subidos:
- **Registro de archivos**: Guarda metadatos en base de datos
- **Integración con S3**: Sube archivos a S3 automáticamente
- **Tipos de archivo**: Imágenes, documentos, recibos, etc.
- **Asociación**: Vincula archivos con paquetes, clientes, etc.
- **Validación**: Verifica tipo, tamaño, formato

#### Funcionalidades clave:
- Registro en BD + almacenamiento en S3
- Soporte para múltiples tipos de archivo
- Validación de tamaño y formato
- Generación de thumbnails (si se configura)

#### Métodos principales:
- `create_file_upload()`: Registrar archivo subido
- `get_files_by_package()`: Obtener archivos de un paquete
- `get_files_by_type()`: Filtrar por tipo
- `delete_file_upload()`: Eliminar registro y archivo

---

### 8. **FileManagementService** - Gestión de Archivos Locales

**Archivo**: `app/services/file_management_service.py`

#### ¿Qué hace?
Gestiona archivos almacenados localmente (alternativa a S3):
- **Almacenamiento local**: Guarda archivos en el sistema de archivos
- **Organización**: Estructura de carpetas local
- **Limpieza**: Eliminación de archivos temporales
- **Validación**: Verificación de integridad

#### Funcionalidades clave:
- Almacenamiento en `uploads/`
- Organización por tipo y fecha
- Limpieza automática de temporales

---

### 9. **RateService** - Gestión de Tarifas

**Archivo**: `app/services/rate_service.py`  
**Modelo**: `Rate`

#### ¿Qué hace?
Gestiona las tarifas de envío de paquetes:
- **CRUD de tarifas**: Crear, actualizar, eliminar tarifas
- **Cálculo automático**: Calcula costo según peso y tipo de paquete
- **Tarifas por tipo**: Diferentes tarifas para documentos, paquetes, etc.
- **Rangos de peso**: Tarifas escalonadas por peso
- **Validación**: Verifica que las tarifas sean coherentes

#### Funcionalidades clave:
- Cálculo automático de costos
- Tarifas por rangos de peso
- Historial de cambios de tarifas
- Tarifas por defecto

#### Métodos principales:
- `create_rate()`: Crear nueva tarifa
- `calculate_rate()`: Calcular costo para un paquete
- `get_active_rates()`: Obtener tarifas activas
- `update_rate()`: Actualizar tarifa existente

---

### 10. **ReportService** - Generación de Reportes

**Archivo**: `app/services/report_service.py`

#### ¿Qué hace?
Genera reportes en diferentes formatos:
- **Reportes de paquetes**: Por estado, período, cliente
- **Reportes financieros**: Ingresos, costos, ganancias
- **Reportes de clientes**: Actividad, estadísticas
- **Exportación**: PDF, Excel, CSV
- **Generación asíncrona**: Vía Celery para reportes grandes

#### Funcionalidades clave:
- Múltiples formatos (PDF, Excel, CSV)
- Filtros avanzados
- Generación asíncrona
- Almacenamiento temporal

#### Métodos principales:
- `generate_report()`: Generar reporte
- `generate_package_report()`: Reporte de paquetes
- `generate_financial_report()`: Reporte financiero
- `export_to_pdf()`: Exportar a PDF
- `export_to_excel()`: Exportar a Excel

---

### 11. **UserService** - Gestión de Usuarios

**Archivo**: `app/services/user_service.py`  
**Modelo**: `User`

#### ¿Qué hace?
Gestiona usuarios del sistema:
- **CRUD de usuarios**: Crear, actualizar, eliminar usuarios
- **Autenticación**: Login, logout, verificación de credenciales
- **Roles y permisos**: Gestión de roles (admin, operador, etc.)
- **Cambio de contraseña**: Actualización segura de contraseñas
- **Búsqueda**: Filtrar usuarios por rol, estado, etc.

#### Funcionalidades clave:
- Hash seguro de contraseñas (bcrypt)
- Gestión de roles y permisos
- Validación de credenciales
- Historial de actividad

---

### 12. **AdminService** - Funciones Administrativas

**Archivo**: `app/services/admin_service.py`

#### ¿Qué hace?
Proporciona funciones administrativas del sistema:
- **Estadísticas generales**: Dashboard con métricas
- **Limpieza de datos**: Eliminación de datos antiguos
- **Configuración**: Gestión de configuraciones del sistema
- **Auditoría**: Logs de acciones administrativas
- **Backup**: Gestión de backups

#### Funcionalidades clave:
- Dashboard con KPIs
- Herramientas de mantenimiento
- Configuración centralizada
- Logs de auditoría

---

### 13. **AnnouncementsService** - Gestión de Anuncios

**Archivo**: `app/services/announcements_service.py`  
**Modelo**: `PackageAnnouncement`

#### ¿Qué hace?
Gestiona los anuncios de paquetes a clientes:
- **Creación de anuncios**: Notificar a clientes sobre paquetes recibidos
- **Envío automático**: SMS y email cuando se crea anuncio
- **Historial**: Registro de todos los anuncios enviados
- **Estados**: Pendiente, enviado, leído

#### Funcionalidades clave:
- Integración con SMS y Email
- Notificación automática
- Historial completo

---

### 14. **PackageEventService** - Gestión de Eventos de Paquetes

**Archivo**: `app/services/package_event_service.py`  
**Modelo**: `PackageEvent`

#### ¿Qué hace?
Registra eventos que ocurren en el ciclo de vida de los paquetes:
- **Registro de eventos**: Cada cambio de estado genera un evento
- **Historial completo**: Timeline de eventos de un paquete
- **Notificaciones**: Dispara notificaciones automáticas
- **Auditoría**: Registro de quién hizo qué y cuándo

#### Funcionalidades clave:
- Timeline completo de eventos
- Integración con notificaciones
- Auditoría detallada

---

### 15. **PackageStateService** - Gestión de Estados de Paquetes

**Archivo**: `app/services/package_state_service.py`

#### ¿Qué hace?
Gestiona las transiciones de estado de los paquetes:
- **Validación de transiciones**: Verifica que los cambios de estado sean válidos
- **Estados permitidos**: Define qué estados pueden seguir a cada estado
- **Automatización**: Cambios automáticos de estado según reglas

#### Funcionalidades clave:
- Máquina de estados
- Validación de transiciones
- Reglas de negocio

---

### 16. **HeaderNotificationService** - Notificaciones en Header

**Archivo**: `app/services/header_notification_service.py`

#### ¿Qué hace?
Gestiona las notificaciones que aparecen en el header de la aplicación:
- **Notificaciones en tiempo real**: Contador de notificaciones no leídas
- **Badges**: Indicadores visuales
- **Actualización automática**: Sin recargar página

#### Funcionalidades clave:
- API para notificaciones del header
- Contadores en tiempo real
- Filtrado por tipo y prioridad

---

## 🔄 Integración entre Servicios

Los servicios trabajan juntos para proporcionar funcionalidad completa:

1. **PackageService** → **CustomerService**: Busca o crea clientes al crear paquetes
2. **PackageService** → **RateService**: Calcula tarifas automáticamente
3. **PackageService** → **NotificationService**: Crea notificaciones al cambiar estado
4. **NotificationService** → **EmailService** / **SMSService**: Envía notificaciones
5. **FileUploadService** → **S3Service**: Sube archivos a S3
6. **PackageEventService** → **NotificationService**: Dispara notificaciones por eventos

---

## 📊 Tareas Asíncronas (Celery)

Varios servicios tienen tareas asíncronas ejecutadas por Celery:

- **EmailService**: `send_bulk_emails` (envío masivo)
- **SMSService**: `send_bulk_sms` (envío masivo)
- **ReportService**: `generate_report` (reportes grandes)
- **FileManagementService**: `process_file_upload` (procesamiento de archivos)
- **AdminService**: `cleanup_old_data` (limpieza de datos)

Ver `app/tasks.py` para todas las tareas definidas.

---

## 🗄️ Modelos de Base de Datos

Cada servicio trabaja con uno o más modelos:

- `Package` → PackageService
- `Customer` → CustomerService
- `Notification` → EmailService, SMSService, NotificationService
- `User` → UserService
- `Rate` → RateService
- `FileUpload` → FileUploadService
- `PackageEvent` → PackageEventService
- `PackageAnnouncement` → AnnouncementsService

---

## 🔧 Configuración

Los servicios obtienen configuración desde:
- `app/config.py`: Configuración centralizada (settings)
- Variables de entorno: `.env` (AWS, SMTP, SMS, etc.)
- Base de datos: Configuraciones dinámicas (tarifas, templates)

---

**Última actualización**: 2025-01-24  
**Versión del documento**: 1.0.0

