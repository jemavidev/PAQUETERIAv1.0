# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Servicio Base
Versión: 2.0.0 (Optimizado para rendimiento)
Fecha: 2026-01-08
Autor: Equipo de Desarrollo

OPTIMIZACIONES v2.0:
- Métodos optimizados para evitar N+1
- Mejor manejo de transacciones
- Logging mejorado
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.database import get_db

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Servicio base con operaciones CRUD comunes optimizadas
    """

    def __init__(self, model: Any):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """Obtener registro por ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error en get_by_id: {e}")
            db.rollback()
            raise e

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtener todos los registros con paginación"""
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error en get_all: {e}")
            db.rollback()
            raise e

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Crear nuevo registro"""
        try:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error en create: {e}")
            db.rollback()
            raise e

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Actualizar registro existente"""
        try:
            obj_data = obj_in.model_dump(exclude_unset=True)
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error en update: {e}")
            db.rollback()
            raise e

    def delete(self, db: Session, id: int) -> bool:
        """Eliminar registro por ID"""
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error en delete: {e}")
            db.rollback()
            raise e

    def exists(self, db: Session, id: int) -> bool:
        """Verificar si existe un registro (optimizado)"""
        try:
            # Usar exists() es más eficiente que first()
            from sqlalchemy import exists as sql_exists
            return db.query(sql_exists().where(self.model.id == id)).scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error en exists: {e}")
            db.rollback()
            raise e

    def count(self, db: Session) -> int:
        """Contar total de registros"""
        try:
            return db.query(self.model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error en count: {e}")
            db.rollback()
            raise e

    def search(self, db: Session, query: str, fields: List[str], skip: int = 0, limit: int = 50) -> List[ModelType]:
        """Búsqueda básica en campos especificados"""
        try:
            search_filters = []
            for field in fields:
                if hasattr(self.model, field):
                    search_filters.append(getattr(self.model, field).ilike(f"%{query}%"))

            if search_filters:
                return db.query(self.model).filter(or_(*search_filters)).offset(skip).limit(limit).all()
            return []
        except SQLAlchemyError as e:
            logger.error(f"Error en search: {e}")
            db.rollback()
            raise e

    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtener registros activos (si tienen campo is_active)"""
        try:
            if hasattr(self.model, 'is_active'):
                return db.query(self.model).filter(self.model.is_active == True).offset(skip).limit(limit).all()
            return self.get_all(db, skip, limit)
        except SQLAlchemyError as e:
            logger.error(f"Error en get_active: {e}")
            db.rollback()
            raise e
    
    def bulk_create(self, db: Session, objects: List[CreateSchemaType]) -> List[ModelType]:
        """Crear múltiples registros de forma eficiente"""
        try:
            db_objects = []
            for obj_in in objects:
                obj_data = obj_in.model_dump()
                db_obj = self.model(**obj_data)
                db.add(db_obj)
                db_objects.append(db_obj)
            
            # Un solo commit para todos los objetos
            db.commit()
            
            for db_obj in db_objects:
                db.refresh(db_obj)
            
            return db_objects
        except SQLAlchemyError as e:
            logger.error(f"Error en bulk_create: {e}")
            db.rollback()
            raise e