# ========================================
# PAQUETES EL CLUB - Servicio de Productos de Facturas
# ========================================
"""
Servicio para gestión de productos extraídos de facturas DIAN.
Incluye auto-matching con catálogo y cálculo de márgenes.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.invoice import InvoiceItem, Invoice
from app.models.product import Product  # Asumiendo que existe

logger = logging.getLogger(__name__)


class InvoiceProductService:
    """Servicio para gestión de productos de facturas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_products(
        self,
        invoice_id: Optional[int] = None,
        matched_only: bool = False,
        unmatched_only: bool = False,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[InvoiceItem], int]:
        """
        Obtiene productos de facturas con filtros.
        
        Args:
            invoice_id: Filtrar por factura específica
            matched_only: Solo productos con match en catálogo
            unmatched_only: Solo productos sin match
            page: Página actual
            per_page: Items por página
            
        Returns:
            Tuple de (productos, total)
        """
        query = self.db.query(InvoiceItem)
        
        if invoice_id:
            query = query.filter(InvoiceItem.invoice_id == invoice_id)
        
        if matched_only:
            query = query.filter(InvoiceItem.matched_with_catalog == True)
        
        if unmatched_only:
            query = query.filter(
                or_(
                    InvoiceItem.matched_with_catalog == False,
                    InvoiceItem.matched_with_catalog == None
                )
            )
        
        total = query.count()
        
        products = query.order_by(InvoiceItem.id.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        return products, total
    
    def auto_match_products(
        self,
        invoice_id: Optional[int] = None,
        confidence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Realiza auto-matching de productos con el catálogo.
        
        Estrategias:
        1. Match exacto por código
        2. Match por código de barras
        3. Fuzzy match por descripción
        
        Args:
            invoice_id: Procesar solo productos de esta factura
            confidence_threshold: Umbral mínimo de confianza (0.0-1.0)
            
        Returns:
            dict con:
                - total: Total de productos procesados
                - matched: Productos con match exitoso
                - failed: Productos sin match
                - results: Lista de resultados
        """
        # Obtener productos sin match
        filters = {}
        if invoice_id:
            filters['invoice_id'] = invoice_id
        
        unmatched_products, _ = self.get_products(
            invoice_id=invoice_id,
            unmatched_only=True,
            per_page=1000  # Procesar en batch
        )
        
        results = {
            'total': len(unmatched_products),
            'matched': 0,
            'failed': 0,
            'results': []
        }
        
        for product in unmatched_products:
            try:
                match_result = self._match_single_product(product, confidence_threshold)
                
                if match_result['matched']:
                    results['matched'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'product_id': product.id,
                    'description': product.descripcion,
                    **match_result
                })
                
            except Exception as e:
                logger.error(f"Error matching product {product.id}: {e}")
                results['failed'] += 1
                results['results'].append({
                    'product_id': product.id,
                    'matched': False,
                    'error': str(e)
                })
        
        self.db.commit()
        
        logger.info(f"Auto-match completado: {results['matched']}/{results['total']} productos")
        
        return results
    
    def _match_single_product(
        self,
        invoice_item: InvoiceItem,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """
        Intenta hacer match de un producto individual.
        
        Args:
            invoice_item: Item de factura a matchear
            confidence_threshold: Umbral de confianza
            
        Returns:
            dict con resultado del match
        """
        # Estrategia 1: Match exacto por código
        if invoice_item.codigo:
            catalog_product = self.db.query(Product).filter(
                Product.codigo == invoice_item.codigo
            ).first()
            
            if catalog_product:
                self._apply_match(
                    invoice_item,
                    catalog_product,
                    confidence=1.0,
                    method='exact_code'
                )
                return {
                    'matched': True,
                    'catalog_product_id': catalog_product.id,
                    'confidence': 1.0,
                    'method': 'exact_code'
                }
        
        # Estrategia 2: Fuzzy match por descripción
        if invoice_item.descripcion:
            fuzzy_result = self._fuzzy_search_catalog(
                invoice_item.descripcion,
                threshold=confidence_threshold
            )
            
            if fuzzy_result:
                self._apply_match(
                    invoice_item,
                    fuzzy_result['product'],
                    confidence=fuzzy_result['similarity'],
                    method='fuzzy_description'
                )
                return {
                    'matched': True,
                    'catalog_product_id': fuzzy_result['product'].id,
                    'confidence': fuzzy_result['similarity'],
                    'method': 'fuzzy_description'
                }
        
        # No se encontró match
        return {
            'matched': False,
            'confidence': 0.0,
            'method': None
        }
    
    def _apply_match(
        self,
        invoice_item: InvoiceItem,
        catalog_product: Product,
        confidence: float,
        method: str
    ) -> None:
        """
        Aplica un match entre item de factura y producto del catálogo.
        
        Args:
            invoice_item: Item de factura
            catalog_product: Producto del catálogo
            confidence: Nivel de confianza del match
            method: Método usado para el match
        """
        invoice_item.product_id = catalog_product.id
        invoice_item.matched_with_catalog = True
        invoice_item.match_confidence = confidence
        invoice_item.match_method = method
        
        logger.debug(f"Match aplicado: Item {invoice_item.id} -> Product {catalog_product.id} ({method}, {confidence:.2f})")
    
    def _fuzzy_search_catalog(
        self,
        description: str,
        threshold: float = 0.85,
        limit: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Búsqueda fuzzy en el catálogo de productos.
        
        Args:
            description: Descripción a buscar
            threshold: Umbral de similitud mínimo
            limit: Número máximo de resultados
            
        Returns:
            dict con producto y similitud, o None
        """
        # Implementación simple usando LIKE
        # En producción, usar pg_trgm o similar para mejor fuzzy matching
        
        search_term = f"%{description.lower()}%"
        
        products = self.db.query(Product).filter(
            func.lower(Product.nombre).like(search_term)
        ).limit(limit).all()
        
        if not products:
            return None
        
        # Calcular similitud simple (en producción usar algoritmo más sofisticado)
        best_match = products[0]
        similarity = self._calculate_similarity(description, best_match.nombre)
        
        if similarity >= threshold:
            return {
                'product': best_match,
                'similarity': similarity
            }
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calcula similitud entre dos strings.
        Implementación simple - en producción usar Levenshtein o similar.
        
        Args:
            str1: Primera string
            str2: Segunda string
            
        Returns:
            float: Similitud 0.0-1.0
        """
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # Similitud simple basada en palabras comunes
        words1 = set(str1_lower.split())
        words2 = set(str2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        return len(common_words) / len(total_words)
    
    def manual_match(
        self,
        invoice_item_id: int,
        catalog_product_id: int
    ) -> Dict[str, Any]:
        """
        Realiza match manual entre item y producto.
        
        Args:
            invoice_item_id: ID del item de factura
            catalog_product_id: ID del producto del catálogo
            
        Returns:
            dict con resultado
        """
        invoice_item = self.db.query(InvoiceItem).filter(
            InvoiceItem.id == invoice_item_id
        ).first()
        
        if not invoice_item:
            raise ValueError(f"Item {invoice_item_id} no encontrado")
        
        catalog_product = self.db.query(Product).filter(
            Product.id == catalog_product_id
        ).first()
        
        if not catalog_product:
            raise ValueError(f"Producto {catalog_product_id} no encontrado")
        
        self._apply_match(
            invoice_item,
            catalog_product,
            confidence=1.0,
            method='manual'
        )
        
        self.db.commit()
        
        return {
            'success': True,
            'invoice_item_id': invoice_item_id,
            'catalog_product_id': catalog_product_id,
            'method': 'manual'
        }
    
    def calculate_margin(
        self,
        invoice_item: InvoiceItem
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula margen de ganancia para un producto.
        
        Args:
            invoice_item: Item de factura con match
            
        Returns:
            dict con:
                - purchase_price: Precio de compra
                - sale_price: Precio de venta
                - margin_amount: Margen en pesos
                - margin_percentage: Margen en porcentaje
                - color: Color para UI (red/yellow/green)
        """
        if not invoice_item.matched_with_catalog or not invoice_item.product_id:
            return None
        
        # Obtener producto del catálogo
        catalog_product = self.db.query(Product).filter(
            Product.id == invoice_item.product_id
        ).first()
        
        if not catalog_product:
            return None
        
        purchase_price = invoice_item.precio_unitario
        sale_price = catalog_product.precio_venta if hasattr(catalog_product, 'precio_venta') else 0
        
        if purchase_price == 0:
            return None
        
        margin_amount = sale_price - purchase_price
        margin_percentage = (margin_amount / purchase_price) * 100
        
        # Determinar color
        if margin_percentage < 0:
            color = 'red'
        elif margin_percentage < 20:
            color = 'yellow'
        else:
            color = 'green'
        
        return {
            'purchase_price': purchase_price,
            'sale_price': sale_price,
            'margin_amount': margin_amount,
            'margin_percentage': round(margin_percentage, 2),
            'color': color
        }
    
    def get_products_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de productos de facturas.
        
        Returns:
            dict con estadísticas
        """
        total = self.db.query(InvoiceItem).count()
        
        matched = self.db.query(InvoiceItem).filter(
            InvoiceItem.matched_with_catalog == True
        ).count()
        
        unmatched = total - matched
        
        # Productos únicos por código
        unique_codes = self.db.query(
            func.count(func.distinct(InvoiceItem.codigo))
        ).scalar()
        
        return {
            'total_items': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': round((matched / total * 100) if total > 0 else 0, 2),
            'unique_codes': unique_codes
        }
    
    def export_products(
        self,
        invoice_id: Optional[int] = None,
        format: str = 'dict'
    ) -> List[Dict[str, Any]]:
        """
        Exporta productos para reportes.
        
        Args:
            invoice_id: Filtrar por factura
            format: Formato de exportación
            
        Returns:
            list: Lista de productos con datos completos
        """
        products, _ = self.get_products(
            invoice_id=invoice_id,
            per_page=10000
        )
        
        export_data = []
        
        for product in products:
            margin = self.calculate_margin(product)
            
            data = {
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
            }
            
            if margin:
                data.update({
                    'precio_venta': margin['sale_price'],
                    'margen_pesos': margin['margin_amount'],
                    'margen_porcentaje': margin['margin_percentage'],
                })
            
            export_data.append(data)
        
        return export_data
