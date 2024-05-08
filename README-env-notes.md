# 開発環境構築の記録
dockerコンテナからdjango初期設定の記録s

## 構造（初期状態）
以下の通り作成
```
work-report
├── app
├── db
├── docker
│   └── app
│       ├── Dockerfile
│       └── requirements.txt
├── .env
└── docker-compose.yml
```

## 各ファイルの内容

**docker-compose.yml**
```yml
version: '3.8'

services:
  app:
    build: ./docker/app
    ports:
      - "${APP_PORT}:8000"
    volumes:
      - ./app:/app
    command: python manage.py runserver 0.0.0.0:8000
    environment:
      DB_HOST: ${DB_HOST}
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      TZ: 'Asia/Tokyo'
    depends_on:
      - db
  db:
    image: mysql:8
    platform: linux/x86_64
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      TZ: 'Asia/Tokyo'
    ports:
      - "${DB_PORT}:3306"
    volumes:
      - db_data:/var/lib/mysql

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    restart: always
    environment:
      PMA_ARBITRARY: 1
      PMA_HOSTS: ${DB_HOST}
      PMA_USER: ${DB_USER}
      PMA_PASSWORD: ${DB_PASSWORD}
    ports:
      - "${PHPMYADMIN_PORT}:80"
    depends_on:
      - db

volumes:
  db_data:
```

**.env**
```
# DB
DB_HOST="db"
DB_ROOT_PASSWORD="secret"
DB_NAME="work-report"
DB_USER="omc"
DB_PASSWORD="secret"

# ports
APP_PORT="8001"
DB_PORT="3307"
PHPMYADMIN_PORT="8080"
```

**./docker/app/Dockerfile**
```
FROM python:3.11
ENV PYTHONBURRERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt
```

**./docker/app/requirements.txt**
```
Django==4.2
mysqlclient
python-decouple
```

## コンテナのビルド
```sh
docker-compose build
```

## djangoプロジェクトとアプリを作成
```
docker-compose run --rm app django-admin startproject config .
docker-compose exec app python manage.py startapp report
docker-compose exec app python manage.py startapp master
```

実行すると、appフォルダにdjangoのファイルが生成される
```
work-report
├─ app
│   ├─ config
│   │   ├─ __init__.py
│   │   ├─ __pycache__
│   │   │   ├─ __init__.cpython-311.pyc
│   │   │   ├─ settings.cpython-311.pyc
│   │   │   ├─ urls.cpython-311.pyc
│   │   │   └─ wsgi.cpython-311.pyc
│   │   ├─ asgi.py
│   │   ├─ settings.py
│   │   ├─ urls.py
│   │   └─ wsgi.py
│   ├── manage.py
│   ├── report
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   └── master
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       │   └── __init__.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
├─ db
├─ docker
│   └─ app
│        ├─ Dockerfile
│        └─ requirements.txt
├─ .env
└─ docker-compose.yml
```

djangoにDB接続設定などを記述する
./app/config/settings.py
```python
import os  # 追加

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'report',  # 追加
    'master',  # 追加
]

LANGUAGE_CODE = 'ja'  # 初期設定 'en-us'
TIME_ZONE = 'Asia/Tokyo'  # 初期設定 'UTC'
USE_TZ = False  # 初期設定 'True'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],  # 元は 'DIRS: [],'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# 初期設定はsqlite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

# mysqlに変更
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': 3306,
    }
}
```
./app/config/urls.py
```python
from django.contrib import admin
from django.urls import path, include   # includeを追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('report.urls')),   # 追加
]
```
./app/report/views.py
```python
from django.shortcuts import render
# これを追加 ↓↓↓
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "report/index.html"
# これを追加 ↑↑↑
```
./app/report/urls.py  (新規作成)
```python
from django.urls import path

from . import views


app_name = "report"
urlpatterns = [
    path('top/', views.IndexView.as_view(), name='index'),
]
```

./app/template/ (フォルダを新規作成)
./app/template/base.html (新規作成)
```django
# プロジェクト全体のベースとなるhtml
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{% block title %}{% endblock %}</title>
  </head>
  <body>
    <div class="container">
      {% block content %}{% endblock %}
    </div>
  </body>
</html>
```

./app/template/report (フォルダを新規作成)
./app/template/report/index.html (新規作成)
```django
{% extends "base.html" %}
{% block title %}トップページ{% endblock %}

{% block content %}
<h1>トップページ</h1>
<p><a href="">topのページだよ！</a></p>
{% endblock %}
```


## コンテナを起動
```
docker-compose up -d
```
おそらくappコンテナで以下のようなエラーが発生するはず
> django.db.utils.OperationalError: (2002, "Can't connect to server on 'db' (115)")

**原因:** dbコンテナ（mysql）が上がりきらないうちにapp（django）を起動してしまい、DBに接続できなかった。

docker-compse.ymlにはdbコンテナの起動を待ってappコンテナを起動する設定にしているが、、、
```yml
services:
  app:
    // ~~ 省略 ~~
    depends_on:
      - db  // dbコンテナの起動を待つ
```
`depends_on: db` でdbコンテナ起動を待つことになっているが、dbコンテナだけでなく、dbコンテナの中のmysqlサービスの起動を待つ必要がある。

**対応**
docker-compose.ymlを修正
```yml
services:
  app:
    // ~~ 省略 ~~
    depends_on:
      db:
        condition: service_healthy  // dbコンテナのヘルスチェックOKを待機
		
  db:
    // ~~ 省略 ~~
    healthcheck:  // ヘルスチェックを追加
      test: ["CMD", "mysqladmin" ,"ping", "-h", "localhost"]
      interval: 3s
      timeout: 3s
      retries: 5
      start_period: 3s
```

コンテナをリビルドし、再起動
```
docker-compose stop
docker-compose build
docker-compose up -d
```

## 起動確認
djangoのwelcomeページ: http://localhost:8001
phpMyAdmin: http://localhost:8080

## django初期マイグレーション
```
docker-compose exec app python manage.py migrate
```

## djangoスーパーユーザー作成
.envから
```
docker-compose exec app python manage.py createsuperuser --noinput
```

## bootstrap5, bootstrap-icon導入
./docker/app/requirements.txt
```
Django==4.2
mysqlclient==2.2.1
django-bootstrap5  # 追加
django-bootstrap-icons5  # 追加
```

./app/config/settings.py
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'report',
    'master',
    'django_bootstrap5',  # 追記
    'django_bootstrap_icons',  # 追記
]
```
./app/templates/base.html
```django
{% load django_bootstrap5 %}  {# 追加 #} 
{% load bootstrap_icons %}  {# 追加 #} 

<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% bootstrap_css %}  {# 追加 #} 
    {% bootstrap_javascript %}  {# 追加 #} 
    <title>{% block title %}{% endblock %}</title>
  </head>
  <body>
    <div class="container">
      {% block content %}{% endblock %}
    </div>
  </body>
</html>
```

リビルド & コンテナ再起動
```
docker-compose up -d --build
```

bootstrapアイコンの使い方
```django
<span>{% bs_icon 'person-circle' %}</span>
```

## デバッグツール導入
./docker/app/requirements.txt
```
django-debug-toolbar  # 追加
```

./app/config/settings.py
```python
import socket  # 追加

INSTALLED_APPS = [
    ...
    'debug_toolbar',  # 追加
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # 追加

]

# 追加 ↓↓↓
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1']
# 追加 ↑↑↑
```

./app/config/urls.py
```python
from django.contrib import admin
from django.urls import path, include 
import debug_toolbar
from django.conf import settings  # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('report.urls')),
]

# 追加 ↓↓↓
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
# 追加 ↑↑↑
```

リビルド & コンテナ再起動
```
docker-compose up -d --build
```

## Sass導入
参考: https://417.run/pg/python/django/scss/

./docker/app/requirements.txt
```python
libsass  # 追加
django-compressor  # 追加
django-sass-processor  # 追加
```

./app/config/settings.py
```python
INSTALLED_APPS = [
    ...
    'sass_processor',  # 追記
]

# 追記 ↓↓↓
# static フォルダの設定
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

# Sass/SCSS
SASS_PROCESSOR_AUTO_INCLUDE = False
SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'static')
SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.(sass|scss)$'
SASS_PRECISION = 8
SASS_OUTPUT_STYLE = 'compressed'
SASS_TEMPLATE_EXTS = ['.html', '.haml']
# 追記 ↑↑↑
```

リビルド & コンテナ再起動
```
docker-compose up -d --build
```

./app/templates/base.html
```django
{% load django_bootstrap5 %}
{% load bootstrap_icons %}
{% load static %}  {# 追記 #}
{% load sass_tags %}   {# 追記 #}

<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% bootstrap_css %}
    {% bootstrap_javascript %}
    <link rel="stylesheet" href="{% sass_src 'css/style.scss' %}" type="text/css">   {# 追記 #}
    <title>{% block title %}{% endblock %}</title>
  </head>
...
```
./app/static/style.scss にscss記法で記述すると、同じフォルダに `style.css`, `style.css.map` が出力される。
```scss
// サンプル
body {
  color: green;
}
```

本番リリース時
- コンパイル `python manage.py compilescss`
- 公開フォルダに移動 `python manage.py collectstatic`

## google fonts 導入
1. 公式サイトからフォントファイルをダウンロード
    https://fonts.google.com/
2. ダウンロードしたフォントファイルを `./app/static/fonts` に配置
3. スタイルシートで読み込み ＆ 適用
    ```scss
    // 使用例
    @font-face {
      font-family: 'MPLUSRounded';
      src: url('/static/fonts/MPLUSRounded1c-ExtraBold.ttf') format('truetype');
    }

    body {
      font-family: "MPLUSRounded";
    }
    ```

## bootstrap icon 導入
前述した `pip install django-bootstrap-icons5` で導入したアイコンは画面表示のパフォーマンスが悪かった。公式サイトからアイコンセットをダウンロードし、staticフォルダに格納して対応した。

githubからzipダウンロード
https://github.com/twbs/icons/releases/tag/{バージョン}
bootstrap-icons-{バージョン}.zip

ダウンロード後解凍したフォルごと、staticに配置。
フォルダ名を `bs-icons`とした。

headタグでcssを読み込む
```html
<link rel="stylesheet" href="{% static 'bs-icons/font/bootstrap-icons.min.css' %}" type="text/css">
```

テンプレートで使用
```html
<i class="bi bi-alarm"></i>
```

## bootstrap 導入
前述した `pip install django-bootstrap5` はCDN経由であるため、ダウンロード版に切り替える。

githubからzipダウンロード
https://getbootstrap.jp/docs/5.3/getting-started/download/#コンパイルされたcssとjs

ダウンロード後解凍し、jsとcssのフォルごと、staticに配置。

cssとjsの読み込み
```html
<head>
  ...
  <!-- BootstrapのCSS読み込み -->
  <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet" />
  ...
</head>
<body>
  ...
  <!-- BootstrapのJS読み込み -->
  <script src="{% static 'js/bootstrap.min.js' %}"></script>
</body>
```

## AlpineJS導入
ダウンロード版がないため、headタグにcdnを挿入

## フラッシュメッセージのタグ変更
djangoデフォルトは `error` が出力される
`error` のままだと、bootstrapが適用されないので、bootstrapに合わせて変更

settings.py
```python
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'dark',
    messages.ERROR: 'danger',
}
```