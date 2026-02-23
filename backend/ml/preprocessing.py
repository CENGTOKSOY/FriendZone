import numpy as np
import logging
import os
import joblib
from typing import List, Dict, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Kullanıcı verilerini embedding'e çeviren production-ready preprocessor.
    """

    PERSONALITY_DIMENSIONS = [
        "analytical", "creative", "practical",
        "introvert", "extrovert", "ambivert",
        "organized", "flexible", "balanced",
        "leader", "supporter", "specialist"
    ]

    ADDITIONAL_DIM = 2  # university + department

    def __init__(self, max_hobby_features: int = 50):
        self.hobbies_vectorizer = TfidfVectorizer(
            max_features=max_hobby_features,
            lowercase=True
        )
        self.scaler = StandardScaler()
        self.max_hobby_features = max_hobby_features

        self.vectorizer_fitted = False
        self.scaler_fitted = False

    # --------------------------------------------------
    # PERSONALITY
    # --------------------------------------------------

    def preprocess_personality(self, personality_data) -> np.ndarray:
        vector = np.zeros(len(self.PERSONALITY_DIMENSIONS))

        if isinstance(personality_data, str):
            for dim in personality_data.split("_"):
                if dim in self.PERSONALITY_DIMENSIONS:
                    idx = self.PERSONALITY_DIMENSIONS.index(dim)
                    vector[idx] = 1.0

        elif isinstance(personality_data, dict):
            for key, value in personality_data.items():
                if key in self.PERSONALITY_DIMENSIONS:
                    idx = self.PERSONALITY_DIMENSIONS.index(key)
                    vector[idx] = float(value)

        return vector

    # --------------------------------------------------
    # HOBBIES
    # --------------------------------------------------

    def fit_hobbies(self, all_hobbies: List[List[str]]):
        corpus = [" ".join(h) for h in all_hobbies if h]
        if corpus:
            self.hobbies_vectorizer.fit(corpus)
            self.vectorizer_fitted = True
            logger.info("Hobby vectorizer fitted.")

    def transform_hobbies(self, hobbies_list: List[str]) -> np.ndarray:
        if not self.vectorizer_fitted:
            return np.zeros(self.max_hobby_features)

        text = " ".join(hobbies_list or [])
        vector = self.hobbies_vectorizer.transform([text])
        return vector.toarray().flatten()

    # --------------------------------------------------
    # ADDITIONAL FEATURES
    # --------------------------------------------------

    def _stable_hash(self, value: Optional[str], mod: int = 100) -> float:
        if not value:
            return 0.0
        return (abs(hash(value)) % mod) / mod

    def encode_additional(self, university, department):
        return np.array([
            self._stable_hash(university),
            self._stable_hash(department)
        ])

    # --------------------------------------------------
    # EMBEDDING
    # --------------------------------------------------

    def create_embedding(self, personality, hobbies, university=None, department=None):
        personality_vec = self.preprocess_personality(personality)
        hobbies_vec = self.transform_hobbies(hobbies)
        additional_vec = self.encode_additional(university, department)

        embedding = np.concatenate([
            personality_vec,
            hobbies_vec,
            additional_vec
        ])

        if self.scaler_fitted:
            embedding = self.scaler.transform([embedding])[0]

        return embedding

    # --------------------------------------------------
    # FIT
    # --------------------------------------------------

    def fit(self, users_data: List[Dict]):
        logger.info("Preprocessor fitting başladı...")

        all_hobbies = [u.get("hobbies", []) for u in users_data]
        self.fit_hobbies(all_hobbies)

        embeddings = []

        for user in users_data:
            emb = self.create_embedding(
                user.get("personality_type"),
                user.get("hobbies", []),
                user.get("university"),
                user.get("department")
            )
            embeddings.append(emb)

        if embeddings:
            self.scaler.fit(embeddings)
            self.scaler_fitted = True
            logger.info(f"Scaler {len(embeddings)} kullanıcı ile fit edildi.")

    # --------------------------------------------------
    # SAVE / LOAD
    # --------------------------------------------------

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        joblib.dump({
            "vectorizer": self.hobbies_vectorizer,
            "scaler": self.scaler,
            "vectorizer_fitted": self.vectorizer_fitted,
            "scaler_fitted": self.scaler_fitted,
        }, path)

        logger.info(f"Preprocessor kaydedildi: {path}")

    def load(self, path: str):
        data = joblib.load(path)

        self.hobbies_vectorizer = data["vectorizer"]
        self.scaler = data["scaler"]
        self.vectorizer_fitted = data["vectorizer_fitted"]
        self.scaler_fitted = data["scaler_fitted"]

        logger.info(f"Preprocessor yüklendi: {path}")

    # --------------------------------------------------
    # INFO
    # --------------------------------------------------

    @property
    def embedding_size(self):
        return (
            len(self.PERSONALITY_DIMENSIONS)
            + self.max_hobby_features
            + self.ADDITIONAL_DIM
        )
