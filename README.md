# 🧠 FriendZone

**FriendZone**, üniversite öğrencilerinin kişilik özellikleri ve ilgi alanlarına göre **makine öğrenimi (ML)** tabanlı bir şekilde sanal topluluklar oluşturmasını sağlayan sosyal bir platformdur.  
Bu proje, bir **üniversite bitirme projesi** kapsamında geliştirilmiştir.

---

## 🎯 Projenin Amacı

FriendZone, öğrencilerin:

- 🧍‍♂️ Kendi **kişilik tipi** ve **hobilerine** göre benzer öğrencilerle tanışmasını,  
- 🧑‍🤝‍🧑 Ortak **sanal topluluklar** (community’ler) içinde etkileşime geçmesini,  
- 🤖 **GPT tabanlı bir asistan** aracılığıyla grup içinde öneriler, sohbet konuları ve etkinlik fikirleri almasını sağlar.  

> Kısacası FriendZone, “Spotify Blend” veya “Netflix öneri motoru” gibi davranır; ancak odak noktası insan eşleşmesidir.

---

## 🧩 Proje Bileşenleri

### 🎨 Frontend (HTML, CSS, JS)
- Kayıt ve giriş ekranları  
- Kişilik testi ve hobi testi sayfaları  
- Kullanıcının dahil olduğu toplulukları listeleyen arayüz  
- Dinamik topluluk sayfası (`community.html`)  
- GPT tabanlı öneri asistanı (`gptAssistant.js`)

### ⚙️ Backend (Python, Flask)
- Kullanıcı ve topluluk işlemleri için **REST API**  
- **SQLAlchemy** ile veritabanı bağlantısı (SQLite veya PostgreSQL)  
- **ML modeli** ile kullanıcı eşleşmesi (cosine similarity veya clustering)  
- **GPT entegrasyonu** için servis katmanı (`gpt_service.py`)  
- Ortam değişkenleri `.env` dosyasında saklanır

### 🧠 Makine Öğrenimi Katmanı (ML)
- Test verilerini sayısallaştırma ve ön işleme (`preprocessing.py`)  
- Kullanıcı embedding’leri oluşturma (`user_vectors.npy`)  
- Benzerlik hesaplama (`similarity_engine.py`)  
- Kullanıcıyı uygun topluluğa atama (`community_assigner.py`)

---

## 🏗️ Proje Klasör Yapısı

```
FriendZone/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── ml/
│   ├── database/
│   ├── services/
│   └── utils/
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── personality_test.html
│   ├── hobbies.html
│   ├── communities.html
│   ├── community.html
│   ├── profile.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── data/
│   ├── raw/
│   └── processed/
│
└── docs/
```

---

## 🔐 .env Örneği

```
FLASK_ENV=development
SECRET_KEY=supersecret
DATABASE_URL=sqlite:///friendzone.db
OPENAI_API_KEY=sk-xxxx
PORT=5000
HOST=0.0.0.0
```

---

## 🧠 Proje Akışı

1. Kullanıcı kayıt olur (`auth_routes.py`)
2. Kişilik ve hobi testlerini tamamlar (`test_routes.py`)
3. Backend, ML modeliyle benzer kullanıcıları bulur (`similarity_engine.py`)
4. Kullanıcıyı uygun topluluğa atar (`community_assigner.py`)
5. Topluluk sayfası frontend’de dinamik olarak oluşturulur (`communityManager.js`)
6. GPT asistanı topluluk içinde öneriler üretir (`gpt_service.py`, `gptAssistant.js`)

---

## ⚙️ Yapay Zekâdan Beklenen Davranışlar

1. Proje mimarisine sadık kal  
2. Her kodu açıklamalı şekilde yaz  
3. Kodlarda dosya yolu belirtilsin (örneğin: `backend/app.py:`)  
4. `.env` içindeki veriler gizli tutulmalı  
5. Gerektiğinde önce backend, sonra frontend ve ML katmanı oluşturulmalı  
6. Flask – HTML – JS entegrasyonu uyumlu şekilde yapılmalı  

---

## 🎯 Son Hedef

- ✅ Çalışır bir Flask backend  
- ✅ Etkileşimli HTML/CSS/JS frontend  
- ✅ ML modeli ile kullanıcı–topluluk eşleşmesi  
- ✅ GPT entegrasyonu ile dinamik öneri asistanı  
- ✅ Hepsi tek proje dizininde, GitHub’a push edilebilir şekilde

---

## 🚀 Başlatma Adımları

### 1️⃣ Backend Kurulumu
Flask backend altyapısını kurmak için şu dosyaları oluştur:
- `backend/app.py`  
- `backend/config.py`  
- `backend/database/db_connection.py`  
- `backend/__init__.py`  

Flask + SQLAlchemy + CORS desteğiyle yapılandır.  
Veritabanı `.env` dosyasındaki `DATABASE_URL` üzerinden bağlansın.

---

### 2️⃣ Modeller
`backend/models/` klasöründe şu modelleri tanımla:
- `user_model.py` → kullanıcı bilgileri  
- `community_model.py` → topluluk bilgileri  
- `similarity_model.py` → kullanıcılar arası benzerlik skorları  

---

### 3️⃣ Route’lar
`backend/routes/` klasöründe:
- `auth_routes.py` → kayıt/giriş işlemleri  
- `test_routes.py` → test sonuçlarını backend’e gönderme  
- `community_routes.py` → kullanıcıyı topluluklara yönlendirme  
- `assistant_routes.py` → GPT’den öneri alma  

Tüm route’lar Blueprint yapısında olmalı.

---

### 4️⃣ ML Katmanı
`backend/ml/` klasöründe:
- `preprocessing.py` → test verilerini normalize eder  
- `similarity_engine.py` → cosine similarity hesaplar  
- `community_assigner.py` → uygun topluluğu belirler  

---

### 5️⃣ GPT Servisi
`backend/services/gpt_service.py` dosyası:
- `.env` içindeki `OPENAI_API_KEY` değerini kullanır  
- `get_group_suggestions(topic, members)` fonksiyonu öneriler üretir  

---

### 6️⃣ Frontend Başlangıcı
Frontend’de:
- `index.html`, `login.html`, `signup.html`  
- Formlar `fetch()` ile backend’e istek atar  

---

### 7️⃣ Test Sayfaları
Frontend’de:
- `personality_test.html`, `hobbies.html`  
- Kullanıcı seçimlerini `testHandler.js` üzerinden backend’e gönderir  

---

### 8️⃣ Topluluk Sayfası
- `community.html`, `communityHandler.js`, `communityManager.js`  
- Kullanıcıya özel topluluk arayüzü dinamik şekilde yüklenir  

---

### 9️⃣ GPT Asistanı
`gptAssistant.js`:
- Sohbet konusu, etkinlik önerisi gibi içerikler üretir  
- Backend’deki `/assistant` endpoint’i ile etkileşir  

---

### 🔟 Final Test
- Backend’i başlat:  
  ```bash
  flask run
  ```

* Frontend sayfalarını tarayıcıda aç
* Veri akışı, topluluk eşleşmesi ve GPT önerilerini test et

---

## 📂 Geliştirici Notu

Bu proje; yapay zekâ, makine öğrenimi, backend ve frontend teknolojilerini bütüncül bir yapıda bir araya getirir.
**FriendZone**, öğrenciler arasında anlamlı bağlantılar kurmayı hedefleyen akıllı bir sosyal etkileşim platformudur.

