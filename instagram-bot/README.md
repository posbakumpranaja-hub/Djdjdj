# Instagram Bot untuk Termux

Bot Instagram terintegrasi yang mendukung like, follow, unfollow, komentar,
manajemen proxy, dan logging lengkap. Dioptimalkan untuk berjalan di **Termux**
(Android).

---

## 📁 Struktur Proyek

```
instagram-bot/
├── main.py              # Entry point & menu interaktif
├── config.py            # Konfigurasi global
├── requirements.txt     # Dependensi Python
├── modules/
│   ├── __init__.py
│   ├── auth.py          # Autentikasi Instagram
│   ├── actions.py       # Semua aksi bot
│   ├── proxy.py         # Manajemen proxy
│   └── logger.py        # Sistem logging
├── utils/
│   ├── __init__.py
│   └── validators.py    # Validasi input
├── data/                # Database & file proxy (auto-dibuat)
├── logs/                # File log (auto-dibuat)
└── sessions/            # Session login (auto-dibuat)
```

---

## ⚡ Instalasi di Termux

### 1. Update & pasang dependensi sistem

```bash
pkg update && pkg upgrade -y
pkg install python git libffi openssl -y
pip install --upgrade pip
```

### 2. Clone / salin proyek

```bash
# Jika sudah ada, masuk ke folder:
cd instagram-bot
```

### 3. Pasang dependensi Python

```bash
pip install -r requirements.txt
```

> **Catatan:** `proxybroker` **tidak** digunakan karena tidak kompatibel dengan
> Termux. Manajemen proxy dilakukan secara internal via `modules/proxy.py`.

### 4. Konfigurasi (opsional)

Buat file `.env` di folder `instagram-bot/`:

```dotenv
INSTAGRAM_USERNAME=namaakun
INSTAGRAM_PASSWORD=passwordkamu

# Rate limiting (detik)
DELAY_BETWEEN_ACTIONS=3
MAX_ACTIONS_PER_HOUR=60

# Proxy
USE_PROXY=false
PROXY_ROTATION_INTERVAL=10

# Logging
LOG_LEVEL=INFO
```

### 5. Jalankan bot

```bash
python main.py
```

---

## 🔧 Fitur

| Fitur | Keterangan |
|---|---|
| Login | Login dengan session management & 2FA support |
| Like | Like postingan user atau hashtag |
| Follow | Follow user atau follower dari akun tertentu |
| Unfollow | Unfollow user atau non-followers otomatis |
| Komentar | Komentar acak pada postingan user/hashtag |
| Proxy | Tambah proxy manual, rotasi otomatis |
| Database | Tracking semua aksi di SQLite |
| Logging | Log berwarna di terminal + file rotating |
| Rate Limiting | Delay otomatis antar aksi untuk menghindari ban |
| Graceful Shutdown | Ctrl+C menutup sesi dengan bersih |

---

## 📋 Dependensi

```
instagrapi>=2.0.0
requests>=2.28.0
colorama>=0.4.6
python-dotenv>=0.21.0
aiohttp>=3.8.0
pydantic>=1.10.0
```

---

## ⚠️ Disclaimer

Penggunaan bot pada Instagram dapat melanggar **Terms of Service** Instagram.
Gunakan dengan bijak dan risiko ditanggung pengguna sendiri.
