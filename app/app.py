import os
import time

import pymysql
from flask import Flask, jsonify, render_template, request
from pymysql.cursors import DictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "site"),
    "password": os.environ.get("DB_PASSWORD", "site"),
    "database": os.environ.get("DB_NAME", "site"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def init_db(retries=10, delay=3):
    """等 MySQL 就绪后建表(容器启动时 MySQL 可能还没准备好)。"""
    for attempt in range(1, retries + 1):
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nickname VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            conn.commit()
            conn.close()
            app.logger.info("数据库表初始化完成")
            return
        except Exception as exc:  # noqa: BLE001
            app.logger.warning("数据库未就绪,第 %s/%s 次重试: %s", attempt, retries, exc)
            time.sleep(delay)
    raise RuntimeError("数据库连接失败")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/guestbook")
def guestbook():
    return render_template("guestbook.html")


@app.route("/api/messages", methods=["GET", "POST"])
def messages():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if request.method == "POST":
                data = request.get_json(silent=True) or {}
                nickname = (data.get("nickname") or "").strip()[:50]
                content = (data.get("content") or "").strip()[:1000]
                if not nickname or not content:
                    return jsonify({"error": "昵称和内容不能为空"}), 400
                cur.execute(
                    "INSERT INTO messages (nickname, content) VALUES (%s, %s)",
                    (nickname, content),
                )
                conn.commit()
                return jsonify({"ok": True}), 201

            cur.execute(
                "SELECT nickname, content, created_at "
                "FROM messages ORDER BY id DESC LIMIT 50"
            )
            rows = cur.fetchall()
            for row in rows:
                row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
            return jsonify({"messages": rows})
    finally:
        conn.close()


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


# 容器启动时初始化表(depends_on 的 healthcheck 已保证 MySQL 就绪)
init_db()
