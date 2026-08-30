#!/bin/bash
set -euo pipefail

# 在项目根目录执行
cd "$(dirname "$0")/.."

echo "▶ 拉取最新代码..."
git pull origin main

echo "▶ 重新构建并启动..."
docker compose up -d --build

echo "▶ 清理无用镜像..."
docker image prune -f

echo "✅ 部署完成,当前容器状态:"
docker compose ps
