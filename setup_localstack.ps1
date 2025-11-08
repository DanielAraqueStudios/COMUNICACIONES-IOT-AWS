# Quick Start Script for LocalStack Setup
# Run this script to set up and start the Bedside Monitor system locally

Write-Host "`n🏥 Bedside Monitor IoT System - LocalStack Quick Start`n" -ForegroundColor Cyan

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================
Write-Host "📋 Step 1: Checking prerequisites...`n" -ForegroundColor Yellow

# Check Docker
Write-Host "  Checking Docker..." -NoNewline
try {
    $dockerVersion = docker --version
    Write-Host " ✅ Found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Docker not found!" -ForegroundColor Red
    Write-Host "  Please install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "  Checking Python..." -NoNewline
try {
    $pythonVersion = python --version
    Write-Host " ✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.7+: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# ============================================================================
# STEP 2: Install Python Dependencies
# ============================================================================
Write-Host "`n📦 Step 2: Installing Python dependencies...`n" -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Dependencies installed successfully`n" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to install dependencies`n" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ❌ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# ============================================================================
# STEP 3: Set Up Environment
# ============================================================================
Write-Host "⚙️  Step 3: Configuring environment...`n" -ForegroundColor Yellow

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "  Creating .env file..." -NoNewline
    Copy-Item ".env.example" ".env"
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host "  ✅ .env file already exists" -ForegroundColor Green
}

# Set environment variables for this session
$env:USE_LOCALSTACK = "true"
$env:LOCALSTACK_ENDPOINT = "http://localhost:4566"
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"

Write-Host "  ✅ Environment configured for LocalStack`n" -ForegroundColor Green

# ============================================================================
# STEP 4: Start LocalStack
# ============================================================================
Write-Host "🚀 Step 4: Starting LocalStack...`n" -ForegroundColor Yellow

# Check if LocalStack is already running
$runningContainers = docker ps --filter "name=bedside-monitor-localstack" --format "{{.Names}}"
if ($runningContainers -contains "bedside-monitor-localstack") {
    Write-Host "  ℹ️  LocalStack is already running" -ForegroundColor Cyan
    $restart = Read-Host "  Do you want to restart it? (y/N)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Host "  Restarting LocalStack..." -NoNewline
        docker-compose restart localstack
        Write-Host " ✅" -ForegroundColor Green
        Start-Sleep -Seconds 10
    }
} else {
    Write-Host "  Starting LocalStack container..." -NoNewline
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "  ⏳ Waiting for LocalStack to initialize (30 seconds)..." -NoNewline
        Start-Sleep -Seconds 30
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "  Failed to start LocalStack. Check Docker logs." -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# STEP 5: Verify LocalStack Services
# ============================================================================
Write-Host "`n🔍 Step 5: Verifying LocalStack services...`n" -ForegroundColor Yellow

# Test connection
Write-Host "  Testing LocalStack endpoint..." -NoNewline
try {
    $health = Invoke-WebRequest -Uri "http://localhost:4566/_localstack/health" -UseBasicParsing
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ❌ Cannot connect to LocalStack" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Test AWS CLI Local
Write-Host "  Testing awslocal CLI..." -NoNewline
try {
    $streams = awslocal kinesis list-streams 2>&1
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  awslocal not available, using aws CLI with endpoint" -ForegroundColor Yellow
}

# ============================================================================
# STEP 6: Test Configuration
# ============================================================================
Write-Host "`n🧪 Step 6: Testing configuration...`n" -ForegroundColor Yellow

python localstack_config.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✅ Configuration test passed!`n" -ForegroundColor Green
} else {
    Write-Host "`n  ❌ Configuration test failed!`n" -ForegroundColor Red
    exit 1
}

# ============================================================================
# SUCCESS - Display Next Steps
# ============================================================================
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ LocalStack Setup Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📚 Next Steps:" -ForegroundColor Yellow
Write-Host "`n1️⃣  Start the data publisher:" -ForegroundColor Cyan
Write-Host "   python kinesis_publisher_local.py`n"

Write-Host "2️⃣  In a new terminal, start the anomaly detector:" -ForegroundColor Cyan
Write-Host "   `$env:USE_LOCALSTACK=`"true`"`n   python consumer_and_anomaly_detector_local.py`n"

Write-Host "3️⃣  In another terminal, start the DynamoDB writer:" -ForegroundColor Cyan
Write-Host "   `$env:USE_LOCALSTACK=`"true`"`n   python consume_and_update_local.py`n"

Write-Host "4️⃣  View DynamoDB data:" -ForegroundColor Cyan
Write-Host "   awslocal dynamodb scan --table-name BSM_anamoly`n"

Write-Host "5️⃣  Stop LocalStack when done:" -ForegroundColor Cyan
Write-Host "   docker-compose down`n"

Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "📖 For detailed documentation, see:" -ForegroundColor Yellow
Write-Host "   - LOCALSTACK_SETUP.md (complete guide)" -ForegroundColor White
Write-Host "   - README.md (project overview)`n" -ForegroundColor White

Write-Host "🌐 LocalStack Dashboard: http://localhost:4566/_localstack/health`n" -ForegroundColor Cyan

# Ask if user wants to start publisher now
$startNow = Read-Host "Do you want to start the publisher now? (y/N)"
if ($startNow -eq "y" -or $startNow -eq "Y") {
    Write-Host "`n🚀 Starting publisher... (Press Ctrl+C to stop)`n" -ForegroundColor Green
    python kinesis_publisher_local.py
}
