# 🔮 Futuro: Preferencias de Notificaciones para Clientes

## 📊 Situación Actual

**Actualmente, solo USUARIOS REGISTRADOS tienen preferencias:**

```
User (admin, operadores)
  ↓ tiene
UserPreferences (puede controlar notificaciones)
  ↓ accede a
/settings (interfaz de configuración)
```

**Los CLIENTES NO tienen preferencias:**

```
Customer (personas que reciben paquetes)
  ↓ NO tiene
user_id (no tiene cuenta)
  ↓ NO puede
Controlar notificaciones
```

**Resultado:** Los clientes reciben TODAS las notificaciones de sus paquetes.

---

## 💡 Opciones para el Futuro

### **Opción 1: Portal de Cliente con Cuenta Opcional** ⭐ (Recomendado)

Permitir que los clientes creen una cuenta opcional para gestionar sus preferencias.

#### **Implementación:**

```python
# 1. Agregar user_id opcional a Customer
class Customer(Base):
    # ... campos existentes ...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ← Nuevo
    user = relationship("User", backref="customer_profile")
```

#### **Flujo:**

```
1. Cliente recibe paquete
   ↓
2. Recibe SMS/Email con link: "Crea tu cuenta para gestionar notificaciones"
   ↓
3. Cliente crea cuenta (opcional)
   ↓
4. Se vincula Customer.user_id = User.id
   ↓
5. Cliente accede a /settings
   ↓
6. Puede controlar sus notificaciones
```

#### **Ventajas:**
- ✅ Clientes pueden controlar notificaciones
- ✅ Clientes pueden ver historial de paquetes
- ✅ Clientes pueden rastrear paquetes
- ✅ Mejor experiencia de usuario
- ✅ Cumplimiento legal (GDPR, CCPA)

#### **Desventajas:**
- ⚠️ Requiere desarrollo de portal de cliente
- ⚠️ Requiere sistema de registro/login
- ⚠️ Algunos clientes no querrán crear cuenta

---

### **Opción 2: Preferencias por Token (Sin Cuenta)**

Permitir que los clientes gestionen preferencias sin crear cuenta, usando un token único.

#### **Implementación:**

```python
# Nueva tabla
class CustomerPreferences(Base):
    __tablename__ = "customer_preferences"
    
    customer_id = Column(UUID, ForeignKey("customers.id"), unique=True)
    token = Column(String(64), unique=True, index=True)  # Token único
    
    sms_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    notify_package_received = Column(Boolean, default=True)
    notify_package_delivered = Column(Boolean, default=True)
    
    customer = relationship("Customer", backref="preferences")
```

#### **Flujo:**

```
1. Cliente recibe SMS/Email
   ↓
2. Incluye link: "Gestionar preferencias"
   ↓
3. Link contiene token único: /preferences?token=abc123xyz
   ↓
4. Cliente accede sin login
   ↓
5. Puede activar/desactivar notificaciones
   ↓
6. Cambios se guardan en CustomerPreferences
```

#### **Ventajas:**
- ✅ No requiere cuenta
- ✅ Fácil de implementar
- ✅ Cumplimiento legal
- ✅ Bajo fricción para el cliente

#### **Desventajas:**
- ⚠️ Token puede perderse
- ⚠️ Menos seguro que cuenta con password
- ⚠️ No permite otras funcionalidades (historial, tracking)

---

### **Opción 3: Link de "Dar de Baja" en Notificaciones**

Opción mínima: solo permitir desactivar notificaciones, no activarlas.

#### **Implementación:**

```python
# Agregar a Customer
class Customer(Base):
    # ... campos existentes ...
    unsubscribe_token = Column(String(64), unique=True, index=True)
    sms_unsubscribed = Column(Boolean, default=False)
    email_unsubscribed = Column(Boolean, default=False)
```

#### **Flujo:**

```
1. Cliente recibe SMS/Email
   ↓
2. Incluye link: "Dejar de recibir notificaciones"
   ↓
3. Link: /unsubscribe?token=abc123&type=sms
   ↓
4. Cliente hace clic
   ↓
5. Se marca Customer.sms_unsubscribed = True
   ↓
6. Ya no recibe SMS (solo emails)
```

#### **Ventajas:**
- ✅ Muy fácil de implementar
- ✅ Cumplimiento legal básico
- ✅ No requiere cuenta ni interfaz compleja

#### **Desventajas:**
- ⚠️ Solo permite desactivar, no reactivar
- ⚠️ Experiencia limitada
- ⚠️ Cliente debe contactar soporte para reactivar

---

## 🎯 Recomendación

### **Corto Plazo (Ahora):**
Dejar como está. Los clientes reciben todas las notificaciones importantes.

### **Mediano Plazo (3-6 meses):**
Implementar **Opción 3** (Link de dar de baja):
- Fácil de implementar
- Cumplimiento legal básico
- Bajo impacto en el sistema

### **Largo Plazo (6-12 meses):**
Implementar **Opción 1** (Portal de cliente):
- Mejor experiencia
- Más funcionalidades
- Diferenciador competitivo

---

## 📋 Implementación de Opción 1 (Portal de Cliente)

### **Paso 1: Agregar user_id a Customer**

```sql
-- Migración
ALTER TABLE customers 
ADD COLUMN user_id INTEGER REFERENCES users(id);

CREATE INDEX idx_customers_user_id ON customers(user_id);
```

```python
# Modelo
class Customer(Base):
    # ... campos existentes ...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="customer_profile")
```

### **Paso 2: Crear endpoint de registro para clientes**

```python
@router.post("/api/customer/register")
async def register_customer_account(
    customer_id: UUID,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Permite a un cliente crear cuenta para gestionar preferencias"""
    
    # Verificar que el cliente existe
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Cliente no encontrado")
    
    # Verificar que no tenga cuenta ya
    if customer.user_id:
        raise HTTPException(400, "Cliente ya tiene cuenta")
    
    # Crear usuario
    user = User(
        username=email,
        email=email,
        full_name=customer.full_name,
        role=UserRole.USUARIO,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.flush()
    
    # Vincular customer con user
    customer.user_id = user.id
    
    # Crear preferencias por defecto
    prefs = UserPreferences(user_id=user.id)
    db.add(prefs)
    
    db.commit()
    
    return {"success": True, "message": "Cuenta creada exitosamente"}
```

### **Paso 3: Modificar envío de notificaciones**

```python
# En sms_service.py
async def send_sms(self, ...):
    # Obtener user_id del customer
    if customer_id:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        user_id = customer.user_id if customer else None
    
    # Verificar preferencias si tiene user_id
    if user_id:
        # ... verificación de preferencias ...
```

### **Paso 4: Agregar link en notificaciones**

```python
# En templates de SMS/Email
message = f"""
PAQUETEX: Su paquete {tracking} ha sido recibido.

¿Quiere gestionar sus notificaciones?
Cree su cuenta: {base_url}/customer/register?id={customer_id}
"""
```

---

## 📊 Comparación de Opciones

| Característica | Opción 1 (Portal) | Opción 2 (Token) | Opción 3 (Dar de baja) |
|----------------|-------------------|------------------|------------------------|
| **Complejidad** | Alta | Media | Baja |
| **Tiempo desarrollo** | 2-4 semanas | 1-2 semanas | 2-3 días |
| **Experiencia usuario** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Seguridad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Funcionalidades** | Muchas | Limitadas | Mínimas |
| **Cumplimiento legal** | ✅ Completo | ✅ Completo | ✅ Básico |
| **Mantenimiento** | Alto | Medio | Bajo |

---

## 🚀 Roadmap Sugerido

### **Fase 1: Ahora (Implementado)**
- ✅ Preferencias para usuarios del sistema
- ✅ Clientes reciben todas las notificaciones

### **Fase 2: Próximos 3 meses**
- [ ] Implementar Opción 3 (Link de dar de baja)
- [ ] Agregar link en footer de SMS/Emails
- [ ] Página simple de unsubscribe

### **Fase 3: 6-12 meses**
- [ ] Implementar Opción 1 (Portal de cliente)
- [ ] Sistema de registro para clientes
- [ ] Dashboard de cliente
- [ ] Historial de paquetes
- [ ] Tracking en tiempo real

---

## 💬 Preguntas Frecuentes

### **¿Por qué los clientes no tienen preferencias ahora?**
Porque no tienen cuenta en el sistema. Solo tienen datos de contacto (email/teléfono).

### **¿Es legal enviar notificaciones sin consentimiento?**
Sí, si son notificaciones transaccionales (información de paquetes). No aplica para marketing.

### **¿Qué pasa si un cliente se queja de spam?**
Puedes desactivar manualmente sus notificaciones en la BD o implementar Opción 3.

### **¿Cuándo implementar portal de cliente?**
Cuando tengas suficientes clientes que lo soliciten o como diferenciador competitivo.

---

**Fecha:** 2025-01-24  
**Versión:** PAQUETEX v3.1  
**Estado:** 📝 Documento de planificación
