from pydantic_settings import BaseSettings
from typing import Optional
import requests
import secrets


def get_ngrok_public_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel.get("proto") == "https":
                return tunnel.get("public_url")
    except Exception as e:
        print(f"Не удалось получить ngrok URL: {e}")
    return None


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # VK OAuth
    VK_CLIENT_ID: str
    VK_CLIENT_SECRET: str
    VK_REDIRECT_URI: str

    # Сессии
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32)

    class Config:
        env_file = ".env"

    def update_redirect_uri(self):
        public_url = get_ngrok_public_url()
        if public_url:
            self.VK_REDIRECT_URI = f"{public_url}/api/auth/vk/callback"


# Инициализация настроек
settings = Settings()
settings.update_redirect_uri()
