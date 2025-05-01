from fastapi import FastAPI, Depends, HTTPException, status, Body, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .models import User, UserCreate, UserResponse, Token, Role, LoginRequest
from .auth import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, get_current_user, check_role
)
from .config import settings
from .database import get_db
import httpx
import uuid
from datetime import timedelta
import base64
import hashlib
import os
from fastapi.responses import JSONResponse

# Глобальная переменная для хранения code_verifier
vk_code_verifier = None

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка безопасности
security = HTTPBearer()

# Маршруты аутентификации
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание нового пользователя
    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        name=user.name,
        hashed_password=get_password_hash(user.password),
        role=Role.USER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создание токенов
    access_token = create_access_token(
        data={"sub": user.email, "role": db_user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    
    # Сохранение refresh токена
    db_user.refresh_token = refresh_token
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    
    # Обновление refresh токена
    user.refresh_token = refresh_token
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Маршруты для работы с VK OAuth
@app.get("/api/auth/vk")
async def vk_auth():
    global vk_code_verifier
    # Генерация code_verifier и code_challenge
    vk_code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(vk_code_verifier.encode()).digest()
    ).decode('utf-8').rstrip('=')

    response = JSONResponse(
        content={
            "auth_url": (
                f"https://id.vk.com/authorize?"
                f"client_id={settings.VK_CLIENT_ID}&"
                f"redirect_uri={settings.VK_REDIRECT_URI}&"
                f"response_type=code&"
                f"scope=email&"
                f"code_challenge={code_challenge}&"
                f"code_challenge_method=S256"
            )
        }
    )

    return response


@app.post("/api/auth/vk/callback")
async def vk_callback(
    request_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Обработка callback от VK OAuth
    Требует JSON тела с параметрами: {"code": "...", "device_id": "..."}
    """
    # Получаем параметры из тела запроса
    code = request_data.get("code")
    device_id = request_data.get("device_id")
    
    # Валидация входных данных
    if not code or not device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Требуются параметры code и device_id в теле запроса"
        )

    if not vk_code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не найден code_verifier. Сначала запросите /api/auth/vk"
        )

    try:
        async with httpx.AsyncClient() as client:
            # 1. Получаем access_token у VK
            token_response = await client.post(
                url="https://id.vk.com/oauth2/auth",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "code_verifier": vk_code_verifier,
                    "device_id": device_id,
                    "redirect_uri": settings.VK_REDIRECT_URI,
                    "client_id": settings.VK_CLIENT_ID
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            # Проверка ответа от VK
            if token_response.status_code != 200:
                error_detail = f"VK вернул ошибку: {token_response.text}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_detail
                )

            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=token_data.get("error_description", "Ошибка авторизации VK")
                )

            # 2. Получаем информацию о пользователе
            user_info = await client.get(
                "https://api.vk.com/method/users.get",
                params={
                    "access_token": token_data["access_token"],
                    "v": "5.131",
                    "fields": "first_name,last_name,email"
                }
            )
            
            user_data = user_info.json()
            
            if "error" in user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=user_data["error"]["error_msg"]
                )

            vk_user = user_data["response"][0]
            email = token_data.get("email") or f"{token_data['user_id']}@vk.com"

            # 3. Создаем или обновляем пользователя
            user = db.query(User).filter(User.vk_id == str(token_data["user_id"])).first()
            
            if not user:
                user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    name=f"{vk_user['first_name']} {vk_user['last_name']}",
                    vk_id=str(token_data["user_id"]),
                    role=Role.USER,
                    hashed_password=get_password_hash(str(token_data["access_token"]))  # Используем access_token для пароля
                )
                db.add(user)
            else:
                # Обновляем данные существующего пользователя
                user.email = email
                user.name = f"{vk_user['first_name']} {vk_user['last_name']}"

            # 4. Генерируем JWT токены
            access_token = create_access_token(
                data={"sub": user.email, "role": user.role}
            )
            refresh_token = create_refresh_token(
                data={"sub": user.email}
            )
            
            # Сохраняем refresh токен
            user.refresh_token = refresh_token
            db.commit()

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user_info": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка подключения к VK API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
# Маршруты для работы с пользователями
@app.get("/api/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/users", response_model=list[UserResponse])
async def read_users(
    current_user: User = Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

@app.put("/api/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: Role,
    current_user: User = Depends(check_role("admin")),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = role
    db.commit()
    return {"message": "Role updated successfully"} 
@app.delete("/api/users/clear-non-admins", 
           dependencies=[Depends(check_role("admin"))],
           summary="Удалить всех пользователей кроме администраторов")
async def clear_non_admin_users(db: Session = Depends(get_db)):
    """
    Удаляет всех пользователей, у которых роль не 'admin'.
    Требуются права администратора.
    """
    try:
        # Удаляем только пользователей без роли admin
        deleted_count = db.query(User)\
                         .filter(User.role != Role.ADMIN)\
                         .delete()
        db.commit()
        
        return {
            "message": f"Удалено {deleted_count} неадминистративных пользователей",
            "remaining_admins": db.query(User)
                                .filter(User.role == Role.ADMIN)
                                .count()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке пользователей: {str(e)}"
        )