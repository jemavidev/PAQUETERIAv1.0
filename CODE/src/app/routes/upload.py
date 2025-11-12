from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import boto3
import json
from datetime import datetime
import os
from pathlib import Path
from app.dependencies import get_current_active_user_from_cookies
from app.models.user import UserRole

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BUCKET_NAME = os.getenv('AWS_S3_BUCKET', 'paquetes-el-club')

# Verificar si las credenciales de AWS están configuradas
USE_S3 = AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and not AWS_ACCESS_KEY_ID.startswith('your-')

# Inicializar S3 client solo si las credenciales están configuradas
s3_client = None
if USE_S3:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        print(f"✅ Cliente S3 inicializado correctamente para bucket: {BUCKET_NAME}")
    except Exception as e:
        print(f"⚠️ Error inicializando cliente S3: {str(e)}")
        USE_S3 = False

# Configuración de almacenamiento local (fallback)
LOCAL_STORAGE_PATH = Path("/app/uploads")
LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

print(f"📦 Modo de almacenamiento: {'AWS S3' if USE_S3 else 'Local (Fallback)'}")

@router.post("/s3")
async def upload_image_to_s3(
    request: Request,
    file: UploadFile = File(...),
    s3_key: str = Form(...),
    package_id: str = Form(...),
    package_type: str = Form(...),
    current_user = Depends(get_current_active_user_from_cookies)
):
    """
    Subir imagen a S3 o almacenamiento local (fallback)
    - Si AWS S3 está configurado, sube a S3
    - Si no, guarda localmente en /app/uploads/
    """
    try:
        # Verificar permisos (Admins y Operadores pueden subir imágenes)
        if current_user.role not in [UserRole.ADMIN, UserRole.OPERADOR]:
            raise HTTPException(status_code=403, detail="No tienes permisos para subir imágenes")
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        if USE_S3 and s3_client:
            # ========================================
            # MODO AWS S3 (Producción)
            # ========================================
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type or 'image/jpeg',
                Metadata={
                    'package_id': package_id,
                    'package_type': package_type,
                    'uploaded_by': str(current_user.id),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            # Generar URL pública de S3
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
            
            print(f"✅ Archivo subido a S3: {s3_key}")
            print(f"🔗 URL S3: {file_url}")
            
        else:
            # ========================================
            # MODO LOCAL (Desarrollo/Fallback)
            # ========================================
            # Crear la estructura de carpetas localmente
            local_file_path = LOCAL_STORAGE_PATH / s3_key
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar el archivo localmente
            with open(local_file_path, 'wb') as f:
                f.write(file_content)
            
            # Generar URL local (accesible via nginx)
            file_url = f"/uploads/{s3_key}"
            
            print(f"✅ Archivo guardado localmente: {local_file_path}")
            print(f"🔗 URL Local: {file_url}")
        
        return {
            "success": True,
            "url": file_url,
            "s3_key": s3_key,
            "size": len(file_content),
            "storage_mode": "s3" if USE_S3 else "local"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error en upload_image_to_s3: {str(e)}")
        print(f"📋 Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

@router.post("/s3-metadata")
async def upload_metadata_to_s3(
    request: Request,
    current_user = Depends(get_current_active_user_from_cookies)
):
    """Subir metadatos JSON a S3 o almacenamiento local (fallback)"""
    try:
        # Verificar permisos (Admins y Operadores pueden subir metadatos)
        if current_user.role not in [UserRole.ADMIN, UserRole.OPERADOR]:
            raise HTTPException(status_code=403, detail="No tienes permisos para subir metadatos")
        
        # Obtener datos del body
        body = await request.json()
        s3_key = body.get('s3_key')
        metadata = body.get('metadata')
        
        if not s3_key or not metadata:
            raise HTTPException(status_code=400, detail="s3_key y metadata son requeridos")
        
        # Convertir metadatos a JSON
        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
        
        if USE_S3 and s3_client:
            # ========================================
            # MODO AWS S3 (Producción)
            # ========================================
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=metadata_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'package_id': metadata.get('packageId', ''),
                    'package_type': metadata.get('packageType', ''),
                    'uploaded_by': str(current_user.id),
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            )
            
            print(f"✅ Metadatos subidos a S3: {s3_key}")
            
        else:
            # ========================================
            # MODO LOCAL (Desarrollo/Fallback)
            # ========================================
            # Crear la estructura de carpetas localmente
            local_file_path = LOCAL_STORAGE_PATH / s3_key
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar los metadatos localmente
            with open(local_file_path, 'w', encoding='utf-8') as f:
                f.write(metadata_json)
            
            print(f"✅ Metadatos guardados localmente: {local_file_path}")
        
        return {
            "success": True,
            "s3_key": s3_key,
            "metadata_uploaded": True,
            "storage_mode": "s3" if USE_S3 else "local"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error subiendo metadatos: {str(e)}")
        print(f"📋 Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error subiendo metadatos: {str(e)}")
