# 🔄 プロジェクト復旧ノート

**最終更新: 2025-08-17 17:17 JST**

## 📊 現在の作業状況

### 完了済み
- ✅ データソースの信頼性評価完了
- ✅ Notionデータベース分析（1,750問確認）
- ✅ 元データ分析（1,850問）
- ✅ 完成形データ分析（2,000問）
- ✅ データ不整合の詳細特定

### 進行中
- 🔄 フェーズ1: web_displayで追加された150問の品質評価

### 待機中
- ⏳ フェーズ2: 1,850問+150問=2,000問の統合データセット作成
- ⏳ フェーズ3: Notion欠損251問の特定と復元
- ⏳ 最終: 2,000問の完全なデータベース構築

## 🎯 データ復元戦略

### データ現状
- **元データ（最も信頼）**: 1,850問（medical_exam_11~シリーズ）
- **完成形データ**: 2,000問（medical_exam_web_display_final.txt）
- **Notionデータベース**: 1,750問（構造化済み、250問不足）

### 3フェーズ復元計画
1. **フェーズ1**: 追加150問の品質評価と妥当性確認
2. **フェーズ2**: ベース1,850問 + 検証済み150問 = 2,000問統合
3. **フェーズ3**: Notion欠損251問を特定し、統合データから復元

## 🔧 実装済みツール

### 分析スクリプト
- `analyze_notion_data.py` - Notionデータベース分析
- `analyze_source_data.py` - ソースデータ詳細分析
- `data_discrepancy_analysis.py` - データ不整合分析
- `data_reliability_assessment.py` - データソース信頼性評価
- `analyze_added_questions.py` - 追加150問の詳細分析

### サポートツール
- `fetch_notion_data.py` - Notionデータ取得
- `quick_export_guide.md` - データエクスポートガイド

## 📁 データ構造

```
/workspaces/jmle-explanation-generator/
├── raw_data/
│   ├── source_texts/          # 元データ（5ファイル、各370問）
│   │   ├── medical_exam_115.txt
│   │   ├── medical_exam_116.txt
│   │   ├── medical_exam_117.txt
│   │   ├── medical_exam_118.txt
│   │   ├── medical_exam_119.txt
│   │   └── medical_exam_web_display_final.txt  # 完成形（2000問）
│   ├── cleaned_texts/         # クリーニング済み（6ファイル予定）
│   ├── notion/               # Notionエクスポート（1750問）
│   ├── exports/              # 出力用
│   └── backup/               # バックアップ用
├── [分析スクリプト群]
└── README.md
```

## 🚀 復旧時の手順

### 1. 環境確認
```bash
cd /workspaces/jmle-explanation-generator
git status
python --version
```

### 2. データ確認
```bash
python analyze_source_data.py      # ソースデータ状況確認
python data_reliability_assessment.py  # 信頼性評価
```

### 3. 作業再開
```bash
python analyze_added_questions.py  # フェーズ1続行
# 追加150問の品質評価結果を基に次フェーズへ
```

## 🎯 次回作業予定

1. **analyze_added_questions.py実行** - 追加150問の詳細分析
2. **品質評価結果確認** - 医学的妥当性と内容品質
3. **統合判断** - 2,000問データセット作成可否決定
4. **Notion復元計画** - 欠損251問の特定と復元

## 📞 重要な発見

- **データフロー**: 1,850問 → 2,000問 → 1,750問
- **主要課題**: 完成形で150問追加、Notionで251問欠損
- **信頼性順位**: medical_exam_11~ > web_display > Notion
- **復元可能性**: 高（完成形データが保存されている）

---
**次回セッション開始時**: このファイルを確認して作業を継続