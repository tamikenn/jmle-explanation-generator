#!/usr/bin/env python3
"""
フェーズ3: Notion欠損251問の特定と復元戦略
"""
import re
import csv
from pathlib import Path
from collections import defaultdict

def restore_missing_notion_data():
    """Notion欠損データの特定と復元"""
    print("🔍 Notion欠損データ復元（フェーズ3）")
    print("=" * 60)
    
    # パス設定
    exports_dir = Path("/workspaces/jmle-explanation-generator/raw_data/exports")
    notion_dir = Path("/workspaces/jmle-explanation-generator/raw_data/notion")
    
    # 1. 統合データセット読み込み
    print("\n📊 ステップ1: 統合データセット読み込み")
    print("-" * 40)
    
    integrated_csv = exports_dir / "integrated_dataset_2000.csv"
    integrated_questions = {}
    
    if integrated_csv.exists():
        with open(integrated_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row['問題ID']
                integrated_questions[qid] = row
        
        print(f"  統合データセット読み込み完了: {len(integrated_questions)}問")
    else:
        print("  ❌ 統合データセットが見つかりません")
        return
    
    # 2. 現在のNotionデータベース読み込み
    print("\n📊 ステップ2: 現在のNotionデータベース読み込み")
    print("-" * 40)
    
    notion_files = list(notion_dir.glob("*.csv"))
    notion_questions = {}
    
    if notion_files:
        notion_file = notion_files[0]
        print(f"  読み込み中: {notion_file.name}")
        
        with open(notion_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 問題IDカラムを探す
                qid = None
                for key in row.keys():
                    if '問題ID' in key:
                        qid = row[key]
                        break
                
                if qid and qid.strip() and re.match(r'\d{3}[A-Z]\d{1,3}', qid.strip()):
                    notion_questions[qid.strip()] = row
        
        print(f"  Notionデータベース読み込み完了: {len(notion_questions)}問")
    else:
        print("  ❌ Notionデータベースが見つかりません")
        return
    
    # 3. 欠損問題の特定
    print("\n🔍 ステップ3: 欠損問題の特定")
    print("-" * 40)
    
    missing_questions = []
    existing_questions = []
    
    for qid in integrated_questions.keys():
        if qid in notion_questions:
            existing_questions.append(qid)
        else:
            missing_questions.append(qid)
    
    missing_questions.sort()
    existing_questions.sort()
    
    print(f"  統合データセット: {len(integrated_questions)}問")
    print(f"  Notionに存在: {len(existing_questions)}問")
    print(f"  Notionに欠損: {len(missing_questions)}問")
    
    # 4. 欠損パターン分析
    print("\n📈 ステップ4: 欠損パターン分析")
    print("-" * 40)
    
    missing_by_year = defaultdict(list)
    missing_by_section = defaultdict(list)
    
    for qid in missing_questions:
        year = qid[:3]
        section = qid[3]
        missing_by_year[year].append(qid)
        missing_by_section[section].append(qid)
    
    print("  年度別欠損:")
    for year in sorted(missing_by_year.keys()):
        count = len(missing_by_year[year])
        print(f"    第{year}回: {count}問")
        
        # サンプル表示
        if missing_by_year[year][:5]:
            print(f"      例: {missing_by_year[year][:5]}")
    
    print("\n  セクション別欠損:")
    for section in sorted(missing_by_section.keys()):
        count = len(missing_by_section[section])
        print(f"    セクション{section}: {count}問")
    
    # 5. 復元可能性評価
    print("\n🔬 ステップ5: 復元可能性評価")
    print("-" * 40)
    
    # 統合データセットから復元可能かチェック
    restorable_count = 0
    restorable_data = {}
    
    for qid in missing_questions:
        if qid in integrated_questions:
            restorable_count += 1
            restorable_data[qid] = integrated_questions[qid]
    
    print(f"  復元可能な問題: {restorable_count}問")
    print(f"  復元不可能な問題: {len(missing_questions) - restorable_count}問")
    
    if restorable_count > 0:
        print(f"  復元成功率: {restorable_count / len(missing_questions) * 100:.1f}%")
    
    # 6. 復元データ作成
    print("\n🛠️ ステップ6: 復元データ作成")
    print("-" * 40)
    
    if restorable_count > 0:
        # 復元用CSVファイル作成
        restore_csv = exports_dir / "notion_missing_questions_restore.csv"
        
        # Notionの既存構造を参考にヘッダー作成
        if notion_questions:
            sample_notion = list(notion_questions.values())[0]
            notion_headers = list(sample_notion.keys())
        else:
            notion_headers = ['問題ID', '年度', 'セクション', '問題番号', '正答', '正答率', 
                            '英語問題', '画像問題', '連問', '計算問題', '問題文', '症例文', 
                            '選択肢', 'Web表示用', 'タグ', '最終更新']
        
        with open(restore_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=notion_headers)
            writer.writeheader()
            
            for qid in sorted(restorable_data.keys()):
                integrated_data = restorable_data[qid]
                
                # Notion形式にマッピング
                notion_row = {}
                for header in notion_headers:
                    if '問題ID' in header:
                        notion_row[header] = qid
                    elif '年度' in header:
                        notion_row[header] = qid[:3]
                    elif 'セクション' in header:
                        notion_row[header] = qid[3]
                    elif '問題番号' in header:
                        notion_row[header] = qid[4:]
                    elif 'Web表示用' in header or 'コンテンツ' in header:
                        notion_row[header] = integrated_data.get('コンテンツ', '')
                    else:
                        notion_row[header] = ''  # デフォルト空白
                
                writer.writerow(notion_row)
        
        print(f"  復元データ作成完了: {restore_csv}")
        
        # 復元手順書作成
        instructions_file = exports_dir / "notion_restore_instructions.md"
        
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write("# Notionデータベース復元手順書\n\n")
            f.write(f"## 📊 復元対象\n")
            f.write(f"- 欠損問題数: {len(missing_questions)}問\n")
            f.write(f"- 復元可能数: {restorable_count}問\n")
            f.write(f"- 復元成功率: {restorable_count / len(missing_questions) * 100:.1f}%\n\n")
            
            f.write("## 📁 復元ファイル\n")
            f.write(f"- 復元データ: `{restore_csv.name}`\n")
            f.write(f"- 手順書: `{instructions_file.name}`\n\n")
            
            f.write("## 🔧 復元手順\n")
            f.write("1. Notionデータベースを開く\n")
            f.write("2. 右上の「...」メニューから「Import」を選択\n")
            f.write("3. CSV形式を選択\n")
            f.write(f"4. `{restore_csv.name}`をアップロード\n")
            f.write("5. マッピング確認後、インポート実行\n\n")
            
            f.write("## 📈 復元後の確認\n")
            f.write("- 総問題数が2000問になることを確認\n")
            f.write("- 各年度400問になることを確認\n")
            f.write("- 重複がないことを確認\n\n")
            
            f.write("## 📝 年度別復元内訳\n")
            for year in sorted(missing_by_year.keys()):
                restorable_year = len([q for q in missing_by_year[year] if q in restorable_data])
                f.write(f"- 第{year}回: {restorable_year}/{len(missing_by_year[year])}問復元可能\n")
        
        print(f"  復元手順書作成完了: {instructions_file}")
    
    # 7. 最終レポート
    print("\n📋 ステップ7: 最終レポート")
    print("-" * 40)
    
    report_file = exports_dir / "notion_restoration_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Notionデータベース復元レポート\n\n")
        f.write("## データ状況\n")
        f.write(f"統合データセット: {len(integrated_questions)}問\n")
        f.write(f"Notion既存データ: {len(existing_questions)}問\n")
        f.write(f"Notion欠損データ: {len(missing_questions)}問\n")
        f.write(f"復元可能データ: {restorable_count}問\n\n")
        
        f.write("## 復元成功率\n")
        if missing_questions:
            f.write(f"{restorable_count / len(missing_questions) * 100:.1f}%\n\n")
        
        f.write("## 年度別欠損内訳\n")
        for year in sorted(missing_by_year.keys()):
            restorable_year = len([q for q in missing_by_year[year] if q in restorable_data])
            f.write(f"第{year}回: {len(missing_by_year[year])}問欠損 ({restorable_year}問復元可能)\n")
        
        f.write("\n## セクション別欠損内訳\n")
        for section in sorted(missing_by_section.keys()):
            f.write(f"セクション{section}: {len(missing_by_section[section])}問\n")
        
        f.write("\n## 欠損問題ID一覧\n")
        for qid in missing_questions[:50]:  # 最初の50問を記載
            f.write(f"{qid}\n")
        
        if len(missing_questions) > 50:
            f.write(f"... および他{len(missing_questions) - 50}問\n")
    
    print(f"  最終レポート作成完了: {report_file}")
    
    # 8. 成功サマリー
    print("\n🎉 ステップ8: 復元戦略完了")
    print("-" * 40)
    
    print("  ✅ Notion欠損データ分析完了")
    print(f"  📊 復元可能: {restorable_count}/{len(missing_questions)}問")
    
    if restorable_count == len(missing_questions):
        print("  🎯 100%復元可能！完全復旧が実現可能")
    elif restorable_count > len(missing_questions) * 0.9:
        print("  🔥 90%以上復元可能！ほぼ完全復旧が可能")
    else:
        print(f"  📈 {restorable_count / len(missing_questions) * 100:.1f}%復元可能")
    
    print("\n  📁 出力ファイル:")
    if restorable_count > 0:
        print(f"     - {restore_csv.name} (復元データ)")
        print(f"     - {instructions_file.name} (復元手順)")
    print(f"     - {report_file.name} (詳細レポート)")
    
    return {
        'missing_count': len(missing_questions),
        'restorable_count': restorable_count,
        'success_rate': restorable_count / len(missing_questions) if missing_questions else 0,
        'missing_by_year': dict(missing_by_year)
    }

if __name__ == "__main__":
    restore_missing_notion_data()