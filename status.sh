#!/usr/bin/env bash
# 查看后端/前端运行状态

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID="$ROOT/.pids"
BE_PORT=8123
FE_PORT=5173

check() {
  local name="$1" port="$2" file="$PID/$1.pid"
  local status="未运行"
  if [ -f "$file" ] && kill -0 "$(cat "$file")" 2>/dev/null; then
    status="运行中 (pid $(cat "$file"))"
  fi
  if (exec 3<>/dev/tcp/127.0.0.1/"$port") 2>/dev/null; then
    status="$status | 端口 $port 监听中"
    exec 3>&-
  fi
  printf "  %-10s %s\n" "$name" "$status"
}

echo "项目运行状态："
check backend "$BE_PORT"
check frontend "$FE_PORT"

# 端口占用提示
echo ""
echo "前端地址: http://localhost:$FE_PORT"
echo "后端地址: http://localhost:$BE_PORT"
echo "日志目录: $ROOT/logs"
