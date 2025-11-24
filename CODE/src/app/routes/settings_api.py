"""
API endpoints para Settings (Configuración)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_active_user_from_cookies
from app.utils.auth import hash_password_for_storage, verify_password

router = APIRouter(prefix="/api/settings", tags=["settings"])


# === SCHEMAS ===

class ProfileUpdate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class NotificationPreferences(BaseModel):
    sms_arrival: bool = True
    email_confirmation: bool = True
    push_notifications: bool = False
    notify_package_received: bool = True
    notify_package_delivered: bool = True
    notify_messages: bool = True
    marketing: bool = False


# === ENDPOINTS ===

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar información del perfil del usuario"""
    try:
        # Verificar si el email ya existe (si cambió)
        if profile_data.email != current_user.email:
            existing_user = db.query(User).filter(User.email == profile_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está en uso"
                )
        
        # Actualizar datos
        current_user.full_name = profile_data.full_name
        current_user.email = profile_data.email
        if profile_data.phone:
            current_user.phone = profile_data.phone
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": "Perfil actualizado correctamente",
            "user": {
                "full_name": current_user.full_name,
                "email": current_user.email,
                "phone": current_user.phone
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario"""
    try:
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Validar nueva contraseña
        if len(password_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 8 caracteres"
            )
        
        # Actualizar contraseña
        current_user.hashed_password = hash_password_for_storage(password_data.new_password)
        db.commit()
        
        return {
            "success": True,
            "message": "Contraseña cambiada correctamente"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.put("/notifications")
async def update_notifications(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Actualizar preferencias de notificaciones"""
    try:
        from app.models.user_preferences import UserPreferences
        
        # Buscar o crear preferencias del usuario
        user_prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == current_user.id
        ).first()
        
        if not user_prefs:
            # Crear nuevas preferencias
            user_prefs = UserPreferences(user_id=current_user.id)
            db.add(user_prefs)
        
        # Actualizar campos de notificaciones
        user_prefs.sms_notifications_enabled = preferences.sms_arrival
        user_prefs.email_notifications_enabled = preferences.email_confirmation
        user_prefs.push_notifications_enabled = preferences.push_notifications
        user_prefs.notify_package_received = preferences.notify_package_received
        user_prefs.notify_package_delivered = preferences.notify_package_delivered
        user_prefs.notify_messages = preferences.notify_messages
        
        # Guardar marketing en additional_preferences
        if not user_prefs.additional_preferences:
            user_prefs.additional_preferences = {}
        user_prefs.additional_preferences['marketing_enabled'] = preferences.marketing
        
        db.commit()
        db.refresh(user_prefs)
        
        return {
            "success": True,
            "message": "Preferencias guardadas correctamente",
            "preferences": {
                "sms_arrival": user_prefs.sms_notifications_enabled,
                "email_confirmation": user_prefs.email_notifications_enabled,
                "push_notifications": user_prefs.push_notifications_enabled,
                "notify_package_received": user_prefs.notify_package_received,
                "notify_package_delivered": user_prefs.notify_package_delivered,
                "notify_messages": user_prefs.notify_messages,
                "marketing": user_prefs.additional_preferences.get('marketing_enabled', False)
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar preferencias: {str(e)}"
        )


@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener preferencias de notificaciones del usuario"""
    try:
        from app.models.user_preferences import UserPreferences
        
        # Cargar preferencias del usuario
        user_prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == current_user.id
        ).first()
        
        if not user_prefs:
            # Retornar valores por defecto si no existen preferencias
            return {
                "success": True,
                "preferences": {
                    "sms_arrival": False,
                    "email_confirmation": True,
                    "push_notifications": False,
                    "notify_package_received": True,
                    "notify_package_delivered": True,
                    "notify_messages": True,
                    "marketing": False
                }
            }
        
        # Retornar preferencias reales
        return {
            "success": True,
            "preferences": {
                "sms_arrival": user_prefs.sms_notifications_enabled,
                "email_confirmation": user_prefs.email_notifications_enabled,
                "push_notifications": user_prefs.push_notifications_enabled,
                "notify_package_received": user_prefs.notify_package_received,
                "notify_package_delivered": user_prefs.notify_package_delivered,
                "notify_messages": user_prefs.notify_messages,
                "marketing": user_prefs.additional_preferences.get('marketing_enabled', False) if user_prefs.additional_preferences else False
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener preferencias: {str(e)}"
        )

