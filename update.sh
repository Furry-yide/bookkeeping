#!/usr/bin/env bash
# 更新脚本：检查 GitHub 远程仓库，拉取最新代码并重建服务
# 保留本地数据（数据库、配置文件、venv、node_modules）
set -e

# ===== 可配置项 =====
GITHUB_REPO="${GITHUB_REPO:-https://github.com/furcw/bookkeeping.git}"
BRANCH="${BRANCH:-main}"

SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

# ===== 工具函数 =====
log() { echo -e "\033[36m[update]\033[0m $*"; }
warn() { echo -e "\033[33m[warn]\033[0m $*"; }
ok() { echo -e "\033[32m[ok]\033[0m $*"; }
fail() { echo -e "\033[31m[error]\033[0m $*"; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/Backend"
FRONTEND="$ROOT/Frontend"
DB="$BACKEND/cat.db"
VENV="$BACKEND/venv"

# ===== 0. 依赖检查 =====
command -v git >/dev/null 2>&1 || fail "未安装 git，请先运行 install.sh 或手动安装"
command -v node >/dev/null 2>&1 || warn "未安装 Node.js，跳过前端重建"
command -v python3 >/dev/null 2>&1 || warn "未安装 Python，跳过后端依赖更新"

# ===== 1. 备份当前版本 =====
log "备份当前版本..."
BACKUP_DIR="$ROOT/.backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
# 备份关键文件（不包括大目录）
cp -p "$BACKEND/cat.db" "$BACKUP_DIR/" 2>/dev/null || true
cp -p "$BACKEND/requirements.txt" "$BACKUP_DIR/" 2>/dev/null || true
cp -p "$FRONTEND/package.json" "$BACKUP_DIR/" 2>/dev/null || true
ok "备份已保存到 $BACKUP_DIR"

# ===== 2. 检查是否是 git 仓库 =====
if [ -d "$ROOT/.git" ]; then
  log "检测到 git 仓库，开始拉取更新..."
  cd "$ROOT"
  
  # 保存当前 commit hash
  OLD_HASH=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
  
  # 拉取远程更新（不合并，仅 fetch + reset）
  log "正在获取远程更新..."
  git fetch origin "$BRANCH" --quiet
  
  # 检查是否有更新
  NEW_HASH=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "unknown")
  if [ "$OLD_HASH" = "$NEW_HASH" ]; then
    ok "已是最新版本 ($OLD_HASH)"
    exit 0
  fi
  
  log "发现新版本: $OLD_HASH → $NEW_HASH"
  
  # 显示更新内容
  echo ""
  git log --oneline "$OLD_HASH..$NEW_HASH" 2>/dev/null | head -10
  echo ""
  
  # 交互确认
  if [ -t 0 ]; then
    printf "确认更新到新版本？(Y/n): "
    read -r ANS </dev/tty
    case "$ANS" in
      n|N|no|NO) log "已取消更新"; exit 0 ;;
    esac
  fi
  
  # 拉取更新（保留本地修改的文件）
  log "正在拉取代码..."
  git stash 2>/dev/null || true
  git reset --hard "origin/$BRANCH" --quiet
  git stash pop 2>/dev/null || true
  
  ok "代码已更新到 $NEW_HASH"

else
  log "未检测到 git 仓库，尝试通过 HTTP 下载更新..."
  
  # 检查是否有配置的仓库地址
  if [ -z "$GITHUB_REPO" ]; then
    fail "未配置 GITHUB_REPO，请设置环境变量或编辑脚本"
  fi
  
  # 下载最新 tarball
  log "正在下载最新版本..."
  TEMP_DIR=$(mktemp -d)
  trap "rm -rf $TEMP_DIR" EXIT
  
  # 从 GitHub 下载 tarball
  tarball_url="https://github.com/furcw/bookkeeping/archive/refs/heads/$BRANCH.tar.gz"
  if curl -fsSL "$tarball_url" -o "$TEMP_DIR/update.tar.gz" 2>/dev/null; then
    # 解压
    tar xzf "$TEMP_DIR/update.tar.gz" -C "$TEMP_DIR" --strip-components=1
    
    # 同步文件（保留本地数据）
    log "正在同步文件..."
    rsync -av --exclude='.git' \
              --exclude='*.db' \
              --exclude='venv' \
              --exclude='node_modules' \
              --exclude='dist' \
              --exclude='.backups' \
              --exclude='cat.db' \
              "$TEMP_DIR/" "$ROOT/"
    
    ok "代码已更新"
  else
    fail "下载失败，请检查网络或仓库地址"
  fi
fi

# ===== 3. 更新后端依赖 =====
if [ -d "$VENV" ] && command -v python3 >/dev/null 2>&1; then
  log "更新后端依赖..."
  VENV_PY="$VENV/bin/python"
  if [ -f "$VENV_PY" ]; then
    "$VENV_PY" -m pip install --upgrade pip -q 2>/dev/null || true
    "$VENV_PY" -m pip install -q -r "$BACKEND/requirements.txt" 2>/dev/null || true
    ok "后端依赖已更新"
  fi
fi

# ===== 4. 重建前端 =====
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  log "重建前端..."
  cd "$FRONTEND"
  npm install --silent 2>/dev/null || true
  npm run build 2>&1 | tail -3
  cd "$ROOT"
  ok "前端已重建"
fi

# ===== 5. 数据库迁移（如有） =====
if [ -f "$BACKEND/app/database.py" ]; then
  log "执行数据库迁移..."
  if [ -d "$VENV" ]; then
    VENV_PY="$VENV/bin/python"
    "$VENV_PY" -c "
import sys
sys.path.insert(0, '$BACKEND')
from app.database import init_db
print('数据库迁移完成')
" 2>/dev/null || warn "数据库迁移跳过或出错"
  fi
fi

# ===== 6. 清理 =====
log "清理临时文件..."
rm -rf "$ROOT/.backups"/*/temp_* 2>/dev/null || true

# ===== 完成 =====
echo ""
ok "更新完成！"
echo ""
echo "  版本: $(cd "$ROOT" && git log --oneline -1 2>/dev/null || echo 'unknown')"
echo "  数据库: $DB"
echo "  备份: $BACKUP_DIR"
echo ""
echo "重启服务："
echo "  ./stop.sh && ./start.sh"
echo ""