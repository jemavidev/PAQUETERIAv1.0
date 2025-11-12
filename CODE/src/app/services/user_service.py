# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Servicio de Usuarios
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from .base import BaseService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserRole
from app.utils.auth import get_password_hash, verify_password


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    Servicio para gestión de usuarios
    """

    def __init__(self):
        super().__init__(User)

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Crear nuevo usuario con contraseña hasheada"""
        # Hashear contraseña
        hashed_password = get_password_hash(user_in.password)

        # Crear objeto usuario con solo los campos válidos
        user_data = {
            'username': user_in.username,
            'email': user_in.email,
            'password_hash': hashed_password,
            'full_name': user_in.full_name,
            'role': user_in.role,
            'is_active': user_in.is_active
        }

        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Autenticar usuario por username/email y contraseña"""
        user = self._get_user_by_username_or_email(db, username)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()

    def update_password(self, db: Session, user_id: int, new_password: str) -> bool:
        """Actualizar contraseña de usuario"""
        user = self.get_by_id(db, user_id)
        if not user:
            return False

        user.password_hash = get_password_hash(new_password)
        db.commit()
        return True

    def update_user_role(self, db: Session, user_id: int, new_role: UserRole) -> bool:
        """Actualizar rol de usuario"""
        user = self.get_by_id(db, user_id)
        if not user:
            return False

        user.role = new_role
        db.commit()
        return True

    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Desactivar usuario"""
        user = self.get_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        db.commit()
        return True

    def activate_user(self, db: Session, user_id: int) -> bool:
        """Activar usuario"""
        user = self.get_by_id(db, user_id)
        if not user:
            return False

        user.is_active = True
        db.commit()
        return True

    def get_users_by_role(self, db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener usuarios por rol"""
        return db.query(User).filter(
            and_(User.role == role, User.is_active == True)
        ).offset(skip).limit(limit).all()

    def search_users(self, db: Session, query: str, skip: int = 0, limit: int = 50) -> List[User]:
        """Buscar usuarios por nombre, username o email"""
        search_filters = [
            User.full_name.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        ]

        return db.query(User).filter(or_(*search_filters)).offset(skip).limit(limit).all()

    def get_user_stats(self, db: Session) -> dict:
        """Obtener estadísticas de usuarios"""
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        operator_users = db.query(User).filter(User.role == UserRole.OPERADOR).count()
        regular_users = db.query(User).filter(User.role == UserRole.USUARIO).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "operator_users": operator_users,
            "regular_users": regular_users
        }

    def _get_user_by_username_or_email(self, db: Session, identifier: str) -> Optional[User]:
        """Obtener usuario por username o email"""
        return db.query(User).filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()