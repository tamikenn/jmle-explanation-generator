#!/usr/bin/env python3
"""
最終フェーズ: 2000問の完全なデータベース構築（修正版）
"""
import re
import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def build_complete_database():
    """2000問の完全なデータベース構築"""
    print("🏗️ 完全データベース構築（最終フェーズ）")
    print("=" * 60)
    
    # パス設定
    exports_dir = Path("/workspaces/jmle-explanation-generator/raw_data/exports")
    notion_dir = Path("/workspaces/jmle-explanation-generator/raw_data/notion")
    final_dir = Path("/workspaces/jmle-explanation-generator/final_database")
    final_dir.mkdir(exist_ok=True)
    
    # 1. 統合データセット読み込み
    print("\n📊 ステップ1: データソース読み込み")
    print("-" * 40)
    
    # 統合データセット
    integrated_csv = exports_dir / "integrated_dataset_2000.csv"
    integrated_data = {}
    
    if integrated_csv.exists():
        with open(integrated_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row['問題ID']
                integrated_data[qid] = row
        print(f"  統合データセット: {len(integrated_data)}問")
    
    # 既存Notionデータ
    notion_files = list(notion_dir.glob("*.csv"))
    existing_notion = {}
    
    if notion_files:
        with open(notion_files[0], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = None
                for key in row.keys():
                    if '問題ID' in key:
                        qid = row[key]
                        break
                
                if qid and qid.strip() and re.match(r'\d{3}[A-Z]\d{1,3}', qid.strip()):
                    existing_notion[qid.strip()] = row
        print(f"  既存Notionデータ: {len(existing_notion)}問")
    
    # 復元データ
    restore_csv = exports_dir / "notion_missing_questions_restore.csv"
    restore_data = {}
    
    if restore_csv.exists():
        with open(restore_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = None
                for key in row.keys():
                    if '問題ID' in key:
                        qid = row[key]
                        break
                
                if qid and qid.strip():
                    restore_data[qid.strip()] = row
        print(f"  復元データ: {len(restore_data)}問")
    
    # 2. データベース統合
    print("\n🔗 ステップ2: データベース統合")
    print("-" * 40)
    
    complete_database = {}
    
    # 統合データセットの全問題を基準とする
    for qid in sorted(integrated_data.keys()):
        # 基本情報
        integrated_row = integrated_data[qid]
        
        # 完全な記録作成
        complete_record = {
            '問題ID': qid,
            '年度': qid[:3],
            'セクション': qid[3],
            '問題番号': qid[4:],
            'ソース': integrated_row.get('ソース', ''),
            'コンテンツ': integrated_row.get('コンテンツ', ''),
            'データ状態': 'complete'
        }
        
        # Notionの詳細データがある場合は統合
        if qid in existing_notion:
            notion_row = existing_notion[qid]
            complete_record['正答'] = notion_row.get('正答', '')
            complete_record['正答率'] = notion_row.get('正答率', '')
            complete_record['英語問題'] = notion_row.get('英語問題', 'No')
            complete_record['画像問題'] = notion_row.get('画像問題', 'No')
            complete_record['連問'] = notion_row.get('連問', 'No')
            complete_record['計算問題'] = notion_row.get('計算問題', 'No')
            complete_record['問題文'] = notion_row.get('問題文', '')
            complete_record['症例文'] = notion_row.get('症例文', '')
            complete_record['選択肢'] = notion_row.get('選択肢', '')
            complete_record['Web表示用'] = notion_row.get('Web表示用', '')
            complete_record['タグ'] = notion_row.get('タグ', '')
            complete_record['最終更新'] = notion_row.get('最終更新', '')
            complete_record['データ状態'] = 'notion_existing'
        elif qid in restore_data:
            restore_row = restore_data[qid]
            complete_record['正答'] = restore_row.get('正答', '')
            complete_record['正答率'] = restore_row.get('正答率', '')
            complete_record['英語問題'] = restore_row.get('英語問題', 'No')
            complete_record['画像問題'] = restore_row.get('画像問題', 'No')
            complete_record['連問'] = restore_row.get('連問', 'No')
            complete_record['計算問題'] = restore_row.get('計算問題', 'No')
            complete_record['問題文'] = restore_row.get('問題文', '')
            complete_record['症例文'] = restore_row.get('症例文', '')
            complete_record['選択肢'] = restore_row.get('選択肢', '')
            complete_record['Web表示用'] = restore_row.get('Web表示用', complete_record['コンテンツ'])
            complete_record['タグ'] = restore_row.get('タグ', '')
            complete_record['最終更新'] = restore_row.get('最終更新', '')
            complete_record['データ状態'] = 'restored'
        else:
            # 基本フィールドをデフォルト値で埋める
            complete_record['正答'] = ''
            complete_record['正答率'] = ''
            complete_record['英語問題'] = 'No'
            complete_record['画像問題'] = 'No'
            complete_record['連問'] = 'No'
            complete_record['計算問題'] = 'No'
            complete_record['問題文'] = ''
            complete_record['症例文'] = ''
            complete_record['選択肢'] = ''
            complete_record['Web表示用'] = complete_record['コンテンツ']
            complete_record['タグ'] = ''
            complete_record['最終更新'] = ''
            complete_record['データ状態'] = 'basic_only'
        
        complete_database[qid] = complete_record
    
    print(f"  完全データベース構築完了: {len(complete_database)}問")
    
    # 3. 品質検証
    print("\n✅ ステップ3: 品質検証")
    print("-" * 40)
    
    # データ状態別カウント
    state_counts = defaultdict(int)
    for record in complete_database.values():
        state_counts[record['データ状態']] += 1
    
    print("  データ状態別内訳:")
    for state, count in state_counts.items():
        print(f"    {state}: {count}問")
    
    # 年度別検証
    by_year = defaultdict(list)
    for qid, record in complete_database.items():
        by_year[record['年度']].append(qid)
    
    print("\n  年度別検証:")
    for year in sorted(by_year.keys()):
        print(f"    第{year}回: {len(by_year[year])}問")
        
        if len(by_year[year]) != 400:
            print(f"      ⚠️  予想と異なる問題数")
    
    # セクション別検証
    by_section = defaultdict(list)
    for qid, record in complete_database.items():
        by_section[record['セクション']].append(qid)
    
    print("\n  セクション別検証:")
    for section in sorted(by_section.keys()):
        print(f"    セクション{section}: {len(by_section[section])}問")
    
    # 4. 出力ファイル作成
    print("\n💾 ステップ4: 最終出力ファイル作成")
    print("-" * 40)
    
    # CSV形式（完全版）
    final_csv = final_dir / "complete_medical_exam_database_2000.csv"
    
    fieldnames = ['問題ID', '年度', 'セクション', '問題番号', '正答', '正答率',
                  '英語問題', '画像問題', '連問', '計算問題', '問題文', '症例文',
                  '選択肢', 'Web表示用', 'タグ', '最終更新', 'ソース', 'コンテンツ', 'データ状態']
    
    with open(final_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for qid in sorted(complete_database.keys()):
            writer.writerow(complete_database[qid])
    
    print(f"  完全版CSV: {final_csv}")
    
    # JSON形式（構造化）
    final_json = final_dir / "complete_medical_exam_database_2000.json"
    
    json_data = {
        'metadata': {
            'total_questions': len(complete_database),
            'creation_date': datetime.now().isoformat(),
            'version': '1.0',
            'description': '日本医師国家試験問題完全データベース（第115-119回）'
        },
        'statistics': {
            'by_year': {year: len(questions) for year, questions in by_year.items()},
            'by_section': {section: len(questions) for section, questions in by_section.items()},
            'by_data_state': dict(state_counts)
        },
        'questions': complete_database
    }
    
    with open(final_json, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"  JSON形式: {final_json}")
    
    # 統計レポート
    stats_file = final_dir / "database_statistics.md"
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("# 完全データベース統計レポート\n\n")
        f.write(f"## 基本情報\n")
        f.write(f"- 総問題数: {len(complete_database)}問\n")
        f.write(f"- 対象年度: 第115-119回医師国家試験\n")
        f.write(f"- 作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 年度別内訳\n")
        for year in sorted(by_year.keys()):
            f.write(f"- 第{year}回: {len(by_year[year])}問\n")
        
        f.write("\n## セクション別内訳\n")
        for section in sorted(by_section.keys()):
            f.write(f"- セクション{section}: {len(by_section[section])}問\n")
        
        f.write("\n## データ状態別内訳\n")
        for state, count in state_counts.items():
            f.write(f"- {state}: {count}問\n")
        
        f.write("\n## 復元成功率\n")
        total = len(complete_database)
        complete_data = state_counts['notion_existing'] + state_counts['restored']
        f.write(f"完全データ: {complete_data}/{total}問 ({complete_data/total*100:.1f}%)\n")
    
    print(f"  統計レポート: {stats_file}")
    
    # 5. 検証レポート
    print("\n📊 ステップ5: 最終検証")
    print("-" * 40)
    
    total_questions = len(complete_database)
    complete_data_count = state_counts['notion_existing'] + state_counts['restored']
    
    print(f"  ✅ 総問題数: {total_questions}問")
    print(f"  📊 完全データ: {complete_data_count}問 ({complete_data_count/total_questions*100:.1f}%)")
    print(f"  🔄 復元データ: {state_counts['restored']}問")
    print(f"  💾 既存データ: {state_counts['notion_existing']}問")
    
    if total_questions == 2000:
        print("  🎯 目標達成: 2000問の完全データベース構築成功！")
    
    # 6. 最終サマリー
    print("\n🎉 ステップ6: プロジェクト完了")
    print("-" * 40)
    
    print("  📁 出力ファイル:")
    print(f"     - {final_csv.name} (CSV完全版)")
    print(f"     - {final_json.name} (JSON構造化版)")
    print(f"     - {stats_file.name} (統計レポート)")
    
    print("\n  🚀 JMLE説明文生成システム準備完了")
    print("     - 2000問の医師国家試験データベース")
    print("     - 完全な問題構造とメタデータ")
    print("     - 説明文生成用データセット基盤")
    
    return {
        'total_questions': total_questions,
        'complete_data_count': complete_data_count,
        'success_rate': complete_data_count / total_questions,
        'output_files': [final_csv, final_json, stats_file]
    }

if __name__ == "__main__":
    build_complete_database()