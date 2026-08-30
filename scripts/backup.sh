#!/bin/bash
set -euo pipefail

# 在项目根目录执行
cd "$(dirname "$0")/.."

# 加载 .env 里的数据库密码
set -a
[ -f .env ] && . ./.env
set +a

BACKUP_DIR="${BACKUP_DIR:-/root/backups}"
KEEP_DAYS="${KEEP_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="${BACKUP_DIR}/site_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

# 用 MYSQL_PWD 传密码(不暴露在命令行里),从 db 容器导出并压缩
docker compose exec -T -e MYSQL_PWD="${MYSQL_ROOT_PASSWORD}" db \
  mysqldump -u root "${MYSQL_DATABASE}" | gzip > "$FILE"

# 删除超过 KEEP_DAYS 天的旧备份,只保留最近 7 份
find "$BACKUP_DIR" -name "site_*.sql.gz" -mtime +"$KEEP_DAYS" -delete

echo "✅ 备份完成: $FILE"
ls -lh "$BACKUP_DIR" | tail -n +2
