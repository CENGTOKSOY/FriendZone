from backend import db
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import relationship
import logging

logger = logging.getLogger(__name__)


# ==================================================
# COMMUNITY
# ==================================================

class Community(db.Model):
    __tablename__ = "communities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)

    category = db.Column(db.String(50), index=True)
    tags = db.Column(db.JSON, nullable=True)

    compatibility_score = db.Column(db.Float, default=0.0, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    max_members = db.Column(db.Integer, default=10)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    members = relationship(
        "CommunityMember",
        back_populates="community",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="selectin"
    )

    # ---------------------------
    # Business Logic (No Commit)
    # ---------------------------

    def add_member(self, user_id: int, role="member"):
        """
        Commit dışarıdan yapılmalı.
        """
        if self.is_full:
            raise ValueError("Topluluk maksimum kapasiteye ulaştı.")

        existing = db.session.query(CommunityMember).filter_by(
            community_id=self.id,
            user_id=user_id
        ).first()

        if existing:
            raise ValueError("Kullanıcı zaten üye.")

        new_member = CommunityMember(
            community_id=self.id,
            user_id=user_id,
            role=role
        )

        db.session.add(new_member)
        return new_member

    def remove_member(self, user_id: int):
        member = db.session.query(CommunityMember).filter_by(
            community_id=self.id,
            user_id=user_id
        ).first()

        if not member:
            return False

        db.session.delete(member)
        return True

    @property
    def current_member_count(self):
        return len(self.members)

    @property
    def is_full(self):
        return self.current_member_count >= self.max_members

    def update_compatibility_score(self, score: float):
        self.compatibility_score = float(score)
        self.updated_at = datetime.utcnow()

    # ---------------------------
    # Serialization
    # ---------------------------

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags or [],
            "compatibility_score": self.compatibility_score,
            "max_members": self.max_members,
            "current_member_count": self.current_member_count,
            "is_full": self.is_full,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        if include_members:
            data["members"] = [
                m.to_dict(include_user=True)
                for m in self.members
                if m.is_active
            ]

        return data

    # ---------------------------
    # Query Helpers
    # ---------------------------

    @classmethod
    def active_by_category(cls, category):
        return cls.query.filter_by(
            category=category,
            is_active=True
        ).all()

    @classmethod
    def recommended(cls, limit=5):
        return (
            cls.query
            .filter_by(is_active=True)
            .order_by(cls.compatibility_score.desc())
            .limit(limit)
            .all()
        )

    def __repr__(self):
        return f"<Community {self.id} | {self.name}>"



# ==================================================
# COMMUNITY MEMBER (JOIN TABLE)
# ==================================================

class CommunityMember(db.Model):
    __tablename__ = "community_members"

    __table_args__ = (
        UniqueConstraint("community_id", "user_id", name="uq_community_user"),
        Index("idx_community_user", "community_id", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)

    community_id = db.Column(
        db.Integer,
        db.ForeignKey("communities.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    role = db.Column(db.String(20), default="member")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Relationships
    community = relationship("Community", back_populates="members")
    user = relationship("User", back_populates="communities", lazy="selectin")

    def to_dict(self, include_user=False):
        data = {
            "id": self.id,
            "community_id": self.community_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_at": self.joined_at.isoformat(),
            "is_active": self.is_active,
        }

        if include_user and self.user:
            data["user"] = self.user.to_dict()

        return data

    def __repr__(self):
        return f"<CommunityMember u:{self.user_id} c:{self.community_id}>"
