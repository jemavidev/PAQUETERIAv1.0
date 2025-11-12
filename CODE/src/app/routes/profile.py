from fastapi import APIRouter, Depends, Response, Request
from app.dependencies import get_current_active_user_from_cookies
from app.models.user import User

router = APIRouter()

@router.api_route('/', methods=['GET', 'HEAD'])
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies)
):
    """Obtener información del perfil del usuario actual (GET) o verificar autenticación (HEAD)"""
    # Si es HEAD, solo retornar 200 sin contenido
    if request.method == 'HEAD':
        return Response(status_code=200)
    
    # Si es GET, retornar información completa
    return {
        'id': str(current_user.id),
        'username': current_user.username,
        'email': current_user.email,
        'full_name': current_user.full_name,
        'role': current_user.role.value if current_user.role else None,
        'is_active': current_user.is_active,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'updated_at': current_user.updated_at.isoformat() if current_user.updated_at else None
    }
