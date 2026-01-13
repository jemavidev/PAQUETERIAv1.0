# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Rutas de Productos
Versión: 1.0.0
Fecha: 2026-01-13
Autor: Equipo de Desarrollo
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from datetime import datetime
import logging

from app.database import get_db
from app.models.product import Product, ProductColumnConfig, ProductSyncLog
from app.services.product_sync_service import ProductSyncService
from app.dependencies import get_current_active_user, get_current_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/products",
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}}
)


@router.get("/", response_model=dict)
async def list_products(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Búsqueda por código, nombre o descripción"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    vendible: Optional[bool] = Query(None, description="Filtrar por vendible"),
    tipo_id: Optional[int] = Query(None, description="Filtrar por tipo"),
    marca_id: Optional[int] = Query(None, description="Filtrar por marca"),
    linea_id: Optional[int] = Query(None, description="Filtrar por línea"),
    destacado: Optional[bool] = Query(None, description="Filtrar por destacado"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Listar productos con filtros y paginación
    """
    try:
        # Construir query base
        query = db.query(Product)
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.codigo.ilike(search_term),
                    Product.nombre.ilike(search_term),
                    Product.descripcion.ilike(search_term),
                    Product.codigo_barra.ilike(search_term),
                    Product.referencia.ilike(search_term)
                )
            )
        
        if activo is not None:
            query = query.filter(Product.activo == activo)
        
        if vendible is not None:
            query = query.filter(Product.vendible == vendible)
        
        if tipo_id is not None:
            query = query.filter(Product.tipo_id == tipo_id)
        
        if marca_id is not None:
            query = query.filter(Product.marca_id == marca_id)
        
        if linea_id is not None:
            query = query.filter(Product.linea_id == linea_id)
        
        if destacado is not None:
            query = query.filter(Product.destacado == destacado)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        offset = (page - 1) * page_size
        products = query.order_by(Product.nombre).offset(offset).limit(page_size).all()
        
        # Convertir a diccionarios
        products_data = [product.to_dict() for product in products]
        
        return {
            "success": True,
            "data": products_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Error listando productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando productos: {str(e)}"
        )


@router.get("/{product_id}", response_model=dict)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtener detalle de un producto por ID
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return {
            "success": True,
            "data": product.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo producto: {str(e)}"
        )


@router.post("/sync", response_model=dict)
async def sync_products(
    activo: Optional[bool] = Query(None, description="Sincronizar solo productos activos"),
    vendible: Optional[bool] = Query(None, description="Sincronizar solo productos vendibles"),
    visualizable_web: Optional[bool] = Query(None, description="Sincronizar solo productos visualizables en web"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Sincronizar productos desde DynamiaERP (solo administradores)
    """
    try:
        # Construir filtros
        filters = {}
        if activo is not None:
            filters['activo'] = activo
        if vendible is not None:
            filters['vendible'] = vendible
        if visualizable_web is not None:
            filters['visualizableWeb'] = visualizable_web
        
        # Ejecutar sincronización
        sync_service = ProductSyncService(db)
        result = sync_service.sync_products(filters=filters if filters else None)
        
        return {
            "success": result['success'],
            "message": "Sincronización completada" if result['success'] else "Sincronización con errores",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error sincronizando productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando productos: {str(e)}"
        )


@router.get("/search/advanced", response_model=dict)
async def search_products(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Búsqueda avanzada de productos usando índice de texto completo
    """
    try:
        # Búsqueda usando índice de texto completo
        search_query = func.to_tsquery('spanish', q.replace(' ', ' & '))
        
        products = db.query(Product).filter(
            and_(
                Product.activo == True,
                func.to_tsvector('spanish', 
                    func.coalesce(Product.nombre, '') + ' ' + 
                    func.coalesce(Product.descripcion, '') + ' ' + 
                    func.coalesce(Product.codigo, '')
                ).op('@@')(search_query)
            )
        ).limit(limit).all()
        
        return {
            "success": True,
            "data": [product.to_dict() for product in products],
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda avanzada: {e}")
        # Fallback a búsqueda simple
        try:
            search_term = f"%{q}%"
            products = db.query(Product).filter(
                and_(
                    Product.activo == True,
                    or_(
                        Product.codigo.ilike(search_term),
                        Product.nombre.ilike(search_term),
                        Product.codigo_barra.ilike(search_term)
                    )
                )
            ).limit(limit).all()
            
            return {
                "success": True,
                "data": [product.to_dict() for product in products],
                "count": len(products)
            }
        except Exception as e2:
            logger.error(f"Error en búsqueda fallback: {e2}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en búsqueda: {str(e2)}"
            )


@router.get("/sync/history", response_model=dict)
async def get_sync_history(
    limit: int = Query(10, ge=1, le=50, description="Límite de registros"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Obtener historial de sincronizaciones (solo administradores)
    """
    try:
        logs = db.query(ProductSyncLog).order_by(
            ProductSyncLog.sync_date.desc()
        ).limit(limit).all()
        
        return {
            "success": True,
            "data": [log.to_dict() for log in logs],
            "count": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de sincronización: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial: {str(e)}"
        )


@router.get("/columns/config", response_model=dict)
async def get_column_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtener configuración de columnas del usuario actual
    """
    try:
        configs = db.query(ProductColumnConfig).filter(
            ProductColumnConfig.user_id == current_user.id
        ).order_by(ProductColumnConfig.order_index).all()
        
        # Si no tiene configuración, devolver columnas por defecto
        if not configs:
            default_columns = [
                {"column_key": "codigo", "column_label": "Código Único", "visible": True, "order_index": 0},
                {"column_key": "referencia", "column_label": "Referencia", "visible": True, "order_index": 1},
                {"column_key": "nombre", "column_label": "Nombre", "visible": True, "order_index": 2},
                {"column_key": "linea_nombre", "column_label": "Línea", "visible": True, "order_index": 3},
                {"column_key": "tipo_nombre", "column_label": "Tipo", "visible": True, "order_index": 4},
                {"column_key": "costo_aproximado", "column_label": "Costo", "visible": True, "order_index": 5},
                {"column_key": "precio_venta", "column_label": "Precio de Venta", "visible": True, "order_index": 6},
                {"column_key": "existencias_totales", "column_label": "Cantidad Inicial", "visible": True, "order_index": 7},
                {"column_key": "marca_nombre", "column_label": "Marca", "visible": True, "order_index": 8},
                {"column_key": "descripcion", "column_label": "Descripción", "visible": True, "order_index": 9},
                {"column_key": "existencias_minimas", "column_label": "Stock Mínimo", "visible": True, "order_index": 10},
                {"column_key": "existencias_maximas", "column_label": "Stock Máximo", "visible": True, "order_index": 11},
                {"column_key": "codigo_barra", "column_label": "Código de Barras", "visible": True, "order_index": 12},
            ]
            return {
                "success": True,
                "data": default_columns
            }
        
        return {
            "success": True,
            "data": [config.to_dict() for config in configs]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de columnas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )


@router.post("/columns/config", response_model=dict)
async def save_column_config(
    columns: List[dict],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Guardar configuración de columnas del usuario actual
    """
    try:
        # Eliminar configuración anterior
        db.query(ProductColumnConfig).filter(
            ProductColumnConfig.user_id == current_user.id
        ).delete()
        
        # Crear nueva configuración
        for col in columns:
            config = ProductColumnConfig(
                user_id=current_user.id,
                column_key=col['column_key'],
                column_label=col['column_label'],
                visible=col.get('visible', True),
                order_index=col.get('order_index', 0),
                width=col.get('width')
            )
            db.add(config)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Configuración guardada correctamente"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error guardando configuración de columnas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando configuración: {str(e)}"
        )
