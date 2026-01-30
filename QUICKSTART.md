# 🚀 Quick Start - Chạy Ngay Trong 5 Phút

Hướng dẫn siêu nhanh để chạy Smart Trading Journal.

## ⚡ Cài Đặt Nhanh (Windows)

### 1. Prerequisites (nếu chưa có)

- Python 3.8+: https://www.python.org/downloads/
- Node.js 16+: https://nodejs.org/
- Docker Desktop: https://www.docker.com/products/docker-desktop/

### 2. Clone & Setup (3 phút)

```powershell
# Clone repository
git clone https://github.com/your-username/smart-trading-journal.git
cd smart-trading-journal

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# Database
cd ..\infrastructure
docker-compose up -d postgres
timeout /t 10

# Migrations
cd ..\backend
alembic upgrade head

# Frontend setup
cd ..\frontend
npm install
```

### 3. Run (30 giây)

```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn main:app --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 4. Open Browser

🌐 http://localhost:3000

## 🐧 Linux/Mac

```bash
git clone https://github.com/your-username/smart-trading-journal.git
cd smart-trading-journal

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Database
cd ../infrastructure
docker-compose up -d postgres
sleep 10

# Migrations
cd ../backend
alembic upgrade head

# Frontend
cd ../frontend
npm install

# Run
# Terminal 1: cd backend && source venv/bin/activate && uvicorn main:app --port 8000
# Terminal 2: cd frontend && npm run dev
```

## ⚙️ Models (Optional)

**Chạy không cần models:**
Trong `backend/.env`:
```env
DEMO_MODE=true
```

**Tải models:**
- Link: [Google Drive - Coming Soon]
- Giải nén vào `backend/ml/models/`

## ✅ Kiểm Tra

```bash
python scripts/quick_test.py
```

Phải thấy 4 ✓ màu xanh!

## 🎯 Features

- ✅ Tạo/sửa/xóa trades
- ✅ Autocomplete symbols
- ✅ Basic sentiment analysis
- 🔜 Advanced NLP (cần models)
- 🔜 Behavioral detection (cần models)

## 🆘 Lỗi?

**Port 8000 đã dùng:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Database lỗi:**
```powershell
docker-compose restart postgres
```

**Frontend không connect:**
```powershell
# Ctrl + Shift + R trong browser
```

## 📚 Docs

- 📖 [README.md](README.md) - Full documentation
- 🔧 [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- 🌐 API Docs: http://localhost:8000/docs

---

⭐ Star nếu thấy hữu ích!
