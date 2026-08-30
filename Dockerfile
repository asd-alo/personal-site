FROM python:3.11-slim

WORKDIR /app

# 先复制依赖文件,利用 Docker 构建缓存加速后续构建
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

# 用 gunicorn 跑生产环境(比 Flask 自带 dev server 更稳)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
