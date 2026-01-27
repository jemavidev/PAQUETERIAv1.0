# ========================================
# PAQUETES EL CLUB - API de Productos de Facturas
# ========================================
"""
API REST para gestión de productos extraídos de facturas DIAN.
Incluye auto-matching y cálculo de márgenes.
"""

import logging
from typing import Optional
import io
import csv

from fastapi import APIRouter, Depends, HTTPException, Query, Form
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user_from_cookies
from app.models.user import User
from app.services.invoice_product_service import InvoiceProductService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["products"])


# ========================================
# ENDPOINTS DE PRODUCTOS
# ========================================

@router.get("")
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    invoice_id: Optional[int] = None,
    matched_only: bool = False,
    unmatched_only: bool = False,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Lista productos de facturas con filtros.
    """
    try:
        service = InvoiceProductService(db)
        
        products, total = service.get_products(
            invoice_id=invoice_id,
            matched_only=matched_only,
            unmatched_only=unmatched_only,
            page=page,
            per_page=per_page
        )
        
        data = []
        for product in products:
            margin = service.calculate_margin(product)
            
            item = {
                'id': product.id,
                'invoice_id': product.invoice_id,
                'codigo': product.codigo,
                'descripcion': product.descripcion,
                'cantidad': product.cantidad,
                'precio_unitario': product.precio_unitario,
                'iva_porcentaje': product.iva_porcentaje,
                'iva_valor': product.iva_valor,
                'valor_total': product.valor_total,
                'matched': product.matched_with_catalog,
                'match_confidence': product.match_confidence,
                'match_method': product.match_method,
                'catalog_product_id': product.product_id
            }
            
            if margin:
                item['margin'] = margin
            
            data.append(item)
        
        return JSONResponse({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error listando productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles de un producto específico.
    """
    try:
        from app.models.invoice import InvoiceItem
        
        product = db.query(InvoiceItem).filter(
            InvoiceItem.id == product_id
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        service = InvoiceProductService(db)
        margin = service.calculate_margin(product)
        
        data = {
            'id': product.id,
            'invoice_id': product.invoice_id,
            'numero_item': product.numero_item,
            'codigo': product.codigo,
            'descripcion': product.descripcion,
            'unidad_medida': product.unidad_medida,
            'cantidad': product.cantidad,
            'precio_unitario': product.precio_unitario,
            'precio_base': product.precio_base,
            'descuento': product.descuento,
            'recargo': product.recargo,
            'iva_porcentaje': product.iva_porcentaje,
            'iva_valor': product.iva_valor,
            'valor_total': product.valor_total,
            'matched': product.matched_with_catalog,
            'match_confidence': product.match_confidence,
            'match_method': product.match_method,
            'catalog_product_id': product.product_id,
            'notas': product.notas
        }
        
        if margin:
            data['margin'] = margin
        
        return JSONResponse({
            'success': True,
            'data': data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_id}/match")
async def match_product(
    product_id: int,
    catalog_product_id: int = Form(...),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Realiza match manual entre producto de factura y catálogo.
    """
    try:
        service = InvoiceProductService(db)
        
        result = service.manual_match(
            invoice_item_id=product_id,
            catalog_product_id=catalog_product_id
        )
        
        return JSONResponse({
            'success': True,
            **result
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en match manual: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-match")
async def auto_match_products(
    invoice_id: Optional[int] = Form(None),
    confidence_threshold: float = Form(0.85),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Ejecuta auto-matching de productos con el catálogo.
    """
    try:
        service = InvoiceProductService(db)
        
        results = service.auto_match_products(
            invoice_id=invoice_id,
            confidence_threshold=confidence_threshold
        )
        
        return JSONResponse({
            'success': True,
            **results
        })
        
    except Exception as e:
        logger.error(f"Error en auto-match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_products_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de productos.
    """
    try:
        service = InvoiceProductService(db)
        stats = service.get_products_stats()
        
        return JSONResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_products(
    invoice_id: Optional[int] = Form(None),
    format: str = Form('csv'),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """
    Exporta productos a CSV o Excel.
    """
    try:
        service = InvoiceProductService(db)
        
        products = service.export_products(
            invoice_id=invoice_id,
            format='dict'
        )
        
        if format == 'csv':
            # Generar CSV
            output = io.StringIO()
            
            if products:
                fieldnames = products[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(products)
            
            # Crear respuesta
            output.seek(0)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=productos_facturas.csv'
                }
            )
        
        elif format == 'json':
            return JSONResponse({
                'success': True,
                'data': products,
                'count': len(products)
            })
        
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exportando productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
