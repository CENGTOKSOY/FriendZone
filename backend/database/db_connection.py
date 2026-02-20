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


