# ========================================
# PAQUETES EL CLUB v4.0 - Configuración Centralizada
# ========================================
# Archivo: CODE/LOCAL/src/app/config.py (siguiendo reglas de AGENTS.md y .kilorules)
# Versión: 1.0.0
# Fecha: 2025-01-24
# Autor: Equipo de Desarrollo
# ========================================

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuración centralizada - Siguiendo reglas KiloCode (.kilorules)"""

    # Configuración de la Aplicación
    app_name: str = os.getenv("APP_NAME", "PAQUETES EL CLUB")
    app_version: str = os.getenv("APP_VERSION", "4.0.0")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Base de Datos - PostgreSQL EXCLUSIVO (regla .kilorules-database)
    database_url: str = os.getenv("DATABASE_URL", "postgresql://dev:dev@localhost:5432/paqueteria_dev")  # ⚠️ DEVELOPMENT FALLBACK - INSECURE
    postgres_user: str = os.getenv("POSTGRES_USER", "")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_db: str = os.getenv("POSTGRES_DB", "")
    postgres_host: str = os.getenv("POSTGRES_HOST", "")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))

    # Cache Redis (desarrollo)
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # Seguridad - JWT obligatorio (regla .kilorules-security)
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-insecure-change-in-production")  # ⚠️ DEVELOPMENT FALLBACK - INSECURE
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas = 1440 minutos

    # Configuración SMTP
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "PAQUETES EL CLUB")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")

    # Configuración SMS (LIWA.co) - Colombia obligatorio
    liwa_api_key: str = os.getenv("LIWA_API_KEY", "")
    liwa_account: str = os.getenv("LIWA_ACCOUNT", "")
    liwa_password: str = os.getenv("LIWA_PASSWORD", "")
    liwa_auth_url: str = os.getenv("LIWA_AUTH_URL", "https://api.liwa.co/v2/auth/login")
    liwa_from_name: str = os.getenv("LIWA_FROM_NAME", "PAQUETES EL CLUB")

    # Configuración de Tarifas - CORREGIDAS
    base_storage_rate: int = int(os.getenv("BASE_STORAGE_RATE", "1000"))
    
    # Tarifas base de entrega por tipo de paquete
    base_delivery_rate_normal: int = int(os.getenv("BASE_DELIVERY_RATE_NORMAL", "1500"))
    base_delivery_rate_extra_dimensioned: int = int(os.getenv("BASE_DELIVERY_RATE_EXTRA_DIMENSIONED", "2000"))
    overtime_rate_per_24h: int = int(os.getenv("OVERTIME_RATE_PER_24H", "1000"))
    
    # Mantener para compatibilidad (deprecated)
    base_delivery_rate: int = int(os.getenv("BASE_DELIVERY_RATE", "1500"))
    normal_package_multiplier: int = int(os.getenv("NORMAL_PACKAGE_MULTIPLIER", "1"))
    extra_dimension_package_multiplier: float = float(os.getenv("EXTRA_DIMENSIONED_PACKAGE_MULTIPLIER", "1.33"))
    currency: str = os.getenv("CURRENCY", "COP")

    # Configuración de Archivos
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    allowed_extensions: str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp")
    allowed_image_types: str = os.getenv("ALLOWED_IMAGE_TYPES", "jpg,jpeg,png,webp")
    allowed_document_types: str = os.getenv("ALLOWED_DOCUMENT_TYPES", "pdf,doc,docx")
    max_file_uploads: int = int(os.getenv("MAX_FILE_UPLOADS", "3"))

    # Configuración AWS S3 - SOLO desde .env
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "")

    # Configuración de la Empresa
    company_name: str = os.getenv("COMPANY_NAME", "PAQUETES EL CLUB")
    company_display_name: str = os.getenv("COMPANY_DISPLAY_NAME", "PAQUETES EL CLUB")
    company_short_name: str = os.getenv("COMPANY_SHORT_NAME", "PEC")
    company_website: str = os.getenv("COMPANY_WEBSITE", "https://paquetes.com.co")
    company_address: str = os.getenv("COMPANY_ADDRESS", "Cra. 91 #54-120, Local 12")
    company_phone: str = os.getenv("COMPANY_PHONE", "3334004007")
    company_email: str = os.getenv("COMPANY_EMAIL", "guia@papyrus.com.co")
    
    # Configuración Geográfica
    default_country: str = os.getenv("DEFAULT_COUNTRY", "Colombia")
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "America/Bogota")
    default_phone_prefix: str = os.getenv("DEFAULT_PHONE_PREFIX", "+57")
    default_phone_length: int = int(os.getenv("DEFAULT_PHONE_LENGTH", "10"))
    
    # URLs y Dominios
    production_url: str = os.getenv("PRODUCTION_URL", "https://paquetes.com.co")
    development_url: str = os.getenv("DEVELOPMENT_URL", "http://localhost:8000")
    tracking_base_url: str = os.getenv("TRACKING_BASE_URL", "https://paquetes.com.co/seguimiento")
    
    # Configuración de Mensajes SMS
    sms_daily_limit: int = int(os.getenv("SMS_DAILY_LIMIT", "1000"))
    sms_monthly_limit: int = int(os.getenv("SMS_MONTHLY_LIMIT", "30000"))
    sms_max_message_length: int = int(os.getenv("SMS_MAX_MESSAGE_LENGTH", "2000"))
    sms_default_sender: str = os.getenv("SMS_DEFAULT_SENDER", "PAQUETES EL CLUB")
    
    # Plantillas de Mensajes SMS
    sms_announcement_template: str = os.getenv("SMS_ANNOUNCEMENT_TEMPLATE", "PAQUETES EL CLUB: Su paquete con guía {guide_number} ha sido anunciado. Código: {tracking_code}. Más info: {tracking_url}")
    sms_received_template: str = os.getenv("SMS_RECEIVED_TEMPLATE", "PAQUETES EL CLUB: Su paquete {guide_number} ha sido RECIBIDO en nuestras instalaciones. Código: {tracking_code}. Procesaremos su entrega pronto.")
    sms_delivered_template: str = os.getenv("SMS_DELIVERED_TEMPLATE", "PAQUETES EL CLUB: ¡Su paquete {guide_number} ha sido ENTREGADO exitosamente! Código: {tracking_code}. Gracias por confiar en nosotros.")
    sms_cancelled_template: str = os.getenv("SMS_CANCELLED_TEMPLATE", "PAQUETES EL CLUB: Su paquete {guide_number} ha sido CANCELADO. Código: {tracking_code}. Contacte con nosotros para más información.")
    sms_payment_reminder_template: str = os.getenv("SMS_PAYMENT_REMINDER_TEMPLATE", "PAQUETES EL CLUB: Tiene un pago pendiente por ${amount} COP para el paquete {guide_number}. Realice el pago para continuar con la entrega.")
    
    # Configuración de UI
    toast_default_duration: int = int(os.getenv("TOAST_DEFAULT_DURATION", "5000"))
    toast_success_duration: int = int(os.getenv("TOAST_SUCCESS_DURATION", "3000"))
    toast_error_duration: int = int(os.getenv("TOAST_ERROR_DURATION", "5000"))
    toast_info_duration: int = int(os.getenv("TOAST_INFO_DURATION", "2000"))
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Datos de Prueba (Solo desarrollo)
    test_phone_number_1: str = os.getenv("TEST_PHONE_NUMBER_1", "3000000000")
    test_phone_number_2: str = os.getenv("TEST_PHONE_NUMBER_2", "3001234567")
    test_phone_number_3: str = os.getenv("TEST_PHONE_NUMBER_3", "3009876543")

    # Configuración de Monitoreo
    grafana_password: str = os.getenv("GRAFANA_PASSWORD", "")
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    grafana_port: int = int(os.getenv("GRAFANA_PORT", "3000"))

    # Configuración de Logs
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/app.log")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Configuración de PWA
    pwa_name: str = os.getenv("PWA_NAME", "PAQUETES EL CLUB")
    pwa_short_name: str = os.getenv("PWA_SHORT_NAME", "Paquetes")
    pwa_description: str = os.getenv("PWA_DESCRIPTION", "Sistema de gestión de paquetería")
    pwa_theme_color: str = os.getenv("PWA_THEME_COLOR", "#3B82F6")
    pwa_background_color: str = os.getenv("PWA_BACKGROUND_COLOR", "#FFFFFF")

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        # En Docker, las variables se cargan desde .env mediante docker-compose
        # No necesitamos buscar el archivo .env dentro del contenedor
        # Las variables de entorno ya están disponibles desde docker-compose
        env_file=None,  # Usar solo variables de entorno del sistema
        env_file_encoding="utf-8"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_required_settings()

    def _validate_required_settings(self):
        """Validar que las configuraciones críticas estén presentes"""
        required_vars = []

        # In production, database URL must be properly configured (not the dev fallback)
        if self.environment == "production":
            if not self.database_url or "dev:dev@localhost" in self.database_url:
                required_vars.append("DATABASE_URL (production)")

            if not self.secret_key or "dev-secret-key-insecure" in self.secret_key:
                required_vars.append("SECRET_KEY (production)")

            if not self.smtp_password:
                required_vars.append("SMTP_PASSWORD (required for production email)")

        # AWS S3 credentials are required for file operations - SOLO desde .env
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            required_vars.append("AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY (requeridas para S3)")

        if not self.aws_s3_bucket:
            required_vars.append("AWS_S3_BUCKET (requerido para S3)")

        # Detectar credenciales de ejemplo
        example_credentials = [
            'your-aws-access-key', 'your-aws-secret-key', 
            'AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'your-access-key', 'your-secret-key'
        ]
        
        if self.aws_access_key_id in example_credentials:
            required_vars.append("AWS_ACCESS_KEY_ID (configure credenciales reales en .env)")
            
        if self.aws_secret_access_key in example_credentials:
            required_vars.append("AWS_SECRET_ACCESS_KEY (configure credenciales reales en .env)")

        # Show warnings for development insecure fallbacks
        if self.environment == "development":
            if "dev:dev@localhost" in self.database_url:
                print("⚠️  ADVERTENCIA: Usando configuración de base de datos de desarrollo insegura")
                print("   Configure DATABASE_URL en .env para producción")

            if "dev-secret-key-insecure" in self.secret_key:
                print("⚠️  ADVERTENCIA: Usando clave JWT de desarrollo insegura")
                print("   Configure SECRET_KEY en .env para producción")

        if required_vars:
            raise ValueError(
                f"Variables de entorno requeridas para {self.environment} no encontradas: {', '.join(required_vars)}. "
                "Configure estas variables en su archivo .env"
            )

# Instancia global de configuración
try:
    settings = Settings()
    print("✅ Configuración KiloCode cargada correctamente")
    print(f"📊 Ambiente: {settings.environment}")
    print(f"🗄️ Base de datos: {'✅ Configurada' if settings.database_url else '❌ No configurada'}")
    print(f"🔐 JWT Secret: {'✅ Configurado' if settings.secret_key else '❌ No configurado'}")
except Exception as e:
    print(f"❌ Error cargando configuración KiloCode: {e}")
    print("💡 Asegúrate de que las variables de entorno requeridas estén configuradas en .env")
    raise