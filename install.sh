#!/usr/bin/env bash
# 自动配置运行环境（支持裸 Linux 服务器）：
#   1. (可选) 从 GitHub 拉取/更新代码
#   2. (自动) 安装 git / Python / Node 运行时（按系统包管理器）
#   3. 创建 Python 虚拟环境并安装后端依赖
#   4. 安装前端依赖
set -e

# ===== 可配置项 =====
# 留空则使用脚本所在目录；填入仓库地址则会 clone/pull 到本地目录
GITHUB_REPO=""
# 例如: GITHUB_REPO="https://github.com/yourname/bookkeeping.git"

SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "macos" ;;
    Linux)
      if [ -f /etc/debian_version ]; then echo "debian";
      elif [ -f /etc/redhat-release ]; then echo "redhat";
      else echo "linux"; fi ;;
    *) echo "unknown" ;;
  esac
}
OS="$(detect_os)"

pkg_install() {
  # $1 = debian 包名, $2 = redhat 包名
  case "$OS" in
    debian) $SUDO apt-get install -y "$1" ;;
    redhat) $SUDO dnf install -y "$2" ;;
    macos) command -v brew >/dev/null 2>&1 && brew install "$1" ;;
  esac
}

install_git() {
  command -v git >/dev/null 2>&1 && return
  echo "==> 未检测到 git，开始自动安装 ($OS)"
  case "$OS" in
    macos) brew install git ;;
    debian) $SUDO apt-get update -y; $SUDO apt-get install -y git ;;
    redhat) $SUDO dnf install -y git ;;
    *) echo "❌ 无法自动安装 git，请手动安装后重试"; exit 1 ;;
  esac
}

install_python() {
  if command -v python3 >/dev/null 2>&1; then return; fi
  echo "==> 未检测到 python3，开始自动安装 ($OS)"
  case "$OS" in
    macos)
      command -v brew >/dev/null 2>&1 || { echo "❌ 请先安装 Homebrew: https://brew.sh"; exit 1; }
      brew install python@3.12 ;;
    debian) $SUDO apt-get update -y; $SUDO apt-get install -y python3 python3-venv python3-pip ;;
    redhat) $SUDO dnf install -y python3 ;;
    *) echo "❌ 无法自动安装 Python，请手动安装 Python 3.10+ 后重试"; exit 1 ;;
  esac
}

install_node() {
  if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then return; fi
  echo "==> 未检测到 node/npm，开始自动安装 Node.js 18+ ($OS)"
  case "$OS" in
    macos) brew install node ;;
    debian)
      command -v curl >/dev/null 2>&1 || $SUDO apt-get install -y curl
      curl -fsSL https://deb.nodesource.com/setup_20.x -o /tmp/nodesource.sh
      if $SUDO bash /tmp/nodesource.sh && $SUDO apt-get install -y nodejs; then
        echo "✅ 已通过 NodeSource 安装 Node.js"
      else
        echo "⚠️  NodeSource 安装失败，回退使用 apt 默认版本"
        $SUDO apt-get install -y nodejs npm || true
      fi ;;
    redhat)
      $SUDO dnf install -y nodejs || {
        $SUDO dnf module enable -y nodejs:20 && $SUDO dnf install -y nodejs
      } ;;
    *) echo "⚠️  无法自动安装 Node.js，请手动安装 18+ 后重新运行"; return ;;
  esac
}

# ===== 1. 拉取代码 =====
install_git
if [ -n "$GITHUB_REPO" ]; then
  echo "==> 从 GitHub 拉取代码: $GITHUB_REPO"
  REPO_NAME="$(basename "$GITHUB_REPO" .git)"
  if [ ! -d "$REPO_NAME" ]; then
    git clone "$GITHUB_REPO" "$REPO_NAME"
  else
    (cd "$REPO_NAME" && git pull)
  fi
  ROOT="$(cd "$REPO_NAME" && pwd)"
else
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
echo "项目目录: $ROOT"

BACKEND="$ROOT/Backend"
FRONTEND="$ROOT/Frontend"

# ===== 2. 自动安装运行时 =====
install_python
install_node
echo "使用 $(python3 -V 2>&1)"

# ===== 3. Python 虚拟环境 + 后端依赖 =====
echo "==> 创建 Python 虚拟环境 ($BACKEND/venv)"
if [ ! -d "$BACKEND/venv" ]; then
  python3 -m venv "$BACKEND/venv"
fi
VENV_PY="$BACKEND/venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip -q
"$VENV_PY" -m pip install -q -r "$BACKEND/requirements.txt"
echo "✅ 后端依赖已安装到虚拟环境"

# ===== 4. 前端依赖 =====
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  NODE_VER="$(node -v)"
  echo "使用 Node $NODE_VER / npm $(npm -v)"
  if [ "${NODE_VER#v}" \< "18.0.0" ]; then
    echo "⚠️  当前 Node 版本低于 18，前端可能无法构建，建议升级到 Node 18+"
  fi
  echo "==> 安装前端依赖"
  (cd "$FRONTEND" && npm install)
  echo "✅ 前端依赖已安装"
else
  echo "⚠️  未安装 Node.js，已跳过前端依赖（Vue 环境不完整）"
fi

echo ""
echo "🎉 环境配置完成，运行 ./start.sh 启动服务。"
