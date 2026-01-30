# 📋 ĐỀ XUẤT DỰ ÁN - VÒNG LOẠI
## CUỘC THI FINTECH - BLOCKCHAIN HACKATHON LẦN THỨ V

---

## 1️⃣ TÊN CHỦ ĐỀ

**SMART TRADING JOURNAL - NHẬT KÝ GIAO DỊCH TỰ ĐỘNG THÔNG MINH**

**Slogan:** *"Turn Your Trading Mistakes Into Winning Strategies"*

---

## 2️⃣ VẤN ĐỀ GIẢI QUYẾT

### 🔴 **Bối cảnh & Pain Points**

#### **Vấn đề 1: Thiếu tự nhận thức trong giao dịch**
- **92% trader thua lỗ** do yếu tố tâm lý (FOMO, Fear, Greed, Revenge Trading)
- Trader không nhận ra mình đang giao dịch theo cảm xúc thay vì theo chiến lược
- Ví dụ thực tế:
  ```
  Trader A mua BTC tại $68,000 (đỉnh trong ngày)
  Lý do: "BTC tăng quá mạnh, sợ lỡ sóng!"
  Kết quả: Giá giảm về $62,000 → Loss -9%
  Vấn đề: Không nhận ra đây là lệnh FOMO
  ```

#### **Vấn đề 2: Ghi chép thủ công tốn thời gian và không hiệu quả**
- Trader phải ghi chép thủ công vào Excel/Notion
- Mất 15-30 phút/ngày cho việc ghi chép
- Dữ liệu không được phân tích sâu, chỉ lưu trữ đơn thuần
- Không có insights hoặc recommendations

#### **Vấn đề 3: Không học được từ sai lầm**
- 78% trader lặp lại cùng một lỗi tâm lý nhiều lần
- Không có hệ thống giúp nhận diện patterns trong hành vi giao dịch
- Thiếu feedback loop để cải thiện chiến lược

#### **Vấn đề 4: Phụ thuộc vào phân tích kỹ thuật mà bỏ qua tâm lý**
- Trader chỉ focus vào RSI, MACD, MA... nhưng bỏ qua psychology
- Không kết hợp được Technical Analysis (TA) với Emotional State
- Ví dụ: Dù biết Doji là tín hiệu đảo chiều, nhưng vẫn FOMO vào do sợ lỡ

### 💡 **Giải pháp của chúng tôi**

**Smart Trading Journal** là một nền tảng tự động hóa:

1. **Tự động import trades** từ sàn (Binance, OKX...)
2. **AI phân tích tâm lý** từ ghi chú giao dịch → Gán nhãn FOMO, Fear, Greed...
3. **Nhận diện mô hình nến** tự động (Doji, Hammer, Engulfing...)
4. **Gợi ý cải thiện chiến lược** dựa trên lịch sử giao dịch

→ **Giúp trader từ "thua do tâm lý" thành "thắng do kỷ luật"**

---

## 3️⃣ ĐỐI TƯỢNG HƯỚNG TỚI

### 🎯 **Khách hàng mục tiêu chính (Primary Users)**

#### **1. Retail Traders (Trader cá nhân)**
- **Đặc điểm:**
  - Giao dịch Crypto/Forex/Chứng khoán
  - Vốn: $500 - $50,000
  - Kinh nghiệm: 6 tháng - 3 năm
  - Vẫn đang thua lỗ hoặc break-even
  
- **Nhu cầu:**
  - Cần công cụ giúp nhận diện lỗi tâm lý
  - Muốn cải thiện win-rate
  - Tìm kiếm giải pháp tự động, tiết kiệm thời gian

- **Tại sao họ cần sản phẩm:**
  ```
  "Tôi biết FOMO là không tốt, nhưng lúc thị trường tăng 
  thì não tôi không kiểm soát được. Cần công cụ cảnh báo 
  trước khi tôi nhấn nút Buy."
  ```

#### **2. Semi-Professional Traders (Trader bán chuyên)**
- **Đặc điểm:**
  - Giao dịch full-time hoặc part-time nghiêm túc
  - Vốn: $50,000 - $500,000
  - Có chiến lược rõ ràng nhưng vẫn vi phạm kỷ luật

- **Nhu cầu:**
  - Backtest hiệu quả của chiến lược
  - Phân tích sâu về performance
  - Tối ưu hóa risk management

#### **3. Trading Communities & Mentors**
- **Đặc điểm:**
  - Giáo viên dạy trading
  - Quản lý nhóm học viên

- **Nhu cầu:**
  - Theo dõi tiến độ học viên
  - Phân tích lỗi phổ biến trong nhóm
  - Cung cấp feedback có data

### 👥 **Quy mô thị trường (Market Size)**

- **Việt Nam:** ~3 triệu trader crypto (2024)
- **SEA:** ~15 triệu traders
- **Global:** ~300 triệu cryptocurrency investors

**Penetration target:**
- Year 1: 1,000 users (Vietnam)
- Year 2: 10,000 users (SEA)
- Year 3: 100,000+ users (Global)

---

## 4️⃣ CÔNG NGHỆ SỬ DỤNG

### 🛠️ **Tech Stack Chi Tiết**

#### **A. BACKEND (Python Ecosystem)**

##### **1. Core Framework**
```python
FastAPI 0.109.0          # High-performance async API framework
Uvicorn 0.27.0           # ASGI server
Pydantic 2.5.0           # Data validation
Python 3.11+             # Latest stable version
```

**Lý do chọn:**
- FastAPI: Nhanh hơn Flask/Django, support async, auto API docs
- Type hints + Pydantic: Code safety, dễ maintain
- Python: Ecosystem AI/ML mạnh nhất

##### **2. Database & ORM**
```python
PostgreSQL 15            # Primary database
SQLAlchemy 2.0.25        # ORM
Alembic 1.13.1           # Database migration
Redis 7.2                # Caching & session
```

**Schema chính:**
- `users`: User accounts, API keys
- `trades`: Trade history (symbol, entry, exit, PnL, timestamp)
- `emotions`: NLP results (trade_id, emotion, confidence)
- `patterns`: Candlestick patterns detected
- `suggestions`: AI recommendations

##### **3. AI & NLP Engine**
```python
transformers 4.36.0      # Hugging Face library
torch 2.1.2              # PyTorch framework
FinBERT                  # Pre-trained financial sentiment model
nltk 3.8.1               # Text preprocessing
```

**Pipeline NLP:**
```
Input: "BTC tăng quá mạnh, mua luôn kẻo lỡ!"
  ↓
1. Text Preprocessing (lowercase, remove stopwords)
  ↓
2. FinBERT Classification
  ↓
3. Output: {"emotion": "FOMO", "confidence": 0.92}
  ↓
4. Store in database + Trigger AI suggestions
```

**Fine-tuning Strategy:**
- Dataset: 500 samples tiếng Việt (tự tạo + crowdsource)
- Labels: FOMO, Fear, Greed, Revenge, Confidence, Neutral
- Accuracy target: 85%+ trên test set

##### **4. Technical Analysis**
```python
TA-Lib 0.4.28           # 150+ technical indicators
pandas 2.1.4            # Data manipulation
numpy 1.26.2            # Numerical computing
```

**Patterns Detection (Top 10 patterns):**
1. Doji (Indecision)
2. Hammer / Inverted Hammer (Reversal)
3. Bullish / Bearish Engulfing
4. Morning Star / Evening Star
5. Shooting Star / Hanging Man

**Integration với Trades:**
```python
# Pseudo-code
if pattern_detected("Doji") and trade_entry_near_pattern:
    flag = "Entry at reversal signal"
    suggestion = "Good timing based on TA"
```

##### **5. External API Integration**
```python
python-binance 1.0.19   # Binance API wrapper
ccxt 4.2.0              # Multi-exchange support
```

**Supported Exchanges:**
- Binance (Priority)
- OKX
- Bybit
- Coinbase (Future)

**Data Sync:**
- Real-time: WebSocket for live trades
- Historical: REST API pagination

#### **B. FRONTEND (Modern React Stack)**

##### **1. Core Framework**
```json
{
  "react": "^18.2.0",
  "vite": "^5.0.8",
  "typescript": "^5.3.3"
}
```

**Lý do chọn:**
- React: Component-based, huge ecosystem
- Vite: Build tool cực nhanh (HMR instant)
- TypeScript: Type safety cho large codebase

##### **2. UI Libraries**
```json
{
  "tailwindcss": "^3.4.0",
  "shadcn/ui": "latest",
  "lucide-react": "^0.294.0"
}
```

**Design Philosophy:**
- Clean, minimal, professional
- Dark mode first (trader prefer dark UI)
- Mobile responsive

##### **3. Charts & Visualization**
```json
{
  "chart.js": "^4.4.1",
  "react-chartjs-2": "^5.2.0",
  "lightweight-charts": "^4.1.0"
}
```

**Key Charts:**
- **PnL Timeline**: Line chart với profit/loss theo thời gian
- **Emotion Distribution**: Pie chart (% FOMO, Fear, Greed...)
- **Win Rate by Pattern**: Bar chart
- **Candlestick Chart**: Hiển thị patterns detected

##### **4. State Management & Data Fetching**
```json
{
  "zustand": "^4.4.7",
  "react-query": "^5.17.0",
  "axios": "^1.6.5"
}
```

**Architecture:**
- Zustand: Global state (user, settings)
- React Query: Server state, caching, refetching
- Axios: HTTP client với interceptors

#### **C. DEPLOYMENT & INFRASTRUCTURE**

##### **1. Containerization**
```yaml
Docker 24.0
docker-compose 2.24
```

**Services:**
- `api`: FastAPI backend
- `postgres`: PostgreSQL database
- `redis`: Cache layer
- `nginx`: Reverse proxy (production)

##### **2. Cloud Platform**
```
Option 1 (MVP): Railway.app
  - Free tier: $5 credit/month
  - Auto deploy from GitHub
  - Built-in PostgreSQL

Option 2 (Production): AWS/GCP
  - ECS/Cloud Run cho containers
  - RDS/Cloud SQL cho database
  - CloudFront/CDN cho frontend
```

##### **3. CI/CD**
```yaml
GitHub Actions:
  - Run tests on PR
  - Lint check (flake8, eslint)
  - Auto deploy to Railway on main branch
```

#### **D. BLOCKCHAIN INTEGRATION (Theo yêu cầu cuộc thi)**

##### **1. NFT Credential (Optional)**
```solidity
// Smart Contract trên Polygon/BSC
contract TradingJournalNFT {
    // Store achievement credentials
    // Example: "Completed 100 trades with 60%+ win rate"
}
```

**Use Cases:**
- Achievement NFTs (gamification)
- Proof of performance (shareable on-chain)
- Premium features unlock

##### **2. Data Immutability (Future)**
- Lưu hash của trading data lên IPFS
- Immutable audit trail
- Transparent performance records

---

## 5️⃣ KỲ VỌNG SẢN PHẨM DEMO

### 🎯 **MVP Features (Vòng 2 - Bán Kết)**

#### **Feature 1: Auto Trade Import** ✅
**Mô tả:**
- Kết nối API key Binance Testnet
- Tự động fetch 50 trades gần nhất
- Parse: Symbol, Entry Price, Exit Price, PnL, Timestamp

**User Flow:**
```
1. User nhập API Key + Secret (Binance Testnet)
2. Click "Import Trades"
3. System fetch data qua API
4. Display trong table: Date | Symbol | Entry | Exit | PnL | Status
```

**Technical:**
- Endpoint: `POST /api/trades/import`
- Rate limit: 1200 req/min (Binance limit)
- Store trades trong PostgreSQL

#### **Feature 2: NLP Emotion Tagging** 🧠
**Mô tả:**
- User thêm note cho mỗi trade
- AI phân tích note → Gán emotion label
- Confidence score hiển thị

**Example:**
| Trade Note | Emotion Detected | Confidence |
|------------|------------------|------------|
| "BTC pump mạnh quá, vào luôn!" | FOMO | 94% |
| "Sợ quá cắt lỗ sớm" | Fear | 88% |
| "Theo kế hoạch, entry đúng setup" | Confidence | 91% |

**Technical:**
- Endpoint: `POST /api/analyze-emotion`
- Model: FinBERT fine-tuned
- Response time: <500ms

#### **Feature 3: Candlestick Pattern Detection** 📊
**Mô tả:**
- Tự động nhận diện 7 patterns phổ biến
- Match patterns với thời điểm entry/exit
- Flag good/bad entries based on pattern

**Patterns MVP:**
1. Doji
2. Hammer
3. Bullish Engulfing
4. Bearish Engulfing
5. Morning Star
6. Evening Star
7. Shooting Star

**Visual:**
```
Trade #12: BTC Long @ $64,200
Pattern Detected: Bullish Engulfing at support
Recommendation: ✅ Good entry signal
Historical Win Rate: 78% for this pattern
```

**Technical:**
- TA-Lib integration
- Fetch OHLCV data từ Binance
- Pattern detection algorithm

#### **Feature 4: AI Suggestions Dashboard** 💡
**Mô tả:**
- Phân tích tất cả trades
- Generate top 5 insights + recommendations

**Example Output:**
```
📊 YOUR STATISTICS:
────────────────────────────────────────
Total Trades: 45
Win Rate: 56%
Total PnL: +$1,240

🔴 TOP MISTAKES:
────────────────────────────────────────
1. FOMO Trades: 18 (40%)
   → Win Rate: 22% (vs 73% non-FOMO)
   💡 Suggestion: Đợi RSI về <30 hoặc giá retest support
   
2. Late Night Trading: 12 trades after 22:00
   → Win Rate: 33%
   💡 Suggestion: Tránh trade khi mệt mỏi
   
3. Ignoring Patterns: 15 trades không có pattern confirmation
   → Win Rate: 40%
   💡 Suggestion: Đợi Bullish Engulfing hoặc Morning Star

✅ TOP STRENGTHS:
────────────────────────────────────────
1. Pattern-based Entries: 85% win rate
   → Continue focus on Morning Star & Hammer
   
2. Proper Stop Loss: Chỉ 2% trades vi phạm SL rule
```

**Technical:**
- Rule-based engine (Python)
- SQL aggregations
- Future: ML-based recommendations

#### **Feature 5: Interactive Dashboard** 📈
**Mô tả:**
- Visualize data qua charts
- Filters: Date range, Symbol, Emotion, Pattern
- Export PDF report

**Key Metrics Cards:**
- Total Trades
- Win Rate %
- Total PnL
- Best Performing Pattern
- Most Common Emotion

**Charts:**
1. PnL Timeline (Line chart)
2. Emotion Distribution (Pie chart)
3. Win Rate by Pattern (Bar chart)
4. Win Rate by Emotion (Bar chart)

---

### 🚀 **Product Roadmap**

#### **Phase 1: MVP (Vòng 2 - 8 tuần)**
- [x] Backend API (FastAPI)
- [x] Database setup (PostgreSQL)
- [x] Binance API integration
- [x] NLP emotion tagging (basic)
- [x] Pattern detection (7 patterns)
- [x] Frontend dashboard (React)
- [x] AI suggestions (rule-based)

#### **Phase 2: Enhanced (Vòng 3 - 4 tuần)**
- [ ] Multi-user support + Authentication
- [ ] Advanced NLP (sentiment từ Twitter/Reddit)
- [ ] Backtesting engine
- [ ] Mobile responsive PWA
- [ ] Export reports (PDF)
- [ ] Community features (share insights)

#### **Phase 3: Production (Post-competition)**
- [ ] Multi-exchange support (OKX, Bybit)
- [ ] Real-time alerts (Telegram bot)
- [ ] ML-based strategy optimization
- [ ] Premium tier (subscription model)
- [ ] Blockchain achievement NFTs
- [ ] API for third-party integration

---

## 6️⃣ GIÁ TRỊ MỘT CÁCH ĐỊNH LƯỢNG

### 📊 **Impact Metrics**

#### **1. Time Savings**
- **Before:** 20 phút/ngày ghi chép thủ công
- **After:** 2 phút/ngày (auto import)
- **Savings:** 90% thời gian, ~120 giờ/năm

#### **2. Win Rate Improvement**
- **Hypothesis:** Giảm 50% FOMO trades → Tăng win rate 10-15%
- **Example:**
  ```
  Trader A (Before):
    - Win Rate: 45%
    - FOMO trades: 40% of total
  
  Trader A (After 3 tháng dùng Smart Journal):
    - Win Rate: 58% (+13%)
    - FOMO trades: 15% (-25%)
  ```

#### **3. Financial Impact**
- **Scenario:** Trader với vốn $10,000, trade 50 lệnh/tháng
- **Before:** Win rate 45% → Tháng average -$200
- **After:** Win rate 58% → Tháng average +$400
- **Gain:** $600/tháng = $7,200/năm

---

## 7️⃣ COMPETITIVE ADVANTAGES

### 🏆 **Điểm khác biệt so với đối thủ**

| Feature | Smart Trading Journal | TradingView Notes | Excel Manual | Edgewonk |
|---------|----------------------|-------------------|--------------|----------|
| Auto Import Trades | ✅ | ❌ | ❌ | ✅ |
| NLP Emotion Analysis | ✅ | ❌ | ❌ | ❌ |
| Pattern Detection | ✅ | ✅ | ❌ | ❌ |
| AI Suggestions | ✅ | ❌ | ❌ | Partial |
| Tiếng Việt Support | ✅ | ❌ | ✅ | ❌ |
| Free Tier | ✅ | ✅ | ✅ | ❌ ($79/year) |
| Real-time Analysis | ✅ | ❌ | ❌ | ❌ |

**Core Differentiation:**
1. **First mover** trong NLP emotion analysis cho crypto trading
2. **Tiếng Việt native** - hiểu context "pump", "dump", "fomo" trong tiếng Việt
3. **All-in-one solution** - Không cần dùng 3-4 tools riêng lẻ

---

## 8️⃣ MONETIZATION MODEL (FUTURE)

### 💰 **Revenue Streams**

#### **Tier 1: Free (Freemium)**
- 50 trades/month limit
- Basic NLP (5 emotions)
- 7 candlestick patterns
- 1 exchange connection

#### **Tier 2: Pro ($9.99/month)**
- Unlimited trades
- Advanced NLP (Twitter/Reddit sentiment)
- 30+ patterns
- Multi-exchange
- Export reports
- Priority support

#### **Tier 3: Team ($29.99/month)**
- All Pro features
- Up to 10 members
- Team analytics
- Mentor dashboard
- API access

**Target:**
- Year 1: 1,000 free users → 100 Pro ($12K ARR)
- Year 2: 10,000 free → 1,500 Pro ($180K ARR)

---

## 9️⃣ DEMO SCENARIOS (CHO VIDEO VÒNG 2)

### 🎬 **Script Demo Video (7 phút)**

#### **Part 1: Problem Introduction (1 phút)**
```
[Voice-over]
"Bạn có bao giờ mua coin khi giá đang ở đỉnh, 
chỉ vì sợ lỡ sóng? Đó chính là FOMO - 
kẻ thù lớn nhất của mọi trader.

78% traders thua lỗ không phải do thiếu kiến thức,
mà do không kiểm soát được cảm xúc.

Hôm nay, chúng mình giới thiệu Smart Trading Journal -
công cụ giúp bạn nhận diện và khắc phục các lỗi tâm lý."
```

#### **Part 2: Demo Core Features (4 phút)**

**Scene 1: Auto Import (30s)**
```
[Screen recording]
1. Nhập API key Binance Testnet
2. Click "Import Trades"
3. 50 trades tự động hiển thị trong table
4. Zoom vào trade #7: BTC Long @ $64,200
```

**Scene 2: Emotion Tagging (1 phút)**
```
[Click vào trade #7]
- Trader note: "BTC tăng 10% trong 2 giờ, vào luôn kẻo lỡ!"
- Click "Analyze Emotion"
- System hiển thị: FOMO (94% confidence)
- Trade result: -8% loss

[Narrator]
"AI đã phát hiện đây là lệnh FOMO. 
Nếu trader biết trước, có thể đã tránh được."
```

**Scene 3: Pattern Detection (1 phút)**
```
[Click sang trade #12]
- Entry: BTC @ $63,800
- System highlight: "Bullish Engulfing detected at support"
- Historical win rate: 78%
- Trade result: +12% profit

[Narrator]
"Trade này vào đúng timing với Bullish Engulfing.
Đây là strength của trader này."
```

**Scene 4: AI Suggestions (1.5 phút)**
```
[Navigate to Insights page]

📊 Statistics showing:
- 45 total trades
- 56% win rate
- 18 FOMO trades (40%) với 22% win rate

💡 AI Suggestions:
1. "Reduce FOMO entries - đợi RSI <30"
2. "80% losing trades sau 22:00 - tránh trade đêm khuya"
3. "Pattern Morning Star có 85% win rate - focus vào setup này"

[Narrator]
"Với insights này, trader có thể:
- Giảm FOMO từ 40% xuống 15%
- Tăng win rate lên 65-70%"
```

#### **Part 3: Call-to-Action (1 phút)**
```
[Outro screen]
"Smart Trading Journal - Turn Mistakes Into Strategies

🎯 Tự động import trades
🧠 AI phân tích tâm lý
📊 Nhận diện patterns
💡 Gợi ý cải thiện

👉 Vote cho chúng mình tại:
[Link DAA platform]

#FADA #BLOCKCHAIN #FINTECH #AI"
```

---

## 🔟 IMPLEMENTATION TIMELINE

### 📅 **12-Week Sprint Plan**

#### **Week 1-2: Vòng Loại**
- [x] Hoàn thiện proposal này
- [ ] Tạo slides 10 trang
- [ ] Design mockup UI (Figma)
- [ ] Setup GitHub repo
- [ ] Pitch trước BGK

#### **Week 3-4: Backend Core**
- [ ] FastAPI project structure
- [ ] PostgreSQL schema design
- [ ] CRUD endpoints
- [ ] Binance API integration
- [ ] Unit tests

#### **Week 5-6: NLP Engine**
- [ ] Collect 500 samples tiếng Việt
- [ ] Fine-tune FinBERT
- [ ] Build emotion classification API
- [ ] Accuracy ≥ 85%

#### **Week 7-8: Pattern Detection**
- [ ] Integrate TA-Lib
- [ ] Implement 7 patterns
- [ ] Match patterns với trades
- [ ] Build suggestion engine

#### **Week 9-10: Frontend**
- [ ] React setup (Vite + TypeScript)
- [ ] Dashboard layout
- [ ] Charts integration (Chart.js)
- [ ] Responsive design
- [ ] Dark mode

#### **Week 11: Demo & Video**
- [ ] Deploy lên Railway
- [ ] Record demo video (7 phút)
- [ ] Create PPT 10 slides
- [ ] Test thoroughly
- [ ] Submit to DAA

#### **Week 12: Voting**
- [ ] Share video on social media
- [ ] Engage với community
- [ ] Track voting metrics

#### **Week 13-14: Vòng 3 Prep**
- [ ] Polish UI/UX
- [ ] Add advanced features
- [ ] Prepare Q&A
- [ ] Practice presentation

#### **Week 15: Chung Kết**
- [ ] Present tại TP.HCM
- [ ] Demo live
- [ ] Q&A với BGK

---

## 1️⃣1️⃣ TEAM REQUIREMENTS

### 👥 **Vai trò cần thiết (3-5 thành viên)**

#### **1. Backend Developer** (1-2 người) 🔴 CRITICAL
**Skills:**
- Python (FastAPI, SQLAlchemy)
- PostgreSQL, Redis
- REST API design
- Docker

**Responsibilities:**
- Build API endpoints
- Database design
- Binance API integration
- Deployment

#### **2. AI/ML Engineer** (1 người) 🔴 CRITICAL
**Skills:**
- Python (PyTorch, Transformers)
- NLP fundamentals
- Model fine-tuning
- Data collection

**Responsibilities:**
- Fine-tune FinBERT
- Create Vietnamese dataset
- Build emotion classifier
- Optimize model performance

#### **3. Frontend Developer** (1 người) 🔴 CRITICAL
**Skills:**
- React, TypeScript
- TailwindCSS
- Chart.js / D3.js
- Responsive design

**Responsibilities:**
- Build dashboard UI
- Charts & visualizations
- API integration
- Mobile responsive

#### **4. Data Analyst / BA** (0.5 người - part-time)
**Skills:**
- Data analysis
- Statistics
- Trading knowledge

**Responsibilities:**
- Collect sample trades
- Define AI suggestions logic
- Validate model accuracy
- Prepare demo scenarios

#### **5. Designer / Content Creator** (0.5 người - part-time)
**Skills:**
- UI/UX design (Figma)
- Video editing
- Social media

**Responsibilities:**
- Design mockups
- Create demo video
- Slides design
- Marketing content

---

## 1️⃣2️⃣ RISKS & MITIGATION

### ⚠️ **Potential Challenges**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dataset tiếng Việt thiếu | High | High | Tự tạo 300 samples + crowdsource |
| FinBERT không hiểu tiếng Việt tốt | Medium | Medium | Dùng PhoBERT hoặc translate pipeline |
| Binance API rate limit | Medium | Low | Cache data + Testnet |
| Team member dropout | High | Medium | Document code tốt, pair programming |
| Video không viral | High | High | Hợp tác crypto communities |

---

## 1️⃣3️⃣ SUCCESS METRICS (VÒNG 2)

### 🎯 **Key Results**

#### **Technical Metrics:**
- [ ] 100% trades imported successfully
- [ ] NLP accuracy ≥ 85%
- [ ] API response time < 500ms
- [ ] Pattern detection accuracy ≥ 75%
- [ ] Frontend performance score > 90 (Lighthouse)

#### **Voting Metrics:**
- [ ] Video views: 5,000+
- [ ] Likes on DAA: 500+
- [ ] Comments: 200+
- [ ] Shares: 100+

#### **Presentation Metrics:**
- [ ] BGK score ≥ 80/100
- [ ] Q&A: Trả lời đúng 90% câu hỏi

---

## 📞 CONTACT & NEXT STEPS

### ✅ **Immediate Actions (Tuần này)**

1. **Xác nhận team (3-5 người)**
   - Assigned roles
   - Commitment check

2. **Setup collaboration tools**
   - GitHub organization
   - Discord/Slack channel
   - Google Drive for docs

3. **Create Figma mockups**
   - Dashboard page
   - Trade detail page
   - Insights page

4. **Prepare pitch slides** (10 slides)
   - Problem
   - Solution
   - Tech stack
   - Demo mockups
   - Timeline

5. **Submit registration to BTC**
   - Dùng form đăng ký chính thức
   - Submit proposal này

---

## 📚 APPENDIX

### A. Glossary

- **FOMO:** Fear Of Missing Out - Nỗi sợ bỏ lỡ cơ hội
- **Doji:** Mô hình nến có body nhỏ, thể hiện indecision
- **FinBERT:** BERT model fine-tuned cho financial sentiment
- **TA-Lib:** Technical Analysis Library
- **MVP:** Minimum Viable Product

### B. References

- [1] "Why 95% of Traders Lose Money" - DailyFX Research
- [2] "Psychology of Trading" - Brett Steenbarger
- [3] FinBERT: https://github.com/ProsusAI/finBERT
- [4] TA-Lib: https://ta-lib.org/

---

**Prepared by:** [Team Name]  
**Date:** 24/01/2026  
**Version:** 1.0  
**Competition:** FADA Fintech-Blockchain Hackathon V
