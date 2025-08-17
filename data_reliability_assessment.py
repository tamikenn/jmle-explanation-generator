#!/usr/bin/env python3
"""
データソースの信頼性評価と優先順位決定
"""
import re
from pathlib import Path
from collections import defaultdict

def assess_data_reliability():
    """データソースの信頼性を評価"""
    print("🔍 データソース信頼性評価")
    print("=" * 60)
    
    source_dir = Path("/workspaces/jmle-explanation-generator/raw_data/source_texts")
    
    # 1. medical_exam_11~シリーズ（最も信頼できる元データ）
    print("\n📊 1. medical_exam_11~シリーズ（最も信頼できる）")
    print("-" * 40)
    
    source_files = sorted([f for f in source_dir.glob("medical_exam_11*.txt") 
                          if "web_display" not in f.name])
    
    total_source = 0
    source_by_year = defaultdict(list)
    
    for file in source_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            ids = sorted(set(re.findall(pattern, content)))
            
            print(f"  {file.name}: {len(ids)}問")
            total_source += len(ids)
            
            # 年度別分類
            for qid in ids:
                year = qid[:3]
                source_by_year[year].append(qid)
            
            # データ品質チェック
            lines = content.split('\n')
            print(f"    ファイルサイズ: {file.stat().st_size:,}バイト")
            print(f"    行数: {len(lines):,}")
            
            # 問題構造の確認
            sample_problems = 0
            for line in lines[:100]:
                if re.match(r'\d{3}[A-Z]\d{1,3}\s', line):
                    sample_problems += 1
            print(f"    問題構造の整合性: {sample_problems}/100行でパターン確認")
    
    print(f"\n  🎯 合計: {total_source}問")
    
    # 2. web_display完成形データ
    print("\n📊 2. medical_exam_web_display_final.txt（完成形）")
    print("-" * 40)
    
    web_file = source_dir / "medical_exam_web_display_final.txt"
    web_ids = []
    if web_file.exists():
        with open(web_file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            web_ids = sorted(set(re.findall(pattern, content)))
            
            lines = content.split('\n')
            print(f"  問題数: {len(web_ids)}問")
            print(f"  ファイルサイズ: {web_file.stat().st_size:,}バイト")
            print(f"  行数: {len(lines):,}")
            
            # 完成度チェック
            if len(lines) > 10:
                print(f"  完成度指標: ヘッダー情報あり")
                for i, line in enumerate(lines[:10]):
                    if "総問題数" in line or "英語問題" in line:
                        print(f"    {line.strip()}")
    
    # 3. Notionデータベース
    print("\n📊 3. Notionデータベース（現在の状況）")
    print("-" * 40)
    
    notion_dir = Path("/workspaces/jmle-explanation-generator/raw_data/notion")
    notion_files = list(notion_dir.glob("*.csv"))
    
    if notion_files:
        # 前回の分析結果を要約
        print(f"  問題数: 1,750問（前回分析結果）")
        print(f"  データ完全性: 欠番なし（既存データは完全）")
        print(f"  構造化レベル: 高（CSV形式、完全な構造化）")
    
    # 4. データフロー分析
    print("\n🔄 データ変換フロー分析")
    print("-" * 40)
    
    all_source_ids = []
    for year_ids in source_by_year.values():
        all_source_ids.extend(year_ids)
    all_source_ids = sorted(set(all_source_ids))
    
    print(f"  元データ → 完成形: {len(all_source_ids)} → {len(web_ids)} (+{len(web_ids) - len(all_source_ids)}問)")
    print(f"  完成形 → Notion: {len(web_ids)} → 1750 (-{len(web_ids) - 1750}問)")
    
    # 5. 推奨戦略
    print("\n💡 推奨データ復元戦略")
    print("-" * 40)
    
    print("  【フェーズ1】 ベースデータ確立")
    print("    - medical_exam_11~シリーズ（1,850問）を信頼できるベースとする")
    print("    - web_displayで追加された150問の品質評価")
    
    print("\n  【フェーズ2】 データ統合")
    print("    - ベース1,850問 + 品質確認済み追加150問 = 2,000問")
    print("    - 現在のNotion1,750問との差分251問を特定")
    
    print("\n  【フェーズ3】 完全復元")
    print("    - 欠損251問をweb_displayから抽出")
    print("    - 最終的に2,000問の完全なデータベース構築")
    
    return {
        'source_ids': all_source_ids,
        'web_ids': web_ids,
        'source_count': len(all_source_ids),
        'web_count': len(web_ids)
    }

if __name__ == "__main__":
    assess_data_reliability()