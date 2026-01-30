# 🔧 Setup Guide - Chi Tiết Từng Bước

Hướng dẫn chi tiết để setup Smart Trading Journal từ đầu.

## 📋 Checklist

- [ ] Python 3.8+ đã cài đặt
- [ ] Node.js 16+ đã cài đặt
- [ ] Docker Desktop đã cài đặt và đang chạy
- [ ] Git đã cài đặt
- [ ] 8GB+ RAM available
- [ ] 5GB+ disk space

## 🪟 Windows Setup

### 1. Cài Đặt Prerequisites

#### Python 3.12
```powershell
# Download từ python.org
# Hoặc dùng Windows Store
# Hoặc dùng chocolatey:
choco install python --version=3.12.0
```

#### Node.js
```powershell
# Download từ nodejs.org
# Hoặc dùng chocolatey:
choco install nodejs-lts
```

#### Docker Desktop
```powershell
# Download từ docker.com
# Hoặc dùng chocolatey:
choco install docker-desktop
```

### 2. Clone và Setup

```powershell
# Clone repository
git clone https://github.com/your-username/smart-trading-journal.git
cd smart-trading-journal

# Tạo virtual environment
cd backend
python -m venv venv
venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt

# Setup .env
copy .env.example .env
# Mở .env và chỉnh sửa nếu cần
notepad .env
```

### 3. Khởi Động Database

```powershell
cd ..\infrastructure
docker-compose up -d postgres

# Đợi database khởi động (5-10 giây)
timeout /t 10 /nobreak

# Kiểm tra
docker ps
```

### 4. Chạy Migrations

```powershell
cd ..\backend
alembic upgrade head
```

### 5. Setup Frontend

```powershell
cd ..\frontend
npm install
```

### 6. Khởi Động Ứng Dụng

**Option A: Dùng scripts tự động**
```powershell
cd ..
.\scripts\start-all.bat
```

**Option B: Khởi động thủ công (3 terminals)**

Terminal 1 - Backend:
```powershell
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 - Frontend:
```powershell
cd frontend
npm run dev
```

Terminal 3 - Kiểm tra:
```powershell
cd scripts
python quick_test.py
```

### 7. Truy Cập

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Database: localhost:5432

## 🐧 Linux/Mac Setup

### 1. Cài Đặt Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv nodejs npm docker.io docker-compose

# macOS (dùng Homebrew)
brew install python@3.12 node docker docker-compose
```

### 2. Clone và Setup

```bash
# Clone repository
git clone https://github.com/your-username/smart-trading-journal.git
cd smart-trading-journal

# Tạo virtual environment
cd backend
python3.12 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env
nano .env  # hoặc vim, code, etc.
```

### 3. Khởi Động Database

```bash
cd ../infrastructure
docker-compose up -d postgres

# Đợi database khởi động
sleep 10

# Kiểm tra
docker ps
```

### 4. Chạy Migrations

```bash
cd ../backend
alembic upgrade head
```

### 5. Setup Frontend

```bash
cd ../frontend
npm install
```

### 6. Khởi Động Ứng Dụng

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Test:**
```bash
python scripts/quick_test.py
```

## 🤖 ML Models Setup

### Option 1: Tải Models Đã Train (Khuyến nghị)

```powershell
# Windows
Invoke-WebRequest -Uri "YOUR_GOOGLE_DRIVE_LINK" -OutFile "models.zip"
Expand-Archive models.zip -DestinationPath backend\ml\models\
Remove-Item models.zip

# Linux/Mac
wget YOUR_GOOGLE_DRIVE_LINK -O models.zip
unzip models.zip -d backend/ml/models/
rm models.zip
```

### Option 2: Train Models Từ Đầu

**⚠️ Cần 2-3 giờ trên CPU, 30 phút trên GPU**

```bash
# Train NLP model
python backend/ml/training/train_nlp.py

# Train behavioral classifier
python backend/ml/behavioral/train_classifier.py
```

### Option 3: Chạy Không Models (Simplified)

Trong `backend/.env`:
```env
DEMO_MODE=true
```

App sẽ bỏ qua NLP analysis và chạy với basic features.

## 🔍 Kiểm Tra Setup

### Quick Test

```bash
cd scripts
python quick_test.py
```

Kết quả mong đợi:
```
✓ Backend Health       http://localhost:8000/health             Status: 200
✓ Backend API          http://localhost:8000/api/nlp/keywords   Status: 200
✓ Frontend             http://localhost:3000                    Status: 200
✓ Frontend Proxy       http://localhost:3000/api/nlp/keywords   Status: 200
```

### System Test

```bash
python scripts/system_test.py
```

### Manual Tests

```bash
# Test backend
curl http://localhost:8000/health

# Test symbols API
curl http://localhost:8000/api/symbols/popular?limit=5

# Test trade creation (demo mode)
curl -X POST http://localhost:8000/api/trades/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "long",
    "entry_price": 45000,
    "quantity": 0.1,
    "notes": "Test trade"
  }'
```

## 🐛 Common Issues

### Port Already in Use

```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Database Connection Failed

```bash
# Restart Docker
docker-compose restart postgres

# Check logs
docker logs trading-journal-db

# Verify connection string in .env matches docker-compose.yml
```

### Module Not Found

```bash
# Verify virtual environment is activated
# Should see (venv) in prompt

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Can't Connect to Backend

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS in `backend/.env`: Must include `http://localhost:3000`
3. Hard refresh browser: `Ctrl + Shift + R`
4. Check browser console (F12) for errors

### Docker Desktop Not Running

```bash
# Windows
Start-Service docker

# Or restart Docker Desktop from taskbar
```

## 📊 Verify Installation

Sau khi setup xong, bạn nên:

1. ✅ Thấy frontend tại http://localhost:3000
2. ✅ Thấy API docs tại http://localhost:8000/docs
3. ✅ Tạo được trade mới trong UI
4. ✅ Autocomplete symbols hoạt động
5. ✅ Tất cả tests pass

## 🎯 Next Steps

1. Đọc [API Documentation](http://localhost:8000/docs)
2. Explore code trong `backend/` và `frontend/`
3. Tạo vài trades để test
4. Xem logs để hiểu flow
5. Bắt đầu customize!

## 💡 Tips

- **Performance**: Models cần ~2GB RAM, giảm USE_GPU=false nếu chậm
- **Development**: Dùng `--reload` cho uvicorn để auto-restart
- **Debugging**: Check logs trong `backend/ml/logs/`
- **Database**: Dùng PgAdmin tại localhost:5050 (optional)

## 📞 Need Help?

1. Check [README.md](README.md) Troubleshooting section
2. Review [GitHub Issues](https://github.com/your-username/smart-trading-journal/issues)
3. Create new issue with:
   - OS version
   - Python version (`python --version`)
   - Error logs
   - Steps to reproduce
