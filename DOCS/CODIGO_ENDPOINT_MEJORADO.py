# ========================================
# ENDPOINT MEJORADO: Buscar Cliente con Paquetes Anunciados
# ========================================
# 
# Este código debe agregarse/reemplazar en:
# CODE/src/app/routes/public.py
#
# Línea aproximada: 1690
# ========================================

@router.get("/api/customers/search-by-phone")
async def search_customer_by_phone_public(
    phone: str,
    db: Session = Depends(get_db)
):
    """
    Buscar cliente por teléfono - Incluye códigos de consulta de paquetes anunciados
    
    Endpoint público para la vista /announce-papyrus
    
    Returns:
        - Información básica del cliente
        - Lista de códigos de consulta de paquetes anunciados (solo tracking_code)
        - Total de paquetes anunciados
    """
    try:
        from app.utils.phone_utils import normalize_phone
        from app.services.customer_service import CustomerService
        
        # Normalizar teléfono
        normalized_phone = normalize_phone(phone)
        
        # Buscar cliente
        customer_service = CustomerService()
        customer = customer_service.get_customer_by_phone(db, normalized_phone)
        
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"detail": "Cliente no encontrado"}
            )
        
        # ========================================
        # 🆕 BUSCAR PAQUETES ANUNCIADOS
        # ========================================
        announced_packages = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.customer_id == customer.id,
            PackageAnnouncementNew.is_processed == False,
            PackageAnnouncementNew.is_active == True
        ).order_by(PackageAnnouncementNew.announced_at.desc()).all()
        
        # Formatear solo los códigos de consulta (tracking_code)
        announced_codes = []
        for pkg in announced_packages:
            announced_codes.append({
                "tracking_code": pkg.tracking_code,
                "guide_number": pkg.guide_number  # Solo para referencia interna
            })
        
        # Log para debugging
        logger.info(f"Cliente {customer.id} tiene {len(announced_codes)} paquetes anunciados")
        
        # ========================================
        # RESPUESTA CON CÓDIGOS DE CONSULTA
        # ========================================
        return {
            # Datos básicos del cliente
            "id": str(customer.id),
            "full_name": customer.full_name,
            "display_name": customer.display_name,
            "phone": customer.phone,
            "email": customer.email,
            "is_vip": customer.is_vip,
            "total_packages_received": customer.total_packages_received,
            
            # 🆕 CÓDIGOS DE CONSULTA DE PAQUETES ANUNCIADOS
            "announced_codes": announced_codes,
            "total_announced": len(announced_codes),
            "has_announced_packages": len(announced_codes) > 0
        }
        
    except Exception as e:
        logger.error(f"Error buscando cliente por teléfono: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error al buscar cliente: {str(e)}"}
        )

