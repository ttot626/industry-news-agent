# Windows 启动脚本 — 智能资讯问答 Agent
# 用法: .\start-windows.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  智能资讯问答 Agent - 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Docker
Write-Host "[1/5] 检查 Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  OK: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "  错误: 未检测到 Docker！" -ForegroundColor Red
    Write-Host "  请先安装 Docker Desktop:" -ForegroundColor Red
    Write-Host "  https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    Write-Host ""
    exit 1
}

# 2. 检查 .env.development
Write-Host "[2/5] 检查环境配置..." -ForegroundColor Yellow
if (-not (Test-Path ".env.development")) {
    Write-Host "  错误: 找不到 .env.development" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: .env.development 存在" -ForegroundColor Green

# 3. 启动 PostgreSQL
Write-Host "[3/5] 启动 PostgreSQL (Docker)..." -ForegroundColor Yellow
$env:APP_ENV = "development"
Get-Content .env.development | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+?)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim().Trim('"')
        Set-Item -Path "env:$name" -Value $value
    }
}
docker compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Host "  错误: PostgreSQL 启动失败" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: PostgreSQL 已启动 (localhost:5432)" -ForegroundColor Green
Write-Host "  等待数据库就绪..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# 4. 安装 Python 依赖
Write-Host "[4/5] 安装 Python 依赖 (首次较慢)..." -ForegroundColor Yellow
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    pip install uv
}
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "  错误: 依赖安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: 依赖已安装" -ForegroundColor Green

# 5. 数据库迁移 + 启动服务
Write-Host "[5/5] 数据库迁移并启动 API..." -ForegroundColor Yellow
$env:APP_ENV = "development"
uv run alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "  警告: 迁移可能失败，继续尝试启动..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  启动成功！打开浏览器访问:" -ForegroundColor Green
Write-Host "  http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

uv run uvicorn app.main:app --reload --port 8000
