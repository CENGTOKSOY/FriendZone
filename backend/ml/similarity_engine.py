import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import logging
import os
import pickle
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """
    FriendZone Gelişmiş Kullanıcı Benzerlik ve Eşleştirme Motoru.
    Vektörize edilmiş işlemler ve ağırlıklı benzerlik skorlaması içerir.
    """

    def __init__(self, preprocessor, weights: Optional[Dict[str, float]] = None):
        self.preprocessor = preprocessor
        # user_id -> np.array (embedding)
        self.user_embeddings = {}
        # user_id -> meta_data (fakülte, hobi vb. hızlı erişim için)
        self.user_metadata = {}

        # Özellik ağırlıklandırması (Gelecekte ince ayar yapabilmen için)
        self.weights = weights or {
            'personality': 0.4,
            'hobbies': 0.4,
            'academic': 0.2
        }

    def add_user(self, user_id: str, user_data: Dict[str, Any]):
        """Kullanıcıyı sisteme dahil eder ve embedding üretir."""
        try:
            # Preprocessor'dan gelen ham vektör
            embedding = self.preprocessor.create_user_embedding(
                personality_type=user_data.get('personality_type'),
                hobbies=user_data.get('hobbies', []),
                university=user_data.get('university'),
                department=user_data.get('department')
            )

            if embedding is not None:
                # Ensure it's a float32 numpy array for performance
                self.user_embeddings[user_id] = np.array(embedding, dtype=np.float32)
                self.user_metadata[user_id] = {
                    'department': user_data.get('department'),
                    'university': user_data.get('university'),
                    'interests': user_data.get('hobbies', [])
                }
                logger.info(f"Kullanıcı başarıyla indekslendi: {user_id}")
        except Exception as e:
            logger.error(f"Kullanıcı eklenirken hata (ID: {user_id}): {str(e)}")

    def find_similar_users(self, user_id: str, top_k: int = 5, filter_same_dept: bool = False) -> List[Dict[str, Any]]:
        """
        Vektörize edilmiş hızlı benzerlik arama.
        filter_same_dept: Sadece aynı bölümdeki kişileri getirmek için opsiyonel filtre.
        """
        try:
            if user_id not in self.user_embeddings or len(self.user_embeddings) < 2:
                return []

            target_vec = self.user_embeddings[user_id].reshape(1, -1)

            # Tüm kullanıcıları ve embeddingleri listeye dök (Vektörizasyon için)
            all_ids = []
            all_vecs = []

            for uid, vec in self.user_embeddings.items():
                if uid == user_id: continue

                # Opsiyonel Filtreleme: Aynı bölüm kısıtı varsa kontrol et
                if filter_same_dept and self.user_metadata[uid]['department'] != self.user_metadata[user_id][
                    'department']:
                    continue

                all_ids.append(uid)
                all_vecs.append(vec)

            if not all_vecs: return []

            # Tek tek dönmek yerine matris çarpımı yapıyoruz (Çok daha hızlı)
            similarity_matrix = cosine_similarity(target_vec, np.array(all_vecs))
            scores = similarity_matrix[0]

            # En yüksek skorlu top_k indeksi al
            top_indices = np.argsort(scores)[::-1][:top_k]

            results = []
            for idx in top_indices:
                uid = all_ids[idx]
                results.append({
                    'user_id': uid,
                    'similarity_score': round(float(scores[idx]), 4),
                    'metadata': self.user_metadata[uid]
                })

            return results
        except Exception as e:
            logger.error(f"Arama hatası: {str(e)}")
            return []

    def get_batch_recommendations(self, n_clusters: int = 5) -> Dict[int, List[str]]:
        """Kullanıcıları kümelere ayırarak 'topluluk' önerileri oluşturur."""
        if len(self.user_embeddings) < n_clusters:
            return {0: list(self.user_embeddings.keys())}

        uids = list(self.user_embeddings.keys())
        matrix = np.array([self.user_embeddings[uid] for uid in uids])

        kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=42)
        labels = kmeans.fit_predict(matrix)

        clusters = {}
        for uid, label in zip(uids, labels):
            clusters.setdefault(int(label), []).append(uid)

        return clusters

    def save_state(self, directory: str = "models/engine_data"):
        """Sistemin son durumunu (embeddings + metadata) diske kaydeder."""
        try:
            os.makedirs(directory, exist_ok=True)
            with open(f"{directory}/embeddings.pkl", "wb") as f:
                pickle.dump(self.user_embeddings, f)
            with open(f"{directory}/metadata.pkl", "wb") as f:
                pickle.dump(self.user_metadata, f)
            logger.info("Motor durumu başarıyla kaydedildi.")
        except Exception as e:
            logger.error(f"Kaydetme hatası: {e}")

    def load_state(self, directory: str = "models/engine_data"):
        """Diskteki verileri sisteme geri yükler."""
        try:
            if os.path.exists(f"{directory}/embeddings.pkl"):
                with open(f"{directory}/embeddings.pkl", "rb") as f:
                    self.user_embeddings = pickle.load(f)
                with open(f"{directory}/metadata.pkl", "rb") as f:
                    self.user_metadata = pickle.load(f)
                logger.info("Motor durumu geri yüklendi.")
        except Exception as e:
            logger.error(f"Yükleme hatası: {e}")