from backend import db
from sqlalchemy.exc import SQLAlchemyError
from backend.utils.logger import logger


def init_db(app):
    """Veritabanını başlatma fonksiyonu"""
    try:
        with app.app_context():
            # Tüm tabloları oluştur
            db.create_all()
            logger.info("Veritabanı başarıyla oluşturuldu")

    except SQLAlchemyError as e:
        logger.error(f"Veritabanı başlatma hatası: {str(e)}")
        raise

def get_db_session():
    """Veritabanı session'ını döndür"""
    return db.session


def close_db_session(exception=None):
    """Veritabanı session'ını kapat"""
    if exception:
        logger.error(f"Session kapatma hatası: {str(exception)}")
