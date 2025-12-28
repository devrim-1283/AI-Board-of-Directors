# 🏛️ AI Yönetim Kurulu / AI Board of Directors

> Yapay zeka destekli sanal yönetim kurulu simülasyonu ile fikirlerinizi test edin!  
> Test your ideas with an AI-powered virtual board of directors simulation!

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots)
[![Gemini](https://img.shields.io/badge/Google-Gemini%203-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🇹🇷 Türkçe

### 📋 Proje Hakkında

Bu proje, Telegram üzerinde çalışan yapay zeka destekli bir "Yönetim Kurulu" simülasyonudur. 6 farklı AI karakteri, sunduğunuz fikirleri kendi uzmanlık alanlarından değerlendirir ve gerçekçi bir tartışma ortamı oluşturur.

### 🤖 Yönetim Kurulu Üyeleri

| Rol | Görev | Odak Noktası |
|-----|-------|--------------|
| **Başkan (Chairman)** | Toplantıyı yönetir, özetler | Karar verme, konsensüs |
| **CTO** | Teknik fizibilite | Mimari, güvenlik, süre tahmini |
| **CFO** | Maliyet analizi | Bütçe, ROI, finansal risk |
| **Growth Hacker** | Pazarlama stratejisi | Viral potansiyel, pazar analizi |
| **Product Owner** | Kullanıcı deneyimi | UX, basitlik, hedef kitle |
| **Risk Analisti** | Kriz senaryoları | Hukuki riskler, tehditler |

### ✨ Özellikler

- 🎭 **6 Farklı AI Karakteri** - Her biri kendine özgü bakış açısıyla
- 💬 **3 Turlu Tartışma** - İlk Görüşler → Tartışma → Son Sözler
- 🔄 **Gerçek Zamanlı** - Telegram grubunda anlık etkileşim
- 📊 **Şirket Bağlamı** - `readme.json` ile kişiselleştirme
- 💾 **Veritabanı Kaydı** - Tüm toplantılar PostgreSQL'de saklanır

### 🚀 Kurulum

#### 1. Gereksinimleri Yükle

```bash
git clone https://github.com/YOUR_USERNAME/ai-yonetim-kurulu.git
cd ai-yonetim-kurulu
pip install -r requirements.txt
```

#### 2. Telegram Botlarını Oluştur

1. [@BotFather](https://t.me/BotFather)'a git
2. `/newbot` komutu ile 6 bot oluştur:
   - `YonetimKuruluBaskani_bot` (Chairman)
   - `CTO_DevrimSoft_bot`
   - `CFO_DevrimSoft_bot`
   - `GrowthHacker_DevrimSoft_bot`
   - `ProductOwner_DevrimSoft_bot`
   - `RiskAnalisti_DevrimSoft_bot`
3. Her bot için aldığın token'ı not et

#### 3. Telegram Grubu Oluştur

1. Yeni bir Telegram grubu oluştur
2. Tüm 6 botu gruba ekle ve **admin** yap
3. Grup ID'sini öğren (bot başladığında loglardan veya [@userinfobot](https://t.me/userinfobot) ile)

#### 4. Ortam Değişkenlerini Ayarla

`.env` dosyası oluştur:

```env
# Google AI Studio API Key
GOOGLE_API_KEY=your_google_api_key

# Telegram Bot Tokens
TOKEN_CHAIRMAN=your_chairman_token
TOKEN_CTO=your_cto_token
TOKEN_CFO=your_cfo_token
TOKEN_GROWTH=your_growth_token
TOKEN_PRODUCT=your_product_token
TOKEN_DEVIL=your_devil_token

# Telegram Group
TELEGRAM_GROUP_ID=-100xxxxxxxxxx

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/board_db
```

#### 5. Şirket Bilgilerini Düzenle

`src/readme.json` dosyasını düzenleyerek AI'ların sizi daha iyi tanımasını sağlayın:

```json
{
  "company": {
    "name": "Şirket Adınız",
    "sector": "Sektörünüz",
    "team_size": 5
  },
  "budget": {
    "monthly_budget_try": 10000
  },
  "priorities": ["Düşük maliyet", "Hızlı geliştirme"]
}
```

#### 6. Çalıştır

```bash
# Lokal
python src/main.py

# Docker ile
docker-compose up --build
```

### 📱 Kullanım

Telegram grubunda şu komutları kullanabilirsiniz:

| Komut | Açıklama |
|-------|----------|
| `/toplanti [Konu]` | Yeni toplantı başlatır |
| `/tanis` | Tüm botlar kendini tanıtır |
| `/ozet` | Mevcut toplantıyı özetleyip kapatır |
| `/sus` | Toplantıyı acil durdurur |
| `/info` | Yardım mesajını gösterir |

**Örnek:**
```
/toplanti Mobil uygulama geliştirmeli miyiz?
```

### 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Group                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Bot Manager                          │
│  (6 Telegram Bot - Chairman, CTO, CFO, Growth, etc.)    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Orchestrator                         │
│  (Toplantı akışı, tur yönetimi, mesaj sıralaması)       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Gemini AI Engine                      │
│  (Google Gemini 3 Flash API)                            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     PostgreSQL                           │
│  (Toplantı ve mesaj kayıtları)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🇬🇧 English

### 📋 About

This project is an AI-powered "Board of Directors" simulation running on Telegram. 6 different AI characters evaluate your ideas from their areas of expertise and create a realistic discussion environment.

### 🤖 Board Members

| Role | Responsibility | Focus |
|------|---------------|-------|
| **Chairman** | Moderates meeting, summarizes | Decision making, consensus |
| **CTO** | Technical feasibility | Architecture, security, timeline |
| **CFO** | Cost analysis | Budget, ROI, financial risk |
| **Growth Hacker** | Marketing strategy | Viral potential, market analysis |
| **Product Owner** | User experience | UX, simplicity, target audience |
| **Risk Analyst** | Crisis scenarios | Legal risks, threats |

### ✨ Features

- 🎭 **6 Different AI Characters** - Each with unique perspective
- 💬 **3-Round Discussion** - Initial Opinions → Debate → Final Verdict
- 🔄 **Real-time** - Instant interaction in Telegram group
- 📊 **Company Context** - Personalization via `readme.json`
- 💾 **Database Logging** - All meetings stored in PostgreSQL

### 🚀 Installation

#### 1. Install Requirements

```bash
git clone https://github.com/YOUR_USERNAME/ai-board-of-directors.git
cd ai-board-of-directors
pip install -r requirements.txt
```

#### 2. Create Telegram Bots

1. Go to [@BotFather](https://t.me/BotFather)
2. Create 6 bots using `/newbot` command
3. Save each bot token

#### 3. Create Telegram Group

1. Create a new Telegram group
2. Add all 6 bots and make them **admin**
3. Get the Group ID from logs or [@userinfobot](https://t.me/userinfobot)

#### 4. Set Environment Variables

Create `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
TOKEN_CHAIRMAN=your_chairman_token
TOKEN_CTO=your_cto_token
TOKEN_CFO=your_cfo_token
TOKEN_GROWTH=your_growth_token
TOKEN_PRODUCT=your_product_token
TOKEN_DEVIL=your_devil_token
TELEGRAM_GROUP_ID=-100xxxxxxxxxx
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/board_db
```

#### 5. Configure Company Info

Edit `src/readme.json` to help AI understand your context:

```json
{
  "company": {
    "name": "Your Company",
    "sector": "Your Sector",
    "team_size": 5
  },
  "budget": {
    "monthly_budget_try": 10000
  }
}
```

#### 6. Run

```bash
# Local
python src/main.py

# With Docker
docker-compose up --build
```

### 📱 Usage

Available commands in Telegram group:

| Command | Description |
|---------|-------------|
| `/toplanti [Topic]` | Start a new meeting |
| `/tanis` | All bots introduce themselves |
| `/ozet` | Summarize and close current meeting |
| `/sus` | Emergency stop meeting |
| `/info` | Show help message |

**Example:**
```
/toplanti Should we develop a mobile app?
```

### 🛠️ Tech Stack

- **Backend:** Python 3.11+
- **AI:** Google Gemini 3 Flash
- **Bot Framework:** python-telegram-bot
- **Database:** PostgreSQL + SQLAlchemy (async)
- **Deployment:** Docker + Coolify

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Devrim Tunçer**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Devrim%20Tunçer-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request