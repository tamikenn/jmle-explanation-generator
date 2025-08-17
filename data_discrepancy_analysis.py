#!/usr/bin/env python3
"""
データ不整合の詳細分析スクリプト
"""
import re
import csv
from pathlib import Path
from collections import defaultdict

def extract_question_ids_from_text(file_path):
    """テキストファイルから問題IDを抽出"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
    ids = sorted(set(re.findall(pattern, content)))
    return ids

def extract_question_ids_from_csv(file_path):
    """CSVファイルから問題IDを抽出"""
    ids = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # BOMありの問題IDカラムを探す
            qid = None
            for key in row.keys():
                if '問題ID' in key:
                    qid = row[key]
                    break
            
            if qid and qid.strip() and qid != '問題ID':  # ヘッダー行を除外
                # 問題IDのパターンに一致するかチェック
                if re.match(r'\d{3}[A-Z]\d{1,3}', qid.strip()):
                    ids.append(qid.strip())
    return sorted(set(ids))

def analyze_data_discrepancies():
    """データ不整合の詳細分析"""
    print("🔍 データ不整合詳細分析")
    print("=" * 60)
    
    # パス設定
    source_dir = Path("/workspaces/jmle-explanation-generator/raw_data/source_texts")
    notion_dir = Path("/workspaces/jmle-explanation-generator/raw_data/notion")
    
    # 1. 元データファイルから問題ID抽出
    source_files = sorted(source_dir.glob("medical_exam_11*.txt"))
    source_files = [f for f in source_files if "web_display" not in f.name]
    
    all_source_ids = []
    source_by_year = defaultdict(list)
    
    print("\n📁 元データファイル分析:")
    for file in source_files:
        ids = extract_question_ids_from_text(file)
        all_source_ids.extend(ids)
        
        # 年度別に分類
        for qid in ids:
            year = qid[:3]
            source_by_year[year].append(qid)
        
        print(f"  {file.name}: {len(ids)}問")
    
    all_source_ids = sorted(set(all_source_ids))
    
    # 2. 完成形ファイルから問題ID抽出
    web_file = source_dir / "medical_exam_web_display_final.txt"
    web_ids = []
    if web_file.exists():
        web_ids = extract_question_ids_from_text(web_file)
    
    # 3. NotionCSVから問題ID抽出
    notion_files = list(notion_dir.glob("*.csv"))
    notion_ids = []
    if notion_files:
        notion_file = notion_files[0]  # 最初のCSVファイルを使用
        print(f"  Notionファイル: {notion_file.name}")
        notion_ids = extract_question_ids_from_csv(notion_file)
    
    # 4. 差異分析
    print(f"\n📊 データ数比較:")
    print(f"  元データ (source): {len(all_source_ids)}問")
    print(f"  完成形 (web): {len(web_ids)}問")
    print(f"  Notion: {len(notion_ids)}問")
    
    # 5. 完成形で増えた問題を特定
    extra_in_web = sorted(set(web_ids) - set(all_source_ids))
    missing_in_web = sorted(set(all_source_ids) - set(web_ids))
    
    print(f"\n🔍 完成形での変更:")
    print(f"  追加された問題: {len(extra_in_web)}問")
    if extra_in_web[:10]:
        print(f"  追加例: {extra_in_web[:10]}")
    
    print(f"  欠落した問題: {len(missing_in_web)}問")
    if missing_in_web[:10]:
        print(f"  欠落例: {missing_in_web[:10]}")
    
    # 6. Notionでの欠損を特定
    missing_in_notion = sorted(set(web_ids) - set(notion_ids))
    extra_in_notion = sorted(set(notion_ids) - set(web_ids))
    
    print(f"\n🔍 Notionでの変更:")
    print(f"  欠損問題: {len(missing_in_notion)}問")
    if missing_in_notion[:10]:
        print(f"  欠損例: {missing_in_notion[:10]}")
    
    print(f"  余分な問題: {len(extra_in_notion)}問")
    if extra_in_notion[:10]:
        print(f"  余分例: {extra_in_notion[:10]}")
    
    # 7. 年度別分析
    print(f"\n📅 年度別分析:")
    years = ['115', '116', '117', '118', '119']
    
    for year in years:
        source_count = len([qid for qid in all_source_ids if qid.startswith(year)])
        web_count = len([qid for qid in web_ids if qid.startswith(year)])
        notion_count = len([qid for qid in notion_ids if qid.startswith(year)])
        
        print(f"  第{year}回:")
        print(f"    元データ: {source_count}問")
        print(f"    完成形: {web_count}問")
        print(f"    Notion: {notion_count}問")
        
        if web_count != source_count:
            year_extra = [qid for qid in extra_in_web if qid.startswith(year)]
            year_missing = [qid for qid in missing_in_web if qid.startswith(year)]
            if year_extra:
                print(f"    追加: {len(year_extra)}問 {year_extra[:5]}")
            if year_missing:
                print(f"    欠落: {len(year_missing)}問 {year_missing[:5]}")
    
    # 8. 推奨アクション
    print(f"\n💡 推奨アクション:")
    print(f"  1. 完成形データ (2,000問) を基準とする")
    print(f"  2. Notionデータベースに欠損している {len(missing_in_notion)}問を補完")
    print(f"  3. 元データと完成形の差異 {len(extra_in_web)}問の追加理由を確認")
    
    return {
        'source_ids': all_source_ids,
        'web_ids': web_ids,
        'notion_ids': notion_ids,
        'missing_in_notion': missing_in_notion,
        'extra_in_web': extra_in_web
    }

if __name__ == "__main__":
    analyze_data_discrepancies()