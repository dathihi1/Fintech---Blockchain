# System Testing Guide

## Available Test Scripts

### 1. Quick Test (Recommended)
**File:** `scripts/quick_test.py`

Fast connectivity test for all services.

```bash
python scripts/quick_test.py
```

**Tests:**
- Backend Health Check
- Backend API Endpoints
- Frontend Server
- Frontend-to-Backend Proxy

**Duration:** ~2 seconds

---

### 2. Full System Test
**File:** `scripts/system_test.py`

Comprehensive integration test with detailed results.

```bash
python scripts/system_test.py
```

**Tests:**
- Backend health and all API endpoints
- Frontend server
- Proxy configuration
- CORS configuration
- Response validation

**Duration:** ~5 seconds

---

### 3. Batch File (Windows)
**File:** `scripts/system-test.bat`

Double-click to run the full system test.

---

## Test Results

### All Tests Pass ✓
System is healthy and ready to use.

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Some Tests Fail ⚠
Check:
1. Backend is running: `uvicorn main:app --host 0.0.0.0 --port 8000`
2. Frontend is running: `npm run dev`
3. Database is running: `docker-compose up -d`

### Critical Failures ✗
System is not working. Please:
1. Start database: `cd infrastructure && docker-compose up -d`
2. Check backend logs for errors
3. Check frontend console for errors
4. Verify ports 8000, 3000, 5432 are not blocked

---

## Common Issues

### "Connection refused" Error

**Cause:** Service is not running

**Solution:**
```bash
# Start database
cd infrastructure
docker-compose up -d

# Start backend (in backend directory)
uvicorn main:app --host 0.0.0.0 --port 8000

# Start frontend (in frontend directory)
npm run dev
```

### "Frontend Proxy Failed" Error

**Cause:** Vite proxy not configured or backend not responding

**Solution:**
1. Check `frontend/vite.config.js` has proxy config:
```javascript
proxy: {
    '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
    }
}
```
2. Restart frontend server

### "CORS Error" in Browser

**Cause:** Backend CORS not configured for frontend origin

**Solution:**
Check `backend/core/config.py`:
```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
```

---

## Manual Testing

### Test Backend Directly
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/nlp/keywords
```

### Test Frontend
```bash
curl http://localhost:3000
```

### Test Proxy
```bash
curl http://localhost:3000/api/nlp/keywords
```

---

## Automated Testing

### Run All Tests
```bash
# Quick test
python scripts/quick_test.py

# Full test
python scripts/system_test.py

# Windows batch
scripts\system-test.bat
```

### Expected Output
```
✓ Backend Health       Status: 200
✓ Backend API          Status: 200
✓ Frontend             Status: 200
✓ Frontend Proxy       Status: 200

✓ ALL TESTS PASSED (4/4)
Your system is ready! Access at: http://localhost:3000
```

---

## Dependencies

Test scripts require:
- Python 3.8+
- `requests` library: `pip install requests`
- `colorama` library (for colored output): `pip install colorama`

Install all:
```bash
pip install requests colorama
```

---

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <process_id> /F
```

### Database Connection Failed

**Error:** `Failed to connect to database`

**Solution:**
```bash
# Check Docker is running
docker ps

# Restart database
cd infrastructure
docker-compose down
docker-compose up -d

# Wait 5 seconds for database to start
timeout /t 5
```

### Frontend Build Errors

**Error:** `Module not found` or `Cannot find module`

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

---

## Exit Codes

- `0` - All tests passed
- `1` - Some tests failed (recoverable)
- `2` - Critical failures (system not working)

---

## Test Schedule

**Before Development:**
- Run `quick_test.py` to verify system is ready

**After Changes:**
- Run `system_test.py` to ensure nothing broke

**Before Deployment:**
- Run full system test
- Check all endpoints manually
- Test in browser

---

## Support

If tests continue to fail:
1. Check logs in backend terminal
2. Check browser console (F12)
3. Check Docker logs: `docker-compose logs`
4. Review [IMPLEMENTATION_GUIDE.md](../docs/IMPLEMENTATION_GUIDE.md)
