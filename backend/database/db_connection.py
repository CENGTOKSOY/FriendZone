from backend import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from backend.utils.logger import logger


# --------------------------------------------------
# INIT DATABASE
# --------------------------------------------------

def init_db(app):
    """
    Development ortamında tablo oluşturur.
    Production'da migration kullanılmalıdır.
    """
    try:
        with app.app_context():

            if app.config.get("ENV") == "development":
                db.create_all()
                logger.info("Development ortamında tablolar oluşturuldu.")
            else:
                logger.info("Production ortamında create_all çalıştırılmadı.")

            # Bağlantı testi
            db.session.execute(text("SELECT 1"))
            logger.info("Veritabanı bağlantısı başarılı.")

    except SQLAlchemyError as e:
        logger.exception("Veritabanı başlatma hatası.")
        raise


# --------------------------------------------------
# SESSION MANAGEMENT
# --------------------------------------------------

def get_db_session():
    """
    Aktif SQLAlchemy session'ını döndürür.
    """
    return db.session


def commit_session():
    """
    Güvenli commit işlemi.
    """
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception("Commit sırasında hata oluştu.")
        raise


def rollback_session():
    """
    Manuel rollback.
    """
    db.session.rollback()
    logger.warning("Session rollback yapıldı.")


def close_db_session(exception=None):
    """
    Flask teardown ile birlikte çağrılmalı.
    """
    try:
        if exception:
            db.session.rollback()
            logger.error(f"Session hata nedeniyle rollback edildi: {exception}")

        db.session.remove()
        logger.debug("DB session kapatıldı.")

    except Exception as e:
        logger.exception("Session kapatma sırasında hata oluştu.")
