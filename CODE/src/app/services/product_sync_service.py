"""
Servicio de sincronización de productos desde DynamiaERP
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.product import Product, ProductSyncLog
import os

logger = logging.getLogger(__name__)


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
        """Obtener todos los productos de DynamiaERP"""
        try:
            response = requests.get(
                f"{self.base_url}/api/inventario/items",
                headers=self.get_headers(),
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('data', [])
            
            logger.info(f"Obtenidos {len(items)} productos de DynamiaERP")
            return items
            
        except Exception as e:
            logger.error(f"Error obteniendo productos de DynamiaERP: {e}")
            raise
    
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
    
    def sync_products(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sincronizar productos desde DynamiaERP
        
        Args:
            filters: Filtros opcionales (activo, vendible, etc.)
            
        Returns:
            Diccionario con resultados de la sincronización
        """
        start_time = datetime.now()
        sync_log = ProductSyncLog(
            sync_date=start_time,
            status='IN_PROGRESS'
        )
        
        try:
            # Obtener productos de DynamiaERP
            logger.info("Iniciando sincronización de productos...")
            dynamia_products = self.fetch_all_products_from_dynamia()
            
            # Aplicar filtros si existen
            if filters:
                if filters.get('activo') is not None:
                    dynamia_products = [p for p in dynamia_products if p.get('activo') == filters['activo']]
                if filters.get('vendible') is not None:
                    dynamia_products = [p for p in dynamia_products if p.get('vendible') == filters['vendible']]
                if filters.get('visualizableWeb') is not None:
                    dynamia_products = [p for p in dynamia_products if p.get('visualizableWeb') == filters['visualizableWeb']]
            
            new_count = 0
            updated_count = 0
            error_count = 0
            
            for dynamia_item in dynamia_products:
                try:
                    # Mapear datos
                    product_data = self.map_dynamia_to_local(dynamia_item)
                    
                    # Buscar si ya existe
                    existing = self.db.query(Product).filter(
                        Product.dynamia_id == product_data['dynamia_id']
                    ).first()
                    
                    if existing:
                        # Actualizar
                        for key, value in product_data.items():
                            setattr(existing, key, value)
                        updated_count += 1
                    else:
                        # Crear nuevo
                        new_product = Product(**product_data)
                        self.db.add(new_product)
                        new_count += 1
                    
                    # Commit cada 100 productos para evitar transacciones muy largas
                    if (new_count + updated_count) % 100 == 0:
                        self.db.commit()
                        logger.info(f"Procesados {new_count + updated_count} productos...")
                        
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
            sync_log.total_products = len(dynamia_products)
            sync_log.new_products = new_count
            sync_log.updated_products = updated_count
            sync_log.errors = error_count
            sync_log.duration_seconds = Decimal(str(duration))
            sync_log.status = 'SUCCESS' if error_count == 0 else 'PARTIAL_SUCCESS'
            sync_log.details = {
                'filters': filters,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            self.db.add(sync_log)
            self.db.commit()
            
            result = {
                'success': True,
                'total': len(dynamia_products),
                'new': new_count,
                'updated': updated_count,
                'errors': error_count,
                'duration_seconds': duration,
                'sync_log_id': sync_log.id
            }
            
            logger.info(f"Sincronización completada: {result}")
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
                'error': str(e),
                'sync_log_id': sync_log.id
            }
