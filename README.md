douban2kindle
=============

豆瓣阅读图书推送 Kindle，使用 Django 开发。

功能和代码参考了 [@jacksyen](https://github.com/jacksyen) 的 [gk7-douban](https://github.com/jacksyen/gk7-douban) 项目，Thanks a lot.

## 安装

clone 代码到本地：

```bash
git clone git@github.com:messense/douban2kindle.git
```

推荐使用 `virtualenv` 安装部署：

```bash
cd douban2kindle
virtualenv .
source bin/activate
pip install -r requirements.txt
```

系统软件包依赖：

1. RabbitMQ 消息队列系统（可使用 Redis 替代）
2. Redis
3. Calibre

## 运行

启动服务器端：

```bash
cd douban2kindle
# migrate database
python manage.py migrate
# run server
python manage.py runserver 0.0.0.0:9999
```

启动 Celery 任务队列：

```bash
cd douban2kindle
celery -A douban2kindle worker -l info
```

## Chrome 客户端
Chrome 客户端代码在 client 文件夹中，通过开发中模式加载。

1. 修改插件推送的后台地址 URL，编辑 client/scripts/background.js，在 send 函数中修改 URL 地址，和上面服务器端启动的 IP /端口对应
2. 在chrome浏览器中的地址栏中输入：chrome://extensions/，点击 加载正在开发的扩展程序，选择 client 文件夹即可
