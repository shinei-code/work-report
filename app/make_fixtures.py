import pandas
import json
import os
import sys
from datetime import datetime as dt

now_datetime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

args = sys.argv

if len(args) >= 3:
    app_name = args[1]
    file_name = args[2]
else:
    sys.exit("ERROR! 引数にアプリ名とCSVファイル名を指定してください")

csv_file_path = f'./{app_name}/fixtures/csv/{file_name}.csv'
fixtures_directory =  f'./{app_name}/fixtures'

if not os.path.exists(csv_file_path):
    sys.exit(f"CSVファイルが存在しません {csv_file_path}")

df = pandas.read_csv(csv_file_path, dtype=str) 
df = df.fillna("")

fixtures_data = []
for _, row in df.iterrows():
    
    fixture = {
        'model': "",
        'fields': {}
    }
    
    for key in row.index:
        if 'model' == key:
            fixture["model"] = row[key]
        elif 'pk' == key:
            fixture["pk"] = row[key]
        elif key in ['created_at', 'updated_at']:
            fixture["fields"][key] = now_datetime
        else:
            fixture["fields"][key] = str(row[key]) if str(row[key]) else None

    fixtures_data.append(fixture)

fixtures_filename = f"{file_name}.json"
fixtures_file_path = os.path.join(fixtures_directory, fixtures_filename)
with open(fixtures_file_path, 'w', encoding='utf-8') as outfile:
    json.dump(fixtures_data, outfile, ensure_ascii=False, indent=4)

print(f"Fixtures作成が完了しました   {csv_file_path} >>> {fixtures_file_path}")
