# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Formateador de Errores
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from typing import Dict, List, Any, Union
from pydantic import ValidationError
from fastapi import HTTPException
import json

class ErrorFormatter:
    """Formateador de errores para hacer mensajes más amigables al usuario"""
    
    # Mapeo de tipos de error de Pydantic a mensajes simples y amigables
    ERROR_MESSAGES = {
        "string_too_short": {
            "title": "Mensaje muy corto",
            "message": "Tu mensaje es muy corto. Escribe al menos {min_length} caracteres.",
            "suggestion": "Agrega más detalles a tu mensaje."
        },
        "string_too_long": {
            "title": "Mensaje muy largo", 
            "message": "Tu mensaje es muy largo. Máximo {max_length} caracteres.",
            "suggestion": "Acorta tu mensaje."
        },
        "value_error": {
            "title": "Datos incorrectos",
            "message": "Los datos que ingresaste no son correctos.",
            "suggestion": "Revisa la información y vuelve a intentar."
        },
        "type_error": {
            "title": "Formato incorrecto",
            "message": "El formato de los datos no es correcto.",
            "suggestion": "Verifica que la información esté bien escrita."
        },
        "missing": {
            "title": "Falta información",
            "message": "Necesitamos que completes todos los campos.",
            "suggestion": "Llena todos los campos requeridos."
        },
        "extra_forbidden": {
            "title": "Campo no válido",
            "message": "Este campo no es válido.",
            "suggestion": "Usa solo los campos disponibles."
        },
        "string_pattern_mismatch": {
            "title": "Formato incorrecto",
            "message": "El formato no es correcto.",
            "suggestion": "Verifica que esté bien escrito."
        }
    }
    
    # Mapeo de campos a nombres simples
    FIELD_NAMES = {
        "content": "mensaje",
        "subject": "asunto", 
        "customer_name": "nombre",
        "customer_phone": "teléfono",
        "customer_email": "correo",
        "package_guide_number": "guía",
        "package_tracking_code": "código",
        "tracking_number": "código",
        "guide_number": "guía",
        "phone": "teléfono",
        "email": "correo",
        "name": "nombre",
        "full_name": "nombre"
    }
    
    @classmethod
    def format_validation_error(cls, error: ValidationError) -> Dict[str, Any]:
        """
        Formatear error de validación de Pydantic a un formato amigable
        
        Args:
            error: Error de validación de Pydantic
            
        Returns:
            Dict con el error formateado
        """
        formatted_errors = []
        
        for err in error.errors():
            field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
            field_name = cls._get_friendly_field_name(field_path)
            error_type = err.get("type", "value_error")
            
            # Obtener mensaje base
            error_info = cls.ERROR_MESSAGES.get(error_type, {
                "title": "Error de validación",
                "message": err.get("msg", "Error desconocido"),
                "suggestion": "Por favor, revisa el campo."
            })
            
            # Personalizar mensaje con contexto
            message = error_info["message"]
            if "min_length" in err.get("ctx", {}):
                message = message.format(min_length=err["ctx"]["min_length"])
            elif "max_length" in err.get("ctx", {}):
                message = message.format(max_length=err["ctx"]["max_length"])
            
            formatted_errors.append({
                "field": field_name,
                "field_path": field_path,
                "error_type": error_type,
                "title": error_info["title"],
                "message": message,
                "suggestion": error_info["suggestion"],
                "input_value": err.get("input", ""),
                "context": err.get("ctx", {})
            })
        
        return {
            "is_validation_error": True,
            "error_type": "validation_error",
            "title": "Revisa tu información",
            "message": f"Hay {len(formatted_errors)} problema(s) que necesitas corregir:",
            "errors": formatted_errors,
            "suggestion": "Corrige los errores y vuelve a intentar."
        }
    
    @classmethod
    def format_http_exception(cls, exc: HTTPException) -> Dict[str, Any]:
        """
        Formatear excepción HTTP a un formato amigable
        
        Args:
            exc: Excepción HTTP de FastAPI
            
        Returns:
            Dict con el error formateado
        """
        return {
            "is_validation_error": False,
            "error_type": "http_error",
            "title": "Algo salió mal",
            "message": "No pudimos procesar tu solicitud. Intenta nuevamente.",
            "status_code": exc.status_code,
            "suggestion": "Si el problema persiste, contacta al soporte."
        }
    
    @classmethod
    def format_generic_error(cls, error: Exception) -> Dict[str, Any]:
        """
        Formatear error genérico a un formato amigable
        
        Args:
            error: Excepción genérica
            
        Returns:
            Dict con el error formateado
        """
        return {
            "is_validation_error": False,
            "error_type": "generic_error",
            "title": "Algo salió mal",
            "message": "Ocurrió un error inesperado. Intenta nuevamente.",
            "suggestion": "Si el problema persiste, contacta al soporte."
        }
    
    @classmethod
    def _get_friendly_field_name(cls, field_path: str) -> str:
        """
        Obtener nombre amigable del campo
        
        Args:
            field_path: Ruta del campo (ej: "body.content")
            
        Returns:
            Nombre amigable del campo
        """
        # Extraer el último elemento de la ruta
        field_name = field_path.split(".")[-1] if "." in field_path else field_path
        
        # Buscar en el mapeo de nombres amigables
        return cls.FIELD_NAMES.get(field_name, field_name.replace("_", " ").title())
    
    @classmethod
    def create_user_friendly_message(cls, error: Union[ValidationError, HTTPException, Exception]) -> str:
        """
        Crear mensaje amigable para mostrar al usuario
        
        Args:
            error: Error a formatear
            
        Returns:
            String con mensaje amigable
        """
        # Verificar si es RequestValidationError (que contiene errores de validación)
        if hasattr(error, 'errors') and hasattr(error, '__class__') and 'ValidationError' in str(error.__class__):
            # Es un RequestValidationError, procesar los errores
            if hasattr(error, 'errors') and callable(error.errors):
                errors_list = error.errors()
            elif hasattr(error, 'errors'):
                errors_list = error.errors
            else:
                errors_list = []
                
            if errors_list:
                first_error = errors_list[0]
                # Si es error de longitud mínima, mostrar mensaje específico
                if first_error.get('type') == 'string_too_short':
                    min_length = first_error.get('ctx', {}).get('min_length', 10)
                    return f"El mensaje debe tener al menos {min_length} caracteres"
                return f"❌ {first_error.get('msg', 'Error de validación')}"
            return "❌ Error de validación"
        
        elif isinstance(error, ValidationError):
            formatted = cls.format_validation_error(error)
            # Solo mostrar el primer error de manera simple
            if formatted['errors']:
                first_error = formatted['errors'][0]
                # Si es error de longitud mínima, mostrar mensaje específico
                if first_error['error_type'] == 'string_too_short':
                    min_length = first_error['context'].get('min_length', 10)
                    return f"El mensaje debe tener al menos {min_length} caracteres"
                return f"❌ {first_error['message']}"
            return f"❌ {formatted['message']}"
        
        elif isinstance(error, HTTPException):
            formatted = cls.format_http_exception(error)
            return f"❌ {formatted['message']}"
        
        else:
            formatted = cls.format_generic_error(error)
            return f"❌ {formatted['message']}"

# Función de conveniencia para uso rápido
def format_error(error: Union[ValidationError, HTTPException, Exception]) -> Dict[str, Any]:
    """
    Función de conveniencia para formatear errores
    
    Args:
        error: Error a formatear
        
    Returns:
        Dict con el error formateado
    """
    if isinstance(error, ValidationError):
        return ErrorFormatter.format_validation_error(error)
    elif isinstance(error, HTTPException):
        return ErrorFormatter.format_http_exception(error)
    else:
        return ErrorFormatter.format_generic_error(error)

def create_user_message(error: Union[ValidationError, HTTPException, Exception]) -> str:
    """
    Función de conveniencia para crear mensaje amigable
    
    Args:
        error: Error a formatear
        
    Returns:
        String con mensaje amigable
    """
    return ErrorFormatter.create_user_friendly_message(error)
