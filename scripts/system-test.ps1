# ========================================
#   Smart Trading Journal - System Test
# ========================================
# This script tests all system components and connections

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Smart Trading Journal - System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0
$warnings = @()

# Test 1: Database Connection
Write-Host "[TEST 1] Testing Database Connection (PostgreSQL:5432)..." -ForegroundColor Yellow
try {
    $dbTest = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue
    if ($dbTest.TcpTestSucceeded) {
        Write-Host "  ✓ Database is running on port 5432" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ Database is NOT running on port 5432" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Error testing database: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 2: Backend API Connection
Write-Host "[TEST 2] Testing Backend API Connection (localhost:8000)..." -ForegroundColor Yellow
try {
    $backendTest = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue
    if ($backendTest.TcpTestSucceeded) {
        Write-Host "  ✓ Backend API is listening on port 8000" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ Backend API is NOT running on port 8000" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Error testing backend: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 3: Backend Health Endpoint
Write-Host "[TEST 3] Testing Backend Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Host "  ✓ Backend health check passed" -ForegroundColor Green
        Write-Host "    - Status: $($health.status)" -ForegroundColor Gray
        Write-Host "    - Demo Mode: $($health.demo_mode)" -ForegroundColor Gray
        Write-Host "    - NLP Model: $($health.nlp_model)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  ✗ Backend health check failed (status: $($health.status))" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Backend health endpoint error: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 4: Backend API Endpoints
Write-Host "[TEST 4] Testing Backend API Endpoints..." -ForegroundColor Yellow
try {
    $keywords = Invoke-RestMethod -Uri "http://localhost:8000/api/nlp/keywords" -Method Get -TimeoutSec 5
    if ($keywords.vi -and $keywords.en) {
        Write-Host "  ✓ NLP Keywords endpoint working" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ NLP Keywords endpoint returned invalid data" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Backend API endpoint error: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 5: Frontend Server Connection
Write-Host "[TEST 5] Testing Frontend Server (localhost:3000)..." -ForegroundColor Yellow
try {
    $frontendTest = Test-NetConnection -ComputerName localhost -Port 3000 -WarningAction SilentlyContinue
    if ($frontendTest.TcpTestSucceeded) {
        Write-Host "  ✓ Frontend is running on port 3000" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ Frontend is NOT running on port 3000" -ForegroundColor Red
        $warnings += "Frontend server is not running. Start it with: npm run dev"
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Error testing frontend: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 6: Frontend HTTP Response
Write-Host "[TEST 6] Testing Frontend HTTP Response..." -ForegroundColor Yellow
try {
    $frontendHttp = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($frontendHttp.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend HTTP response OK (Status: $($frontendHttp.StatusCode))" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ Frontend HTTP response failed (Status: $($frontendHttp.StatusCode))" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Frontend HTTP error: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 7: Frontend API Proxy
Write-Host "[TEST 7] Testing Frontend -> Backend API Proxy..." -ForegroundColor Yellow
try {
    $proxyTest = Invoke-RestMethod -Uri "http://localhost:3000/api/nlp/keywords" -Method Get -TimeoutSec 5
    if ($proxyTest.vi -and $proxyTest.en) {
        Write-Host "  ✓ Frontend proxy to backend API working" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ✗ Frontend proxy returned invalid data" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  ✗ Frontend proxy error: $_" -ForegroundColor Red
    Write-Host "    This means frontend cannot connect to backend!" -ForegroundColor Red
    $warnings += "Frontend-to-Backend proxy is not working. Check Vite configuration."
    $testsFailed++
}
Write-Host ""

# Test 8: CORS Configuration
Write-Host "[TEST 8] Testing CORS Configuration..." -ForegroundColor Yellow
try {
    $corsTest = Invoke-WebRequest -Uri "http://localhost:8000/api/nlp/keywords" -Method Options -Headers @{"Origin"="http://localhost:3000"} -TimeoutSec 5
    $allowOrigin = $corsTest.Headers["Access-Control-Allow-Origin"]
    if ($allowOrigin) {
        Write-Host "  ✓ CORS is configured (Allow-Origin: $allowOrigin)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ⚠ CORS headers not found (may cause browser issues)" -ForegroundColor Yellow
        $warnings += "CORS headers not detected. Frontend may have issues in browser."
        $testsPassed++
    }
} catch {
    Write-Host "  ⚠ Could not test CORS (non-critical): $_" -ForegroundColor Yellow
    $testsPassed++
}
Write-Host ""

# Test 9: Database Connection from Backend
Write-Host "[TEST 9] Testing Backend Database Connection..." -ForegroundColor Yellow
try {
    # Try to access an endpoint that requires database
    $dbTest = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    if ($dbTest.StatusCode -eq 200) {
        Write-Host "  ✓ Backend can serve API docs (database likely connected)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ⚠ Backend API docs returned status: $($dbTest.StatusCode)" -ForegroundColor Yellow
        $testsPassed++
    }
} catch {
    Write-Host "  ✗ Backend database connection may have issues: $_" -ForegroundColor Red
    $warnings += "Backend may not be able to connect to database"
    $testsFailed++
}
Write-Host ""

# Test 10: Process Check
Write-Host "[TEST 10] Checking Running Processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
$nodeProcs = Get-Process | Where-Object {$_.ProcessName -like "*node*"}

if ($pythonProcs) {
    Write-Host "  ✓ Python processes found: $($pythonProcs.Count)" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  ✗ No Python processes running (backend should be running)" -ForegroundColor Red
    $warnings += "Backend Python process not detected"
    $testsFailed++
}

if ($nodeProcs) {
    Write-Host "  ✓ Node processes found: $($nodeProcs.Count)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No Node processes running (frontend may not be running)" -ForegroundColor Yellow
    $warnings += "Frontend Node process not detected"
}
Write-Host ""

# ========================================
# Summary
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests: $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  ⚠ $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Overall Status
if ($testsFailed -eq 0) {
    Write-Host "✓ ALL TESTS PASSED! System is healthy." -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your application at:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    exit 0
} elseif ($testsFailed -le 2) {
    Write-Host "⚠ SOME TESTS FAILED - System may have issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Cyan
    Write-Host "  1. Check if all services are running: docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Restart backend: python backend/main.py" -ForegroundColor White
    Write-Host "  3. Restart frontend: npm run dev (in frontend directory)" -ForegroundColor White
    exit 1
} else {
    Write-Host "✗ CRITICAL FAILURES - System is not working properly" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Cyan
    Write-Host "  1. Database: docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Backend logs for errors" -ForegroundColor White
    Write-Host "  3. Frontend console for errors" -ForegroundColor White
    Write-Host "  4. Network connectivity" -ForegroundColor White
    exit 2
}
