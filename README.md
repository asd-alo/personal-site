# 个人主页 + 留言板(运维求职项目)

一个完整走通「代码 → 构建 → 部署 → 运维」全链路的全栈个人网站。用于展示 **Docker、Nginx、Linux、MySQL、HTTPS、监控、CI/CD** 等运维技能。

## 技术栈

| 层 | 技术 |
|---|---|
| 应用后端 | Python · Flask · Gunicorn |
| 数据库 | MySQL 8 |
| 反向代理 | Nginx |
| 容器编排 | Docker · Docker Compose |
| 自动化 | Shell 脚本 · GitHub Actions CI/CD |
| 监控 | Prometheus · Grafana · Node Exporter |
| 部署环境 | Ubuntu 22.04 云服务器 |

## 架构

```
浏览器
   │
   ▼
Nginx (反向代理 :80) ──► Flask 应用 (gunicorn :5000) ──► MySQL (留言数据)
                              │
                              └── /healthz 健康检查端点

监控链路
Node Exporter (:9100) ──► Prometheus (:9090) ──► Grafana (:3000)
```

业务容器(应用 / 数据库 / Nginx)与监控栈(Prometheus / Grafana / Node Exporter)都接入自定义网络 `site-net`。

## 目录结构

```
personal-site/
├── app/                  # Flask 应用
│   ├── app.py            # 主程序(含建表、留言 API、健康检查)
│   ├── requirements.txt
│   ├── templates/        # 页面模板
│   └── static/           # CSS / JS
├── nginx/nginx.conf      # 反向代理配置
├── monitoring/           # 监控
│   ├── prometheus.yml    # Prometheus 抓取配置
│   └── grafana/          # Grafana 数据源 + 面板(自动加载)
├── Dockerfile            # 应用镜像
├── docker-compose.yml    # 多容器编排
├── scripts/
│   ├── backup.sh         # MySQL 备份 + 自动轮转
│   └── deploy.sh         # 一键部署
├── .github/workflows/    # CI/CD
└── .env.example          # 环境变量示例(密码等)
```

## 快速开始(本地)

```bash
# 1. 准备环境变量
cp .env.example .env
# 编辑 .env,把密码改掉

# 2. 一键构建并启动
docker compose up -d --build

# 3. 访问
# 打开 http://localhost
```

## 监控

Prometheus + Grafana 随 `docker compose up` 一起启动,监控服务器资源指标:

| 入口 | 地址 | 说明 |
|---|---|---|
| Grafana | http://localhost:3000 | 账号 `admin`,密码见 `.env` 的 `GRAFANA_ADMIN_PASSWORD`(默认 `admin`) |
| Prometheus | http://localhost:9090 | 查询 / 调试指标 |

内置「Linux 服务器监控」面板,展示 Node Exporter 采集的 CPU / 内存 / 负载 / 磁盘 / 网络 / 运行时间。

> 说明:Node Exporter 采集的是**运行 Docker 的那台机器**。部署在真实 Ubuntu 服务器上时就是服务器本身;在 Windows / Mac 本地开发时,采集到的是 Docker 虚拟机(Linux)的指标,属正常现象。
>
> 生产环境建议通过 Nginx + HTTPS 暴露 Grafana 并修改默认密码,Prometheus 无需对公网开放。

## 部署到服务器

```bash
# 在服务器上
git clone <你的仓库地址> /opt/personal-site
cd /opt/personal-site
cp .env.example .env   # 改密码
docker compose up -d --build
```

## 日常运维

```bash
# 查看容器状态
docker compose ps

# 看日志
docker compose logs -f web

# 数据库备份(配合 cron 定时执行)
bash scripts/backup.sh

# 重新部署(或 git push 触发 GitHub Actions 自动部署)
bash scripts/deploy.sh
```

建议给备份加定时任务:`crontab -e` 加一行 `0 3 * * * bash /opt/personal-site/scripts/backup.sh`(每天凌晨 3 点备份)。

## CI/CD

推送到 `main` 分支会自动触发 GitHub Actions:
1. `build` 作业:构建镜像,验证代码能正常打包
2. `deploy` 作业:SSH 到服务器执行 `git pull` + `docker compose up -d --build`

需要在仓库 Settings → Secrets 配置三个变量:`SERVER_HOST`、`SERVER_USER`、`SERVER_SSH_KEY`。

## 可以讲的点

- 用 `docker-compose` 编排多容器,`depends_on` + `healthcheck` 解决启动顺序
- Nginx 反向代理、`proxy_set_header` 透传真实 IP
- 数据库密码放 `.env`(不进 git),用 `MYSQL_PWD` 环境变量避免密码出现在命令行
- 备份脚本 `gzip` 压缩 + `find -mtime` 自动删除过期备份
- 前端做 HTML 转义防 XSS、后端做长度限制与空值校验
- `/healthz` 健康检查端点,供监控探活
- Prometheus `scrape_configs` 定时抓取 Node Exporter,`scrape_interval` 控制采集频率
- Grafana 用 provisioning 自动加载数据源与面板,新环境无需手动点配置
