#!/usr/bin/env bash
# 一键启动：后端 (uvicorn) + 前端 (构建并预览)
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/Backend"
FRONTEND="$ROOT/Frontend"
LOGS="$ROOT/logs"
PID="$ROOT/.pids"
BE_PORT=8123
FE_PORT=5173

mkdir -p "$LOGS" "$PID"

echo "==> 启动后端 (端口 $BE_PORT)"
cd "$BACKEND"
if [ -x "$BACKEND/venv/bin/python" ]; then
  PY="$BACKEND/venv/bin/python"
  echo "使用虚拟环境 Backend/venv"
else
  echo "创建虚拟环境..."
  python3 -m venv "$BACKEND/venv" || {
    echo "venv 模块不可用，尝试安装 python3-venv..."
    apt-get update -qq && apt-get install -y -qq python3-venv python3-pip
    python3 -m venv "$BACKEND/venv"
  }
  PY="$BACKEND/venv/bin/python"
  echo "安装后端依赖..."
  "$PY" -m pip install --upgrade pip -q 2>/dev/null || true
  "$PY" -m pip install -q -r requirements.txt
fi
nohup "$PY" -m uvicorn app.main:app --host 0.0.0.0 --port "$BE_PORT" > "$LOGS/backend.log" 2>&1 &
echo $! > "$PID/backend.pid"

echo "==> 安装依赖并构建前端"
cd "$FRONTEND"
npm install
npm run build

echo "==> 启动前端预览 (端口 $FE_PORT)"
nohup npm run preview -- --host 0.0.0.0 --port "$FE_PORT" > "$LOGS/frontend.log" 2>&1 &
echo $! > "$PID/frontend.pid"

sleep 3
echo ""
echo "✅ 启动完成"
echo "   前端: http://localhost:$FE_PORT  (局域网: http://$(hostname -I 2>/dev/null | awk '{print $1}'):$FE_PORT)"
echo "   后端: http://localhost:$BE_PORT"
echo "   日志: $LOGS/backend.log, $LOGS/frontend.log"
