#!/usr/bin/env python3
"""
フェーズ2: 1850問 + 150問 = 2000問の統合データセット作成
"""
import re
import csv
from pathlib import Path
from collections import defaultdict, OrderedDict

def create_integrated_dataset():
    """統合データセット作成"""
    print("🔧 統合データセット作成（フェーズ2）")
    print("=" * 60)
    
    source_dir = Path("/workspaces/jmle-explanation-generator/raw_data/source_texts")
    output_dir = Path("/workspaces/jmle-explanation-generator/raw_data/exports")
    output_dir.mkdir(exist_ok=True)
    
    # 1. ベースデータ（1850問）の抽出
    print("\n📁 ステップ1: ベースデータ（1850問）抽出")
    print("-" * 40)
    
    base_questions = {}
    source_files = sorted([f for f in source_dir.glob("medical_exam_11*.txt") 
                          if "web_display" not in f.name])
    
    for file in source_files:
        print(f"  処理中: {file.name}")
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 問題IDパターンで分割
            pattern = r'(\d{3}[A-Z]\d{1,3})'
            parts = re.split(pattern, content)
            
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    qid = parts[i]
                    text = parts[i + 1]
                    
                    # テキストのクリーニング
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)
                    
                    if clean_text and re.match(r'\d{3}[A-Z]\d{1,3}', qid):
                        base_questions[qid] = {
                            'id': qid,
                            'source': 'base_data',
                            'content': clean_text[:1000],  # 長すぎる場合は制限
                            'year': qid[:3],
                            'section': qid[3],
                            'number': qid[4:]
                        }
    
    print(f"  ベースデータ抽出完了: {len(base_questions)}問")
    
    # 2. 追加データ（150問）の抽出
    print("\n📁 ステップ2: 追加データ（150問）抽出")
    print("-" * 40)
    
    web_file = source_dir / "medical_exam_web_display_final.txt"
    added_questions = {}
    
    if web_file.exists():
        with open(web_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 全問題IDを抽出
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            all_web_ids = sorted(set(re.findall(pattern, content)))
            
            # 追加問題のみを特定
            added_ids = sorted(set(all_web_ids) - set(base_questions.keys()))
            
            print(f"  追加問題特定: {len(added_ids)}問")
            
            # 追加問題のコンテンツ抽出
            for qid in added_ids:
                # 該当問題の内容を抽出
                qid_pattern = fr'{re.escape(qid)}.*?(?=\d{{3}}[A-Z]\d{{1,3}}|$)'
                match = re.search(qid_pattern, content, re.DOTALL)
                
                if match:
                    text = match.group(0)
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)
                    
                    added_questions[qid] = {
                        'id': qid,
                        'source': 'web_display_added',
                        'content': clean_text[:1000],
                        'year': qid[:3],
                        'section': qid[3],
                        'number': qid[4:]
                    }
    
    print(f"  追加データ抽出完了: {len(added_questions)}問")
    
    # 3. データ統合
    print("\n🔗 ステップ3: データ統合")
    print("-" * 40)
    
    # 統合データセット作成
    integrated_dataset = {}
    integrated_dataset.update(base_questions)
    integrated_dataset.update(added_questions)
    
    print(f"  統合完了:")
    print(f"    ベースデータ: {len(base_questions)}問")
    print(f"    追加データ: {len(added_questions)}問")
    print(f"    統合合計: {len(integrated_dataset)}問")
    
    # 4. 品質チェック
    print("\n✅ ステップ4: 品質チェック")
    print("-" * 40)
    
    # 年度別確認
    by_year = defaultdict(list)
    for qid, data in integrated_dataset.items():
        by_year[data['year']].append(qid)
    
    for year in sorted(by_year.keys()):
        year_count = len(by_year[year])
        base_count = len([q for q in by_year[year] if q in base_questions])
        added_count = len([q for q in by_year[year] if q in added_questions])
        
        print(f"  第{year}回: {year_count}問 (ベース:{base_count} + 追加:{added_count})")
    
    # 重複チェック
    all_ids = list(integrated_dataset.keys())
    unique_ids = set(all_ids)
    if len(all_ids) != len(unique_ids):
        print(f"  ⚠️  重複あり: {len(all_ids) - len(unique_ids)}問")
    else:
        print(f"  ✅ 重複なし")
    
    # 欠番チェック
    missing_sequences = []
    for year in ['115', '116', '117', '118', '119']:
        year_ids = [qid for qid in all_ids if qid.startswith(year)]
        
        # セクション別チェック
        for section in ['A', 'B', 'C', 'D', 'E', 'F']:
            section_ids = [qid for qid in year_ids if qid[3] == section]
            if section_ids:
                numbers = sorted([int(re.search(r'(\d+)$', qid).group(1)) for qid in section_ids])
                for i in range(min(numbers), max(numbers) + 1):
                    expected_id = f"{year}{section}{i}"
                    if expected_id not in section_ids:
                        missing_sequences.append(expected_id)
    
    if missing_sequences:
        print(f"  ⚠️  欠番検出: {len(missing_sequences)}問")
        print(f"     例: {missing_sequences[:10]}")
    else:
        print(f"  ✅ 欠番なし")
    
    # 5. 出力ファイル作成
    print("\n💾 ステップ5: 統合データセット出力")
    print("-" * 40)
    
    # CSV形式で出力
    output_csv = output_dir / "integrated_dataset_2000.csv"
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['問題ID', '年度', 'セクション', '問題番号', 'ソース', 'コンテンツ']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for qid in sorted(integrated_dataset.keys()):
            data = integrated_dataset[qid]
            writer.writerow({
                '問題ID': data['id'],
                '年度': data['year'],
                'セクション': data['section'],
                '問題番号': data['number'],
                'ソース': data['source'],
                'コンテンツ': data['content']
            })
    
    print(f"  CSV出力完了: {output_csv}")
    
    # テキスト形式でサマリー出力
    summary_file = output_dir / "integration_summary.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 統合データセット作成サマリー\n\n")
        f.write(f"作成日時: {Path().cwd()}\n")
        f.write(f"総問題数: {len(integrated_dataset)}問\n\n")
        f.write("## 年度別内訳\n")
        
        for year in sorted(by_year.keys()):
            year_count = len(by_year[year])
            base_count = len([q for q in by_year[year] if q in base_questions])
            added_count = len([q for q in by_year[year] if q in added_questions])
            f.write(f"第{year}回: {year_count}問 (ベース:{base_count} + 追加:{added_count})\n")
        
        f.write(f"\n## データソース\n")
        f.write(f"ベースデータ: {len(base_questions)}問 (medical_exam_11~シリーズ)\n")
        f.write(f"追加データ: {len(added_questions)}問 (web_display_final)\n")
        
        if missing_sequences:
            f.write(f"\n## 欠番\n")
            for missing in missing_sequences[:20]:
                f.write(f"{missing}\n")
    
    print(f"  サマリー出力完了: {summary_file}")
    
    # 6. 次フェーズへの準備
    print("\n🚀 ステップ6: フェーズ3準備")
    print("-" * 40)
    
    print("  ✅ 統合データセット作成完了")
    print("  📋 次のフェーズ: Notion欠損251問の特定と復元")
    print("  📁 出力ファイル:")
    print(f"     - {output_csv.name} (CSV形式)")
    print(f"     - {summary_file.name} (サマリー)")
    
    return {
        'total_questions': len(integrated_dataset),
        'base_questions': len(base_questions),
        'added_questions': len(added_questions),
        'output_csv': output_csv,
        'missing_sequences': missing_sequences
    }

if __name__ == "__main__":
    create_integrated_dataset()