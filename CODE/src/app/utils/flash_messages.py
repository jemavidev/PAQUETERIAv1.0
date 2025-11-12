# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Utilidades para Mensajes Flash
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class FlashMessageType(Enum):
    """Tipos de mensajes flash disponibles"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class FlashMessage:
    """Estructura de un mensaje flash"""
    message: str
    type: FlashMessageType
    title: Optional[str] = None
    auto_close: bool = True
    close_delay: int = 5000
    button_text: str = "Cerrar"
    on_close: Optional[str] = None


class FlashMessageManager:
    """Gestor de mensajes flash para el sistema"""
    
    def __init__(self):
        self._messages: List[FlashMessage] = []
    
    def add_message(
        self,
        message: str,
        message_type: FlashMessageType = FlashMessageType.INFO,
        title: Optional[str] = None,
        auto_close: bool = True,
        close_delay: int = 5000,
        button_text: str = "Cerrar",
        on_close: Optional[str] = None
    ) -> None:
        """Agregar un mensaje flash"""
        flash_message = FlashMessage(
            message=message,
            type=message_type,
            title=title,
            auto_close=auto_close,
            close_delay=close_delay,
            button_text=button_text,
            on_close=on_close
        )
        self._messages.append(flash_message)
    
    def add_success(
        self,
        message: str,
        title: str = "Éxito",
        auto_close: bool = True,
        close_delay: int = 3000
    ) -> None:
        """Agregar mensaje de éxito"""
        self.add_message(
            message=message,
            message_type=FlashMessageType.SUCCESS,
            title=title,
            auto_close=auto_close,
            close_delay=close_delay
        )
    
    def add_error(
        self,
        message: str,
        title: str = "Error",
        auto_close: bool = True,
        close_delay: int = 5000
    ) -> None:
        """Agregar mensaje de error"""
        self.add_message(
            message=message,
            message_type=FlashMessageType.ERROR,
            title=title,
            auto_close=auto_close,
            close_delay=close_delay
        )
    
    def add_warning(
        self,
        message: str,
        title: str = "Advertencia",
        auto_close: bool = True,
        close_delay: int = 5000
    ) -> None:
        """Agregar mensaje de advertencia"""
        self.add_message(
            message=message,
            message_type=FlashMessageType.WARNING,
            title=title,
            auto_close=auto_close,
            close_delay=close_delay
        )
    
    def add_info(
        self,
        message: str,
        title: str = "Información",
        auto_close: bool = True,
        close_delay: int = 4000
    ) -> None:
        """Agregar mensaje de información"""
        self.add_message(
            message=message,
            message_type=FlashMessageType.INFO,
            title=title,
            auto_close=auto_close,
            close_delay=close_delay
        )
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Obtener todos los mensajes en formato para el template"""
        return [
            {
                "message": msg.message,
                "type": msg.type.value,
                "title": msg.title,
                "auto_close": msg.auto_close,
                "close_delay": msg.close_delay,
                "button_text": msg.button_text,
                "on_close": msg.on_close
            }
            for msg in self._messages
        ]
    
    def clear_messages(self) -> None:
        """Limpiar todos los mensajes"""
        self._messages.clear()
    
    def has_messages(self) -> bool:
        """Verificar si hay mensajes"""
        return len(self._messages) > 0


def add_flash_message(
    context: Dict[str, Any],
    message: str,
    message_type: FlashMessageType = FlashMessageType.INFO,
    title: Optional[str] = None,
    auto_close: bool = True,
    close_delay: int = 5000,
    button_text: str = "Cerrar",
    on_close: Optional[str] = None
) -> None:
    """
    Función de conveniencia para agregar mensajes flash al contexto
    
    Args:
        context: Contexto del template
        message: Mensaje a mostrar
        message_type: Tipo de mensaje
        title: Título del mensaje
        auto_close: Si cerrar automáticamente
        close_delay: Tiempo antes de cerrar (ms)
        button_text: Texto del botón de cerrar
        on_close: Código JavaScript a ejecutar al cerrar
    """
    if "flash_messages" not in context:
        context["flash_messages"] = []
    
    flash_message = {
        "message": message,
        "type": message_type.value,
        "title": title,
        "auto_close": auto_close,
        "close_delay": close_delay,
        "button_text": button_text,
        "on_close": on_close
    }
    
    context["flash_messages"].append(flash_message)


def add_success_message(context: Dict[str, Any], message: str, title: str = "Éxito") -> None:
    """Agregar mensaje de éxito"""
    add_flash_message(context, message, FlashMessageType.SUCCESS, title, True, 3000)


def add_error_message(context: Dict[str, Any], message: str, title: str = "Error") -> None:
    """Agregar mensaje de error"""
    add_flash_message(context, message, FlashMessageType.ERROR, title, True, 5000)


def add_warning_message(context: Dict[str, Any], message: str, title: str = "Advertencia") -> None:
    """Agregar mensaje de advertencia"""
    add_flash_message(context, message, FlashMessageType.WARNING, title, True, 5000)


def add_info_message(context: Dict[str, Any], message: str, title: str = "Información") -> None:
    """Agregar mensaje de información"""
    add_flash_message(context, message, FlashMessageType.INFO, title, True, 4000)


def add_validation_errors(context: Dict[str, Any], errors: Dict[str, List[str]]) -> None:
    """Agregar errores de validación"""
    for field, field_errors in errors.items():
        for error in field_errors:
            add_error_message(context, f"{field}: {error}", "Error de Validación")


def add_form_errors(context: Dict[str, Any], errors: Dict[str, Any]) -> None:
    """Agregar errores de formulario"""
    if isinstance(errors, dict):
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                for error in error_list:
                    add_error_message(context, f"{field}: {error}", "Error de Formulario")
            else:
                add_error_message(context, f"{field}: {error_list}", "Error de Formulario")
    else:
        add_error_message(context, str(errors), "Error de Formulario")

