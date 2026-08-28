#!/usr/bin/env bash
# 停止后端与前端的运行进程

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID="$ROOT/.pids"

stop_one() {
  local name="$1" file="$PID/$1.pid"
  if [ -f "$file" ]; then
    local pid
    pid="$(cat "$file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && echo "已停止 $name (pid $pid)"
    fi
    rm -f "$file"
  fi
}

echo "==> 停止服务"
stop_one backend
stop_one frontend

# 兜底清理可能残留的进程
pkill -f "uvicorn app.main" 2>/dev/null && echo "已清理残留 uvicorn" || true
pkill -f "vite preview" 2>/dev/null && echo "已清理残留 vite preview" || true

echo "✅ 停止完成"
