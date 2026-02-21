import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Extensions (global ama init_app ile bağlanacak)
db = SQLAlchemy()
migrate = Migrate()


# ----------------------
# Config Sınıfları
# ----------------------

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///friendzone.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# ----------------------
# App Factory
# ----------------------

def create_app(config_class=None):
    """Application Factory Pattern"""

    app = Flask(__name__)

    # Config seçimi
    env = os.getenv("FLASK_ENV", "development")

    if config_class:
        app.config.from_object(config_class)
    elif env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Extensions init
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Models import (circular import önlemek için burada)
    from backend.models import user_model, community_model, similarity_model  # noqa

    # Blueprint register
    register_blueprints(app)

    # Routes
    register_core_routes(app)

    return app


# ----------------------
# Blueprint Register
# ----------------------

def register_blueprints(app):
    from backend.routes.auth_routes import auth_bp
    from backend.routes.test_routes import test_bp
    from backend.routes.community_routes import community_bp
    from backend.routes.assistant_routes import assistant_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(community_bp, url_prefix="/api/community")
    app.register_blueprint(assistant_bp, url_prefix="/api/assistant")


# ----------------------
# Core Routes
# ----------------------

def register_core_routes(app):

    @app.route("/")
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "FriendZone API",
            "version": "1.0.0",
            "environment": os.getenv("FLASK_ENV", "development")
        }), 200

    # Seed sadece development ortamında aktif
    if app.config["DEBUG"]:
        @app.route("/api/seed", methods=["POST"])
        def seed_data():
            from backend.database.seed_data import seed_database
            result = seed_database(app)
            return jsonify(result), 200


# ----------------------
# Run
# ----------------------

if __name__ == "__main__":
    app = create_app()

    from backend.database.db_connection import init_db
    init_db(app)

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app.run(
        host=host,
        port=port,
        debug=debug
    )
