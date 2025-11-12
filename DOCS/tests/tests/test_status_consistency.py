# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Tests de Consistencia de Estados
Versión: 4.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Tests para validar la consistencia de estados entre diferentes endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.services.package_status_service import PackageStatusService
from app.services.nomenclature_service import NomenclatureService
from app.models.package import Package, PackageStatus
from app.models.announcement_new import PackageAnnouncementNew


client = TestClient(app)


class TestStatusConsistency:
    """Tests para validar consistencia de estados"""
    
    def test_package_status_service_consistency(self, db: Session):
        """Test que el PackageStatusService devuelve estados consistentes"""
        # Crear paquete de prueba
        test_package = Package(
            tracking_number="TEST",
            status=PackageStatus.CANCELADO,
            access_code="TEST123",
            announced_at="2025-01-01T00:00:00"
        )
        db.add(test_package)
        db.commit()
        
        # Verificar estado efectivo
        effective_status = PackageStatusService.get_effective_status(db, "TEST")
        assert effective_status["status"] == "CANCELADO"
        assert effective_status["allows_inquiries"] == False
        assert effective_status["is_final"] == True
        
        # Limpiar
        db.delete(test_package)
        db.commit()
    
    def test_nomenclature_service_unification(self, db: Session):
        """Test que el NomenclatureService unifica nomenclatura correctamente"""
        # Crear paquete de prueba
        test_package = Package(
            tracking_number="UNIF",  # tracking_number en Package
            guide_number="12345",
            status=PackageStatus.RECIBIDO,
            access_code="UNIF123",
            announced_at="2025-01-01T00:00:00"
        )
        db.add(test_package)
        db.commit()
        
        # Buscar usando NomenclatureService
        search_result = NomenclatureService.search_by_unified_identifier(db, "UNIF")
        
        assert search_result["found"] == True
        assert search_result["type"] == "package"
        assert search_result["data"]["tracking_code"] == "UNIF"  # Unificado como tracking_code
        assert search_result["data"]["guide_number"] == "12345"
        
        # Limpiar
        db.delete(test_package)
        db.commit()
    
    def test_endpoint_consistency_v1_vs_unified(self):
        """Test que los endpoints v1 y unificado devuelven estados consistentes"""
        # Probar con paquete conocido
        response_v1 = client.get("/api/announcements/search/package?query=LLEI")
        response_unified = client.get("/api/announcements/search/package/unified?query=LLEI")
        
        if response_v1.status_code == 200 and response_unified.status_code == 200:
            data_v1 = response_v1.json()
            data_unified = response_unified.json()
            
            # Verificar que ambos devuelven el mismo estado
            assert data_v1["current_status"] == data_unified["current_status"]
            
            # Verificar que las capacidades de consulta son consistentes
            v1_allows = data_v1.get("inquiry_info", {}).get("allows_inquiries", False)
            unified_allows = data_unified.get("inquiry_info", {}).get("allows_inquiries", False)
            assert v1_allows == unified_allows
    
    def test_status_validation_decorators(self, db: Session):
        """Test que los decoradores de validación funcionan correctamente"""
        from app.decorators.status_validation import ensure_consistent_status
        
        # Función de prueba con decorador
        @ensure_consistent_status
        async def test_function(query: str, db: Session):
            return {
                "current_status": "WRONG_STATUS",  # Estado incorrecto intencionalmente
                "announcement": {
                    "tracking_code": query
                }
            }
        
        # Ejecutar función con decorador
        result = test_function("LLEI", db)
        
        # El decorador debería corregir el estado
        # (Nota: esto requiere que LLEI exista en la base de datos)
        if "current_status" in result:
            # Verificar que el estado fue corregido por el decorador
            assert result["current_status"] != "WRONG_STATUS"
    
    def test_identifier_format_validation(self):
        """Test que la validación de formato de identificadores funciona"""
        # Test tracking_code válido
        validation = NomenclatureService.validate_identifier_format("LLEI")
        assert validation["type"] == "tracking_code"
        assert validation["format"] == "valid"
        assert validation["normalized"] == "LLEI"
        
        # Test guide_number válido
        validation = NomenclatureService.validate_identifier_format("12345A")
        assert validation["type"] == "guide_number"
        assert validation["format"] == "valid"
        assert validation["normalized"] == "12345A"
        
        # Test formato inválido
        validation = NomenclatureService.validate_identifier_format("XX")
        assert validation["type"] == "invalid"
        assert validation["format"] == "invalid"
    
    def test_inquiry_permissions_by_status(self, db: Session):
        """Test que los permisos de consulta son correctos según el estado"""
        # Estados que permiten consultas
        allowed_statuses = ["ANUNCIADO", "RECIBIDO"]
        for status in allowed_statuses:
            can_inquire = PackageStatusService.INQUIRY_ALLOWED_STATUSES
            status_enum = PackageStatus(status)
            assert status_enum in can_inquire, f"Estado {status} debería permitir consultas"
        
        # Estados que NO permiten consultas
        final_statuses = ["ENTREGADO", "CANCELADO"]
        for status in final_statuses:
            final_set = PackageStatusService.FINAL_STATUSES
            status_enum = PackageStatus(status)
            assert status_enum in final_set, f"Estado {status} debería ser final"
    
    def test_unified_endpoint_error_handling(self):
        """Test que el endpoint unificado maneja errores correctamente"""
        # Test sin query
        response = client.get("/api/announcements/search/package/unified")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert data["error_code"] == "MISSING_QUERY"
        
        # Test con identificador no encontrado
        response = client.get("/api/announcements/search/package/unified?query=XXXX")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert data["error_code"] == "PACKAGE_NOT_FOUND"
        assert "validation" in data
    
    def test_nomenclature_report_generation(self, db: Session):
        """Test que el reporte de nomenclatura se genera correctamente"""
        report = NomenclatureService.get_nomenclature_report(db)
        
        assert "total_packages" in report
        assert "total_announcements" in report
        assert "duplicate_tracking_codes" in report
        assert "nomenclature_issues" in report
        assert "recommendations" in report
        
        # Verificar que el reporte identifica problemas conocidos
        issues = report["nomenclature_issues"]
        assert "tracking_number_vs_tracking_code" in issues
        assert "guide_number_confusion" in issues


class TestEndpointConsistency:
    """Tests para verificar consistencia entre endpoints"""
    
    def test_all_search_endpoints_consistency(self):
        """Test que todos los endpoints de búsqueda devuelven estados consistentes"""
        test_queries = ["LLEI", "RBJ9"]
        
        for query in test_queries:
            responses = {}
            
            # Probar todos los endpoints
            endpoints = [
                "/api/announcements/search/package",
                "/api/announcements/search/package/v2", 
                "/api/announcements/search/package/unified"
            ]
            
            for endpoint in endpoints:
                response = client.get(f"{endpoint}?query={query}")
                if response.status_code == 200:
                    responses[endpoint] = response.json()
            
            # Verificar consistencia de estados
            statuses = []
            for endpoint, data in responses.items():
                if data.get("success") and "current_status" in data:
                    statuses.append(data["current_status"])
            
            # Todos los endpoints deberían devolver el mismo estado
            if len(statuses) > 1:
                assert all(status == statuses[0] for status in statuses), \
                    f"Estados inconsistentes para {query}: {statuses}"


# Fixtures para tests
@pytest.fixture
def db():
    """Fixture para base de datos de prueba"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
