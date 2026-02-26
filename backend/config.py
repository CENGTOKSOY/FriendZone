import os
from dotenv import load_dotenv


# Sadece development ortamında .env yükle
if os.getenv("FLASK_ENV") != "production":
    load_dotenv()


def str_to_bool(value: str) -> bool:
    """String environment değişkenini boolean'a çevirir"""
    return str(value).lower() in ("true", "1", "yes", "on")


class BaseConfig:
    """Ortak temel konfigürasyon"""

    # -------------------------------------------------
    # Core Flask
    # -------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = str_to_bool(os.getenv("DEBUG", "false"))

    # -------------------------------------------------
    # Database
    # -------------------------------------------------
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///friendzone.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # -------------------------------------------------
    # API Keys
    # -------------------------------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # -------------------------------------------------
    # Server
    # -------------------------------------------------
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    # -------------------------------------------------
    # Security
    # -------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENV == "production"


class DevelopmentConfig(BaseConfig):
    """Development ortamı"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production ortamı"""

    DEBUG = False

    # Production’da SECRET_KEY zorunlu olsun
    if not os.getenv("SECRET_KEY"):
        raise ValueError("❌ Production ortamında SECRET_KEY tanımlanmalıdır!")

    # Production’da SQLite kullanılmasın
    if "sqlite" in BaseConfig.SQLALCHEMY_DATABASE_URI:
        raise ValueError("❌ Production ortamında SQLite kullanmayın!")


class TestingConfig(BaseConfig):
    """Testing ortamı"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
