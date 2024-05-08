# WORK-REPORT
日報管理システムの再構築

## 開発環境構築
```
docker-compose up -d
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser --noinput
```

## サンプル・マスタデータ（fixtures）の作り方
1. `./app/<アプリのディレクトリ>/fixtures/csv` にcsvファイルを格納する。ファイル名の規則はないが、テーブル名.csvが望ましい。ex. `task_items.csv`
    csvファイルの構成
    - model: <アプリ名>.クラス名　　　ex. `master.TaskItem`
    - pk: プライマリキーがauto_incrementの場合は省略可能。
    - プライマリキー以外の項目を順番に設定。`created_at` と `updated_at` の値は空白でよい。自動的に現在日時が設定される。
2. csvからjsonファイルを生成するコマンドを実行すると、`./app/<アプリのディレクトリ>/fixtures/`にjsonファイルが作成される。
    ```sh
    docker-compose exec app python make_fixtures.py <アプリ名> <csvファイル名(拡張子なし)> 
    
    # 例
    docker-compose exec app python make_fixtures.py master task_items 
    # 実行すると、./app/master/fixtures/task_item.json が生成される。
    ```
3. 生成したjsonファイルをロード
    ```sh
    docker-compose exec app python manage.py loaddata <jsonファイルのパス>

    # 例
    docker-compose exec app python manage.py loaddata master/fixtures/task_items.json
    ```