# hrtool

## インストール

あらかじめ [python](https://www.python.org) と [git](https://git-scm.com) をインストールしておいてください。
その上で適当なディレクトリで以下を実行してください。

```bash
$ git clone https://github.com/m-hilaga/hrtool
$ cd hrtool
$ pip install -r requests.txt
```

## salary_rating.py

年俸偏差値を計算します。  
入力はCSVファイルで左の列から `"社員ID", "社員名", "誕生年月日(YYYY/mm/dd)", "年齢", "年俸"` の形式で、  
出力は以下の3つのCSVファイルになります。
- 年俸偏差値 (ファイル名 `????_salary_rating.csv`)は `"社員ID", "社員名", "年俸偏差値"` の形式で、
- 年齢毎年俸 (ファイル名 `????_salary_by_age.csv`)は `"年齢", "年俸平均", "年俸標準偏差"` の形式で、
- 年代別年俸 (ファイル名 `????_salary_stats.csv`)は `"年代", "年齢平均", "年俸平均", "年俸標準偏差"` の形式で

出力されます。

### 実行例
```
$ python ./salary_rating.py input.csv
```
