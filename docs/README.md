# Smart Trading Journal - Documentation Index

## 📚 Component Documentation

| # | Component | File | Mô tả |
|---|-----------|------|-------|
| 1 | [Kafka Pipeline](./01-kafka-pipeline.md) | Data ingestion & streaming | Thu thập và stream dữ liệu giao dịch |
| 2 | [Passive Analyzer](./02-passive-analyzer.md) | Historical analysis | Phân tích lịch sử, patterns thụ động |
| 3 | [Active Analyzer](./03-active-analyzer.md) | Real-time detection | Phát hiện hành vi rủi ro real-time |
| 4 | [NLP Engine](./04-nlp-engine.md) | Text analysis | Phân tích tâm lý từ ghi chú trade |
| 5 | [Candlestick Analyzer](./05-candlestick-analyzer.md) | Pattern recognition | Nhận diện mô hình nến TA-Lib |
| 6 | [Market Context](./06-market-context.md) | Data enrichment | Enrich bối cảnh thị trường |
| 7 | [API Layer](./07-api-layer.md) | FastAPI backend | REST API & WebSocket |
| 8 | [Frontend](./08-frontend.md) | React dashboard | UI/UX components |

## 🏗️ Kiến trúc tổng quan

```
                    ┌─────────────┐
                    │   Frontend  │
                    │   (React)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  API Layer  │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│ NLP Engine    │  │  Candlestick  │  │    Market     │
│ (FinBERT)     │  │  Analyzer     │  │   Context     │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│   Passive     │  │    Active     │  │    Kafka      │
│   Analyzer    │  │   Analyzer    │  │   Pipeline    │
└───────────────┘  └───────────────┘  └───────────────┘
```

## 🚀 Quick Start (sau khi approve)

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Start backend
cd backend && uvicorn main:app --reload

# 3. Start frontend
cd frontend && npm run dev
```
