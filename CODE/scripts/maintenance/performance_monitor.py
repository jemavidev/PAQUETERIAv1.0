#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Monitor de Rendimiento
Versión: 1.0.0
Fecha: 2025-11-17
Autor: Equipo de Desarrollo
"""

import time
import psutil
import requests
import json
from datetime import datetime
from typing import Dict, List
import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.append('/app/src')

from app.database_optimized import get_db_pool_status, SessionLocal
from app.cache_manager import cache_manager
from sqlalchemy import text

class PerformanceMonitor:
    """Monitor de rendimiento para la aplicación"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.endpoints_to_test = [
            "/api/packages/",
            "/api/customers/",
            "/api/notifications/",
            "/health"
        ]
    
    def test_endpoint_performance(self, endpoint: str, iterations: int = 5) -> Dict:
        """Probar el rendimiento de un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        times = []
        errors = 0
        
        print(f"🧪 Probando {endpoint}...")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=30)
                end_time = time.time()
                
                response_time = end_time - start_time
                times.append(response_time)
                
                if response.status_code != 200:
                    errors += 1
                    print(f"  ❌ Error {response.status_code} en iteración {i+1}")
                else:
                    print(f"  ✅ Iteración {i+1}: {response_time:.3f}s")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Error en iteración {i+1}: {str(e)}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
        else:
            avg_time = min_time = max_time = 0
        
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "errors": errors,
            "success_rate": ((iterations - errors) / iterations) * 100,
            "avg_response_time": avg_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "all_times": times
        }
    
    def get_system_metrics(self) -> Dict:
        """Obtener métricas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_percent": (disk.used / disk.total) * 100
            }
        except Exception as e:
            return {"error": f"Error obteniendo métricas del sistema: {e}"}
    
    def get_database_metrics(self) -> Dict:
        """Obtener métricas de la base de datos"""
        try:
            pool_status = get_db_pool_status()
            
            # Obtener estadísticas de queries
            db = SessionLocal()
            try:
                # Conexiones activas
                result = db.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                active_connections = result.scalar()
                
                # Tamaño de la base de datos
                result = db.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
                db_size = result.scalar()
                
                # Estadísticas de tablas principales
                result = db.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples
                    FROM pg_stat_user_tables 
                    WHERE tablename IN ('packages', 'customers', 'messages')
                    ORDER BY n_live_tup DESC
                """))
                table_stats = [dict(row._mapping) for row in result]
                
            finally:
                db.close()
            
            return {
                "pool_status": pool_status,
                "active_connections": active_connections,
                "database_size": db_size,
                "table_statistics": table_stats
            }
        except Exception as e:
            return {"error": f"Error obteniendo métricas de BD: {e}"}
    
    def get_cache_metrics(self) -> Dict:
        """Obtener métricas del caché"""
        try:
            return cache_manager.get_cache_stats()
        except Exception as e:
            return {"error": f"Error obteniendo métricas de caché: {e}"}
    
    def run_full_performance_test(self) -> Dict:
        """Ejecutar test completo de rendimiento"""
        print("🚀 Iniciando test completo de rendimiento...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Test de endpoints
        endpoint_results = []
        for endpoint in self.endpoints_to_test:
            result = self.test_endpoint_performance(endpoint)
            endpoint_results.append(result)
        
        # Métricas del sistema
        print("\n📊 Obteniendo métricas del sistema...")
        system_metrics = self.get_system_metrics()
        
        # Métricas de base de datos
        print("🗄️  Obteniendo métricas de base de datos...")
        db_metrics = self.get_database_metrics()
        
        # Métricas de caché
        print("💾 Obteniendo métricas de caché...")
        cache_metrics = self.get_cache_metrics()
        
        end_time = datetime.now()
        
        report = {
            "timestamp": start_time.isoformat(),
            "test_duration": (end_time - start_time).total_seconds(),
            "endpoint_performance": endpoint_results,
            "system_metrics": system_metrics,
            "database_metrics": db_metrics,
            "cache_metrics": cache_metrics
        }
        
        return report
    
    def print_performance_summary(self, report: Dict):
        """Imprimir resumen del rendimiento"""
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE RENDIMIENTO")
        print("=" * 60)
        
        # Resumen de endpoints
        print("\n🌐 RENDIMIENTO DE ENDPOINTS:")
        for result in report["endpoint_performance"]:
            status = "✅" if result["success_rate"] == 100 else "⚠️"
            print(f"  {status} {result['endpoint']}")
            print(f"     Tiempo promedio: {result['avg_response_time']:.3f}s")
            print(f"     Tasa de éxito: {result['success_rate']:.1f}%")
        
        # Métricas del sistema
        if "error" not in report["system_metrics"]:
            sys_metrics = report["system_metrics"]
            print(f"\n💻 SISTEMA:")
            print(f"  CPU: {sys_metrics['cpu_percent']:.1f}%")
            print(f"  Memoria: {sys_metrics['memory_percent']:.1f}%")
            print(f"  Disco: {sys_metrics['disk_percent']:.1f}%")
        
        # Métricas de base de datos
        if "error" not in report["database_metrics"]:
            db_metrics = report["database_metrics"]
            print(f"\n🗄️  BASE DE DATOS:")
            print(f"  Conexiones activas: {db_metrics['active_connections']}")
            print(f"  Tamaño BD: {db_metrics['database_size']}")
            if "pool_status" in db_metrics:
                pool = db_metrics["pool_status"]
                print(f"  Pool conexiones: {pool['checked_out']}/{pool['pool_size']}")
        
        # Métricas de caché
        if "error" not in report["cache_metrics"]:
            cache_metrics = report["cache_metrics"]
            print(f"\n💾 CACHÉ:")
            print(f"  Memoria usada: {cache_metrics.get('used_memory', 'N/A')}")
            print(f"  Tasa de aciertos: {cache_metrics.get('hit_rate', 0):.1f}%")
            print(f"  Claves totales: {cache_metrics.get('total_keys', 0)}")
        
        print("\n" + "=" * 60)
    
    def save_report(self, report: Dict, filename: str = None):
        """Guardar reporte en archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/app/logs/performance_report_{timestamp}.json"
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Reporte guardado en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")

def main():
    """Función principal"""
    monitor = PerformanceMonitor()
    
    # Ejecutar test completo
    report = monitor.run_full_performance_test()
    
    # Mostrar resumen
    monitor.print_performance_summary(report)
    
    # Guardar reporte
    monitor.save_report(report)
    
    # Recomendaciones basadas en los resultados
    print("\n💡 RECOMENDACIONES:")
    
    # Analizar tiempos de respuesta
    slow_endpoints = [r for r in report["endpoint_performance"] 
                     if r["avg_response_time"] > 2.0]
    
    if slow_endpoints:
        print("  ⚠️  Endpoints lentos detectados:")
        for endpoint in slow_endpoints:
            print(f"     - {endpoint['endpoint']}: {endpoint['avg_response_time']:.3f}s")
        print("     Considera optimizar estas consultas o agregar caché")
    
    # Analizar uso de recursos
    if "system_metrics" in report and "error" not in report["system_metrics"]:
        sys_metrics = report["system_metrics"]
        if sys_metrics["cpu_percent"] > 80:
            print("  ⚠️  Alto uso de CPU - considera aumentar recursos")
        if sys_metrics["memory_percent"] > 85:
            print("  ⚠️  Alto uso de memoria - considera aumentar RAM")
    
    # Analizar caché
    if "cache_metrics" in report and "error" not in report["cache_metrics"]:
        cache_metrics = report["cache_metrics"]
        hit_rate = cache_metrics.get("hit_rate", 0)
        if hit_rate < 50:
            print("  ⚠️  Baja tasa de aciertos en caché - revisa la estrategia de caché")

if __name__ == "__main__":
    main()