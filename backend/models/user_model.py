from backend.app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)


class User(db.Model):
    """
    Production-ready User modeli
    """

    __tablename__ = "users"

    # --------------------------------------------------
    # Columns
    # --------------------------------------------------

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    university = db.Column(db.String(100), index=True)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)

    # Personality
    personality_type = db.Column(db.String(50), index=True)
    personality_scores = db.Column(db.JSON, nullable=True)

    # Hobbies
    hobbies = db.Column(db.JSON, nullable=True)

    # System
    is_test_completed = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

    communities = relationship(
        "CommunityMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    similarities = relationship(
        "UserSimilarity",
        foreign_keys="UserSimilarity.user_id",
        back_populates="user",
        lazy="selectin"
    )

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(self, name, email, password, **kwargs):
        self.name = name
        self.email = email.lower().strip()
        self.set_password(password)

        self.university = kwargs.get("university")
        self.department = kwargs.get("department")
        self.year = kwargs.get("year")
        self.personality_type = kwargs.get("personality_type")
        self.personality_scores = kwargs.get("personality_scores")
        self.hobbies = kwargs.get("hobbies")

    # --------------------------------------------------
    # Password Methods
    # --------------------------------------------------

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # --------------------------------------------------
    # Business Logic
    # --------------------------------------------------

    def update_test_results(self, personality_type, personality_scores, hobbies):
        """
        Commit işlemi burada yapılmaz.
        Service layer commit eder.
        """
        self.personality_type = personality_type
        self.personality_scores = personality_scores
        self.hobbies = hobbies
        self.is_test_completed = True
        self.updated_at = datetime.utcnow()

    def get_similar_users(self, limit=5):
        """
        Daha performanslı sorgu.
        """
        from backend.models.similarity_model import UserSimilarity

        similarities = (
            db.session.query(UserSimilarity)
            .filter(
                (UserSimilarity.user_id == self.id) |
                (UserSimilarity.similar_user_id == self.id)
            )
            .order_by(UserSimilarity.similarity_score.desc())
            .limit(limit)
            .all()
        )

        similar_users = []

        for sim in similarities:
            other_user_id = (
                sim.similar_user_id
                if sim.user_id == self.id
                else sim.user_id
            )

            similar_user = db.session.get(User, other_user_id)

            if similar_user and similar_user.id != self.id:
                similar_users.append({
                    "user": similar_user.to_dict(),
                    "similarity_score": sim.similarity_score
                })

        return similar_users

    # --------------------------------------------------
    # Serialization
    # --------------------------------------------------

    def to_dict(self):
        """
        Sensitive data (password) dönmez.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "university": self.university,
            "department": self.department,
            "year": self.year,
            "personality_type": self.personality_type,
            "personality_scores": self.personality_scores or {},
            "hobbies": self.hobbies or [],
            "is_test_completed": self.is_test_completed,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # --------------------------------------------------
    # Class Methods
    # --------------------------------------------------

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email.lower().strip()).first()

    @classmethod
    def get_active_test_users(cls):
        return cls.query.filter_by(
            is_test_completed=True,
            is_active=True
        ).all()

    # --------------------------------------------------
    # Representation
    # --------------------------------------------------

    def __repr__(self):
        return f"<User {self.id} | {self.email}>"
