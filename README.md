# 🚀 Smart Trading Journal

Ứng dụng nhật ký giao dịch thông minh với phân tích NLP, phát hiện thao túng tâm lý và phân tích kỹ thuật tự động.

## ✨ Tính Năng Chính

- 📊 **Quản lý giao dịch**: Theo dõi lệnh giao dịch với phân tích chi tiết
- 🤖 **Phân tích NLP**: Phân tích tâm lý từ ghi chú bằng AI (FinBERT)
- 🧠 **Phát hiện thao túng**: Machine Learning phát hiện các bias tâm lý
- 📈 **Phân tích kỹ thuật**: Tự động phân tích candlestick patterns
- 🔍 **Tìm kiếm symbols**: Autocomplete symbols từ Binance
- 🎯 **Demo mode**: Chạy ngay không cần authentication

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Database chính
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PyTorch + Transformers** - NLP models
- **FinBERT** - Financial sentiment analysis
- **Binance API** - Symbol data

### Frontend
- **React** - UI framework
- **Material-UI (MUI)** - Component library
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router** - Routing

### Infrastructure
- **Docker** - PostgreSQL container
- **Uvicorn** - ASGI server

## 📋 Yêu Cầu Hệ Thống

- **Python** 3.8+ (khuyến nghị 3.12)
- **Node.js** 16+ và npm/yarn
- **Docker Desktop** (cho PostgreSQL)
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB cho training models)
- **Disk**: ~5GB cho models và dependencies

## 🚀 Hướng Dẫn Cài Đặt

### 1. Clone Repository

```bash
git clone https://github.com/your-username/smart-trading-journal.git
cd smart-trading-journal
```

### 2. Setup Backend

#### a. Tạo Python Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### b. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

#### c. Setup Environment Variables

Tạo file `.env` trong thư mục `backend/`:

```env
# Database
DATABASE_URL=postgresql://trader:password@localhost:5432/trading_journal

# Security (tạo secret key mới cho production)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Demo Mode
DEMO_MODE=true

# ML Models
NLP_MODEL_NAME=ProsusAI/finbert
USE_GPU=false

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

Hoặc copy từ template:
```bash
cp .env.example .env
```

#### d. Tải ML Models

**⚠️ QUAN TRỌNG**: Do models quá nặng (~3GB), không được đưa vào Git.

**Cách 1: Tải models đã train sẵn**
```bash
# Download từ Google Drive (link sẽ được cung cấp)
# Giải nén vào backend/ml/models/

# Hoặc dùng script tự động (nếu có):
python scripts/download_models.py
```

**Cách 2: Train models từ đầu**
```bash
# Train NLP model (cần ~2-3 giờ trên CPU)
python backend/ml/training/train_nlp.py

# Train behavioral classifier
python backend/ml/behavioral/train_classifier.py
```

**Cách 3: Chạy không cần models (chế độ đơn giản)**

Nếu không cần NLP analysis, set trong `.env`:
```env
DEMO_MODE=true
# App sẽ bỏ qua NLP analysis
```

### 3. Setup Database

#### a. Khởi động PostgreSQL với Docker

```bash
cd infrastructure
docker-compose up -d postgres
```

Kiểm tra database đã chạy:
```bash
docker ps
# Phải thấy container: trading-journal-db
```

#### b. Chạy Database Migrations

```bash
cd ../backend
alembic upgrade head
```

### 4. Setup Frontend

```bash
cd ../frontend
npm install
```

## ▶️ Chạy Ứng Dụng

### Khởi động tất cả services:

#### Option 1: Dùng scripts (Windows)

```bash
# Từ thư mục gốc smart-trading-journal
.\scripts\start-all.bat
```

#### Option 2: Khởi động thủ công

**Terminal 1 - Database:**
```bash
cd infrastructure
docker-compose up postgres
```

**Terminal 2 - Backend:**
```bash
cd backend
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Truy cập ứng dụng:

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🗄️ **Database**: localhost:5432
- 🔍 **PgAdmin** (optional): http://localhost:5050

## 🧪 Testing

### Chạy tất cả tests:

```bash
# Backend tests
cd backend
pytest tests/ -v

# Hoặc dùng script
python scripts/run_tests.py
```

### Quick connectivity test:

```bash
python scripts/quick_test.py
```

### System integration test:

```bash
python scripts/system_test.py
```

## 📁 Cấu Trúc Dự Án

```
smart-trading-journal/
├── backend/                    # FastAPI backend
│   ├── alembic/               # Database migrations
│   ├── analyzers/             # Market analysis logic
│   │   ├── active_analyzer.py # Technical analysis
│   │   ├── passive_analyzer.py# NLP analysis
│   │   └── detectors/         # Pattern detectors
│   ├── api/                   # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── trades.py         # Trade operations
│   │   ├── symbols.py        # Symbol search
│   │   └── nlp.py            # NLP endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Configuration
│   │   └── auth.py           # Auth logic
│   ├── ml/                    # Machine learning
│   │   ├── models/           # Trained models (NOT in git)
│   │   ├── training/         # Training scripts
│   │   └── behavioral/       # Behavioral analysis
│   ├── models/               # SQLAlchemy models
│   ├── nlp/                  # NLP engine
│   ├── services/             # Business logic
│   ├── tests/                # Unit & integration tests
│   └── main.py               # Application entry point
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   └── hooks/            # Custom hooks
│   ├── package.json
│   └── vite.config.js
├── infrastructure/            # Docker setup
│   └── docker-compose.yml
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
└── README.md                 # This file
```

## 🔧 Cấu Hình

### Backend Configuration

File: `backend/.env`

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db_name

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Features
DEMO_MODE=true              # Bật demo mode (không cần auth)
USE_GPU=false              # Dùng GPU cho ML models

# ML Models
NLP_MODEL_NAME=ProsusAI/finbert

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Configuration

File: `frontend/vite.config.js`

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## 🐛 Troubleshooting

### Backend không start được

```bash
# 1. Kiểm tra Python version
python --version  # Phải >= 3.8

# 2. Kiểm tra virtual environment
which python  # Phải trỏ vào venv/Scripts/python

# 3. Kiểm tra port 8000 đã bị chiếm chưa
netstat -ano | findstr :8000

# 4. Kill process nếu cần (Windows)
# Tìm PID từ lệnh trên, sau đó:
taskkill /PID <pid> /F
```

### Database connection error

```bash
# 1. Kiểm tra Docker container
docker ps

# 2. Restart PostgreSQL
docker-compose restart postgres

# 3. Kiểm tra database URL trong .env
# Phải match với docker-compose.yml
```

### Frontend không connect được backend

```bash
# 1. Kiểm tra backend đã chạy chưa
curl http://localhost:8000/health

# 2. Kiểm tra CORS settings trong backend/.env
# Phải có http://localhost:3000 trong CORS_ORIGINS

# 3. Hard refresh browser
# Ctrl + Shift + R (Chrome)
# Ctrl + F5 (Edge)
```

### Models không tải được

```bash
# 1. Kiểm tra models đã tải chưa
ls backend/ml/models/

# 2. Nếu chưa có, tải từ Google Drive
# Hoặc train mới

# 3. Hoặc bật DEMO_MODE=true để bỏ qua NLP
```

### Autocomplete symbols không hoạt động

```bash
# 1. Kiểm tra backend symbols API
curl http://localhost:8000/api/symbols/popular

# 2. Clear browser cache
# F12 > Application > Clear storage

# 3. Hard refresh
# Ctrl + Shift + R
```

## 📚 API Documentation

Sau khi start backend, truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints:

```
GET  /api/health              - Health check
POST /api/auth/register       - Đăng ký user
POST /api/auth/login          - Đăng nhập

GET  /api/trades/             - Lấy danh sách trades
POST /api/trades/             - Tạo trade mới
GET  /api/trades/{id}         - Chi tiết trade
PATCH /api/trades/{id}        - Cập nhật trade
DELETE /api/trades/{id}       - Xóa trade

GET  /api/symbols/popular     - Popular symbols
GET  /api/symbols/search?q=BTC - Tìm symbols

POST /api/nlp/analyze         - Phân tích NLP
GET  /api/nlp/emotions        - Danh sách emotions
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📝 License

[MIT License](LICENSE) - Tự do sử dụng cho mục đích học tập và thương mại.

## 👥 Authors

- **Your Name** - [GitHub](https://github.com/your-username)

## 🙏 Acknowledgments

- [FinBERT](https://huggingface.co/ProsusAI/finbert) - Financial sentiment analysis
- [Binance API](https://binance-docs.github.io/apidocs/) - Market data
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
- [Material-UI](https://mui.com/) - UI components

## 📞 Support

Nếu gặp vấn đề:

1. Kiểm tra [Troubleshooting](#-troubleshooting) section
2. Xem [Issues](https://github.com/your-username/smart-trading-journal/issues)
3. Tạo issue mới nếu chưa có

## 🗺️ Roadmap

- [ ] Thêm real-time price tracking
- [ ] Mobile app (React Native)
- [ ] Advanced charting với TradingView
- [ ] Export reports (PDF, CSV)
- [ ] Social features (share strategies)
- [ ] Multi-language support
- [ ] Cloud deployment guides

---

⭐ **Nếu project hữu ích, hãy cho 1 star nhé!** ⭐
