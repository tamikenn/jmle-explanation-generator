# Raw Data フォルダ

このフォルダにNotionやその他のソースからのデータを配置してください。

## 📁 フォルダ構造

```
raw_data/
├── notion/      # Notionからエクスポートしたファイル（CSV、Markdown等）
├── exports/     # その他のエクスポートファイル
└── backup/      # バックアップファイル
```

## 📝 ファイルの配置方法

### 1. VSCodeのエクスプローラーから
- 左側のファイルツリーで `raw_data` フォルダを開く
- 該当するサブフォルダにファイルをドラッグ&ドロップ

### 2. ターミナルから
```bash
# 例：NotionのCSVファイルを配置
cp ~/Downloads/notion_export.csv /workspaces/jmle-explanation-generator/raw_data/notion/
```

### 3. 直接作成
- 該当フォルダ内で右クリック → 「New File」
- データを貼り付けて保存

## 🎯 推奨ファイル名

- `notion_database.csv` - Notionデータベースのエクスポート
- `problems_list.txt` - 問題リスト
- `answers.json` - 解答データ
- `explanations.md` - 解説テキスト

## 🔄 自動処理

ファイルを配置すると自動的に：
1. データの分析
2. 欠番の特定
3. 復旧スクリプトの生成

が実行されます。