"""
Servicio de sincronización de productos desde DynamiaERP

Soporta dos modos de sincronización:
1. FULL: Descarga completa de todos los productos
2. INCREMENTAL: Solo productos modificados desde última sincronización
"""
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.product import Product, ProductSyncLog
import os

logger = logging.getLogger(__name__)


def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normalizar datetime para comparaciones seguras.
    Convierte a UTC naive (sin timezone) para evitar errores de comparación.
    
    Args:
        dt: Datetime con o sin timezone
        
    Returns:
        Datetime naive en UTC o None
    """
    if dt is None:
        return None
    
    # Si tiene timezone, convertir a UTC y remover timezone
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    return dt


class ProductSyncService:
    """Servicio para sincronizar productos desde DynamiaERP"""
    
    def __init__(self, db: Session):
        self.db = db
        self.token = os.getenv('DYNAMIA_TOKEN')
        self.base_url = os.getenv('DYNAMIA_API_URL', 'https://api.dynamiaerp.co')
        self.account_id = int(os.getenv('DYNAMIA_ACCOUNT_ID', 128))
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers con autenticación"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def fetch_all_products_from_dynamia(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los productos de DynamiaERP (sincronización completa)
        
        Returns:
            Lista de productos
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/inventario/items",
                headers=self.get_headers(),
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('data', [])
            
            logger.info(f"Obtenidos {len(items)} productos de DynamiaERP (sincronización completa)")
            return items
            
        except Exception as e:
            logger.error(f"Error obteniendo productos de DynamiaERP: {e}")
            raise
    
    def _extract_product_date(self, dynamia_item: Dict[str, Any]) -> Optional[datetime]:
        """
        Extraer fecha de última actualización del producto
        
        Args:
            dynamia_item: Item de DynamiaERP
            
        Returns:
            Fecha de actualización o None
        """
        # Intentar varios campos de fecha en orden de prioridad
        date_fields = [
            'lastUpdateInstant',
            'lastUpdate', 
            'creationInstant',
            'creationTimestamp'
        ]
        
        for field in date_fields:
            date_value = dynamia_item.get(field)
            if date_value:
                try:
                    if isinstance(date_value, str):
                        # Formato ISO con Z
                        return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    elif isinstance(date_value, (int, float)):
                        # Timestamp en milisegundos
                        return datetime.fromtimestamp(date_value / 1000)
                except Exception as e:
                    logger.debug(f"Error parseando fecha {field}={date_value}: {e}")
                    continue
        
        return None
    
    def _has_significant_changes(
        self, 
        existing: Product, 
        new_data: Dict[str, Any]
    ) -> bool:
        """
        Verificar si hay cambios significativos en el producto
        
        Args:
            existing: Producto existente en BD
            new_data: Nuevos datos del producto
            
        Returns:
            True si hay cambios significativos
        """
        # Campos críticos para comparar
        critical_fields = [
            'nombre', 'precio_venta', 'costo_aproximado',
            'existencias_totales', 'activo', 'vendible',
            'descripcion', 'codigo_barra'
        ]
        
        for field in critical_fields:
            if field not in new_data:
                continue
                
            existing_value = getattr(existing, field, None)
            new_value = new_data[field]
            
            # Comparación especial para Decimals
            if isinstance(existing_value, Decimal) and isinstance(new_value, Decimal):
                if abs(existing_value - new_value) > Decimal('0.01'):
                    logger.debug(f"Cambio en {field}: {existing_value} -> {new_value}")
                    return True
            elif existing_value != new_value:
                logger.debug(f"Cambio en {field}: {existing_value} -> {new_value}")
                return True
        
        return False
    
    def _apply_filters(
        self, 
        products: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Aplicar filtros a lista de productos
        
        Args:
            products: Lista de productos
            filters: Filtros a aplicar
            
        Returns:
            Lista filtrada
        """
        filtered = products
        
        if filters.get('activo') is not None:
            filtered = [p for p in filtered if p.get('activo') == filters['activo']]
        if filters.get('vendible') is not None:
            filtered = [p for p in filtered if p.get('vendible') == filters['vendible']]
        if filters.get('visualizableWeb') is not None:
            filtered = [p for p in filtered if p.get('visualizableWeb') == filters['visualizableWeb']]
        
        return filtered
    
    def get_last_successful_sync(self) -> Optional[ProductSyncLog]:
        """
        Obtener última sincronización exitosa
        
        Returns:
            ProductSyncLog o None
        """
        return self.db.query(ProductSyncLog).filter(
            ProductSyncLog.status.in_(['SUCCESS', 'PARTIAL_SUCCESS'])
        ).order_by(
            desc(ProductSyncLog.sync_date)
        ).first()
    
    def filter_products_by_date(
        self,
        products: List[Dict[str, Any]],
        since_date: datetime
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Filtrar productos modificados después de una fecha
        
        Args:
            products: Lista de productos
            since_date: Fecha desde la cual filtrar
            
        Returns:
            Tupla (productos_filtrados, productos_descartados)
        """
        filtered = []
        discarded = 0
        
        # Normalizar since_date para comparaciones seguras
        since_date_normalized = normalize_datetime(since_date)
        
        for product in products:
            product_date = self._extract_product_date(product)
            
            if product_date is None:
                # Si no tiene fecha, incluirlo por seguridad
                filtered.append(product)
            else:
                # Normalizar product_date para comparación segura
                product_date_normalized = normalize_datetime(product_date)
                
                if product_date_normalized >= since_date_normalized:
                    # Producto modificado después de la fecha
                    filtered.append(product)
                else:
                    # Producto sin cambios
                    discarded += 1
        
        logger.info(
            f"Filtrado por fecha: {len(filtered)} productos modificados, "
            f"{discarded} sin cambios desde {since_date.isoformat()}"
        )
        
        return filtered, discarded
    
    def map_dynamia_to_local(self, dynamia_item: Dict[str, Any]) -> Dict[str, Any]:
        """Mapear item de DynamiaERP a modelo local"""
        
        def safe_decimal(value, default=0):
            """Convertir a Decimal de forma segura"""
            if value is None:
                return Decimal(str(default))
            try:
                return Decimal(str(value))
            except:
                return Decimal(str(default))
        
        def safe_get(obj, key, default=None):
            """Obtener valor de forma segura"""
            if isinstance(obj, dict):
                return obj.get(key, default)
            return default
        
        # Extraer objetos anidados
        tipo = dynamia_item.get('tipo', {})
        marca = dynamia_item.get('marca', {})
        linea = dynamia_item.get('lineaPrincipal', {})
        
        return {
            # IDs
            'dynamia_id': dynamia_item.get('id'),
            'account_id': dynamia_item.get('accountId', self.account_id),
            
            # Información básica
            'codigo': dynamia_item.get('codigo', ''),
            'nombre': dynamia_item.get('nombre', ''),
            'referencia': dynamia_item.get('referencia', ''),
            'descripcion': dynamia_item.get('descripcion', ''),
            'codigo_barra': dynamia_item.get('codigoBarra', ''),
            'codigo_referencia': dynamia_item.get('codigoReferencia', ''),
            'codigo_lector': dynamia_item.get('codigoLector', ''),
            'external_ref': dynamia_item.get('externalRef', ''),
            
            # Precios y costos
            'precio_venta': safe_decimal(dynamia_item.get('precioVenta')),
            'costo_aproximado': safe_decimal(dynamia_item.get('costoAproximado')),
            'costo_efectivo': safe_decimal(dynamia_item.get('costoEfectivo')),
            'precio_fijo': dynamia_item.get('precioFijo', False),
            'precio_venta_calculado': dynamia_item.get('precioVentaCalculado', False),
            'tiene_precio_temp': dynamia_item.get('tienePrecioTemp', False),
            'usar_precio_sucursales': dynamia_item.get('usarPrecioSucursales', False),
            
            # Impuestos
            'impuesto_incluido': dynamia_item.get('impuestoIncluido', False),
            'porcentaje_impuesto': safe_decimal(dynamia_item.get('porcentajeImpuesto')),
            'exento_impuestos': dynamia_item.get('exentoImpuestos', False),
            'impuesto_fijo': safe_decimal(dynamia_item.get('impuestoFijo')),
            
            # Inventario
            'existencias_totales': safe_decimal(dynamia_item.get('existenciasTotales')),
            'existencias_minimas': safe_decimal(dynamia_item.get('existenciasMinimas')),
            'existencias_maximas': safe_decimal(dynamia_item.get('existenciasMaximas')),
            'existencias_externas': safe_decimal(dynamia_item.get('existenciasExternas')),
            
            # Clasificación - Tipo
            'tipo_id': safe_get(tipo, 'id'),
            'tipo_nombre': safe_get(tipo, 'name'),
            'tipo_class': safe_get(tipo, 'class'),
            
            # Clasificación - Marca
            'marca_id': safe_get(marca, 'id'),
            'marca_nombre': safe_get(marca, 'name'),
            'marca_class': safe_get(marca, 'class'),
            
            # Clasificación - Línea
            'linea_id': safe_get(linea, 'id'),
            'linea_nombre': safe_get(linea, 'name'),
            'linea_class': safe_get(linea, 'class'),
            
            # Estados
            'activo': dynamia_item.get('activo', True),
            'vendible': dynamia_item.get('vendible', True),
            'comprable': dynamia_item.get('comprable', True),
            'trasladable': dynamia_item.get('trasladable', True),
            'visualizable_web': dynamia_item.get('visualizableWeb', True),
            'destacado': dynamia_item.get('destacado', False),
            'permite_pedidos': dynamia_item.get('permitePedidos', False),
            
            # Configuración de ventas
            'cantidad_en_ventas': safe_decimal(dynamia_item.get('cantidadEnVentas', 1)),
            'cantidad_manual': dynamia_item.get('cantidadManual', False),
            'orden_en_ventas': dynamia_item.get('ordenEnVentas', 0),
            'permite_descuentos': dynamia_item.get('permiteDescuentos', True),
            'bloquear_descuentos': dynamia_item.get('bloquearDescuentos', False),
            'porcentaje_descuento': safe_decimal(dynamia_item.get('porcentajeDescuento')),
            'modo_precio': dynamia_item.get('modoPrecio', 'POR_DEFECTO'),
            
            # Domicilios y delivery
            'domicilios': dynamia_item.get('domicilios', True),
            'para_llevar': dynamia_item.get('paraLlevar', True),
            'bebida_alcoholica': dynamia_item.get('bebidaAlcoholica', False),
            'valor_envio': safe_decimal(dynamia_item.get('valorEnvio')),
            
            # Comisiones
            'comisionable': dynamia_item.get('comisionable', False),
            'descontar_en_comisiones': dynamia_item.get('descontarEnComisiones', False),
            'porcentaje_comision': safe_decimal(dynamia_item.get('porcentajeComision')),
            'total_comision_calculada': safe_decimal(dynamia_item.get('totalComisionCalculada')),
            
            # Configuraciones avanzadas
            'compuesto': dynamia_item.get('compuesto', False),
            'compuesto_dinamico': dynamia_item.get('compuestoDinamico', False),
            'multi_presentaciones': dynamia_item.get('multiPresentaciones', False),
            'presentaciones_obligatorias': dynamia_item.get('presentacionesObligatorias', False),
            'usa_seriales': dynamia_item.get('usaSeriales', False),
            'usar_balanza': dynamia_item.get('usarBalanza', False),
            'autolotes': dynamia_item.get('autolotes', False),
            'usar_en_transformaciones': dynamia_item.get('usarEnTransformaciones', False),
            'usar_preguntas_obligatorias': dynamia_item.get('usarPreguntasObligatorias', False),
            'nombre_generado': dynamia_item.get('nombreGenerado', False),
            'autocreado_proveedor': dynamia_item.get('autocreadoProveedor', False),
            
            # Gestión
            'porcentaje_pmg': safe_decimal(dynamia_item.get('porcentajePMG')),
            'porcentaje_admin': safe_decimal(dynamia_item.get('porcentajeAdmin')),
            'porcentaje_utilidad': safe_decimal(dynamia_item.get('porcentajeUtilidad')),
            'porcentaje_imprevisto': safe_decimal(dynamia_item.get('porcentajeImprevisto')),
            'valor_admin': safe_decimal(dynamia_item.get('valorAdmin')),
            'valor_utilidad': safe_decimal(dynamia_item.get('valorUtilidad')),
            'valor_imprevisto': safe_decimal(dynamia_item.get('valorImprevisto')),
            
            # Datos adicionales
            'subitems': dynamia_item.get('subitems', []),
            'preguntas_obligatorias': dynamia_item.get('preguntasObligatorias', []),
            'metadata_adicional': {
                'nombreLinea': dynamia_item.get('nombreLinea'),
                'usaAUI': dynamia_item.get('usaAUI'),
            },
            
            # Auditoría DynamiaERP
            'dynamia_creator': dynamia_item.get('creator'),
            'dynamia_creation_date': dynamia_item.get('creationDate'),
            'dynamia_creation_time': dynamia_item.get('creationTime'),
            'dynamia_creation_timestamp': dynamia_item.get('creationTimestamp'),
            'dynamia_last_update': dynamia_item.get('lastUpdate'),
            'dynamia_creation_instant': dynamia_item.get('creationInstant'),
            'dynamia_last_update_instant': dynamia_item.get('lastUpdateInstant'),
            
            # Auditoría local
            'fecha_sincronizacion': datetime.now(),
            'ultima_sincronizacion': datetime.now(),
            'sincronizado': True,
        }
    
    def sync_products(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        force_full: bool = False
    ) -> Dict[str, Any]:
        """
        Sincronizar productos desde DynamiaERP
        
        Soporta dos modos:
        - INCREMENTAL: Solo productos modificados (por defecto)
        - FULL: Todos los productos (si force_full=True o es primera vez)
        
        Args:
            filters: Filtros opcionales (activo, vendible, etc.)
            force_full: Forzar sincronización completa
            
        Returns:
            Diccionario con resultados de la sincronización
        """
        start_time = datetime.now()
        
        # Determinar tipo de sincronización
        sync_type = 'FULL'
        since_date = None
        
        if not force_full:
            # Intentar sincronización incremental
            last_sync = self.get_last_successful_sync()
            
            if last_sync and last_sync.sync_date:
                # Usar sincronización incremental
                # Restar 5 minutos para evitar perder productos en el límite
                since_date = last_sync.sync_date - timedelta(minutes=5)
                sync_type = 'INCREMENTAL'
                logger.info(
                    f"Sincronización incremental desde {since_date.isoformat()}"
                )
            else:
                logger.info("Primera sincronización - descarga completa")
        else:
            logger.info("Sincronización completa forzada")
        
        # Crear log de sincronización
        sync_log = ProductSyncLog(
            sync_date=start_time,
            status='IN_PROGRESS',
            sync_type=sync_type
        )
        
        try:
            # Obtener productos de DynamiaERP
            logger.info(f"Iniciando sincronización {sync_type}...")
            dynamia_products = self.fetch_all_products_from_dynamia()
            
            total_downloaded = len(dynamia_products)
            products_to_process = dynamia_products
            skipped_count = 0
            
            # Si es incremental, filtrar por fecha
            if sync_type == 'INCREMENTAL' and since_date:
                products_to_process, skipped_count = self.filter_products_by_date(
                    dynamia_products, 
                    since_date
                )
                logger.info(
                    f"Sincronización incremental: {len(products_to_process)} productos "
                    f"a procesar, {skipped_count} sin cambios"
                )
            
            # Aplicar filtros adicionales si existen
            if filters:
                products_to_process = self._apply_filters(products_to_process, filters)
                logger.info(f"Después de filtros: {len(products_to_process)} productos")
            
            # Procesar productos
            new_count = 0
            updated_count = 0
            unchanged_count = 0
            error_count = 0
            latest_product_date = None
            
            for dynamia_item in products_to_process:
                try:
                    # Rastrear fecha más reciente
                    item_date = self._extract_product_date(dynamia_item)
                    if item_date and (not latest_product_date or item_date > latest_product_date):
                        latest_product_date = item_date
                    
                    # Mapear datos
                    product_data = self.map_dynamia_to_local(dynamia_item)
                    
                    # Buscar si ya existe
                    existing = self.db.query(Product).filter(
                        Product.dynamia_id == product_data['dynamia_id']
                    ).first()
                    
                    if existing:
                        # Verificar si hay cambios significativos
                        if self._has_significant_changes(existing, product_data):
                            # Actualizar solo si hay cambios
                            for key, value in product_data.items():
                                setattr(existing, key, value)
                            updated_count += 1
                        else:
                            # Sin cambios significativos
                            unchanged_count += 1
                    else:
                        # Crear nuevo
                        new_product = Product(**product_data)
                        self.db.add(new_product)
                        new_count += 1
                    
                    # Commit cada 100 productos para evitar transacciones muy largas
                    if (new_count + updated_count) % 100 == 0:
                        self.db.commit()
                        logger.info(
                            f"Procesados {new_count + updated_count} productos "
                            f"({new_count} nuevos, {updated_count} actualizados)..."
                        )
                        
                except Exception as e:
                    logger.error(f"Error procesando producto {dynamia_item.get('id')}: {e}")
                    error_count += 1
                    continue
            
            # Commit final
            self.db.commit()
            
            # Calcular duración
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Actualizar log
            sync_log.total_products = total_downloaded
            sync_log.new_products = new_count
            sync_log.updated_products = updated_count
            sync_log.errors = error_count
            sync_log.duration_seconds = Decimal(str(duration))
            sync_log.status = 'SUCCESS' if error_count == 0 else 'PARTIAL_SUCCESS'
            sync_log.last_product_date = latest_product_date
            sync_log.details = {
                'sync_type': sync_type,
                'since_date': since_date.isoformat() if since_date else None,
                'total_downloaded': total_downloaded,
                'products_processed': len(products_to_process),
                'products_skipped': skipped_count,
                'products_unchanged': unchanged_count,
                'filters': filters,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            self.db.add(sync_log)
            self.db.commit()
            
            result = {
                'success': True,
                'sync_type': sync_type,
                'total_downloaded': total_downloaded,
                'products_processed': len(products_to_process),
                'products_skipped': skipped_count,
                'new': new_count,
                'updated': updated_count,
                'unchanged': unchanged_count,
                'errors': error_count,
                'duration_seconds': duration,
                'sync_log_id': sync_log.id,
                'efficiency_gain': f"{(skipped_count / total_downloaded * 100):.1f}%" if total_downloaded > 0 else "0%"
            }
            
            logger.info(
                f"Sincronización {sync_type} completada: "
                f"{new_count} nuevos, {updated_count} actualizados, "
                f"{unchanged_count} sin cambios, {skipped_count} omitidos, "
                f"{error_count} errores en {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            self.db.rollback()
            
            # Registrar error en log
            sync_log.status = 'ERROR'
            sync_log.error_message = str(e)
            sync_log.duration_seconds = Decimal(str((datetime.now() - start_time).total_seconds()))
            self.db.add(sync_log)
            self.db.commit()
            
            logger.error(f"Error en sincronización: {e}")
            return {
                'success': False,
                'sync_type': sync_type,
                'error': str(e),
                'sync_log_id': sync_log.id
            }
    
    def sync_products_legacy(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sincronizar productos desde DynamiaERP (método legacy - sincronización completa)
        
        DEPRECADO: Usar sync_products() con force_full=True en su lugar
        
        Args:
            filters: Filtros opcionales (activo, vendible, etc.)
            
        Returns:
            Diccionario con resultados de la sincronización
        """
        logger.warning("Usando método legacy sync_products_legacy - considerar migrar a sync_products()")
        return self.sync_products(filters=filters, force_full=True)
