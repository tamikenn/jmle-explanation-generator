#!/usr/bin/env python3
"""
アップロードされた医師国家試験データの分析
"""
import os
import re
from pathlib import Path

def analyze_medical_exam_files():
    """medical_examファイルを分析"""
    
    source_dir = Path("/workspaces/jmle-explanation-generator/raw_data/source_texts")
    
    print("=" * 60)
    print("📊 医師国家試験データ分析")
    print("=" * 60)
    
    # medical_exam_11x.txt ファイルの分析
    exam_files = sorted(source_dir.glob("medical_exam_*.txt"))
    
    total_questions = 0
    all_question_ids = []
    
    for exam_file in exam_files:
        if "web_display" in exam_file.name:
            continue  # web_displayファイルは後で分析
            
        print(f"\n📁 {exam_file.name}")
        print("-" * 40)
        
        with open(exam_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            # 問題IDのパターンを探す（例: 115A1, 116B23など）
            question_ids = []
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            
            for line in lines[:100]:  # 最初の100行を確認
                matches = re.findall(pattern, line)
                if matches:
                    question_ids.extend(matches)
            
            # 全体から問題IDを抽出
            all_matches = re.findall(pattern, content)
            unique_ids = sorted(set(all_matches))
            
            print(f"  ファイルサイズ: {exam_file.stat().st_size:,} bytes")
            print(f"  行数: {len(lines):,}")
            print(f"  検出された問題ID数: {len(unique_ids)}")
            
            if unique_ids[:5]:
                print(f"  最初の問題ID: {unique_ids[:5]}")
            if unique_ids[-5:]:
                print(f"  最後の問題ID: {unique_ids[-5:]}")
            
            total_questions += len(unique_ids)
            all_question_ids.extend(unique_ids)
            
            # 内容のサンプル表示
            print(f"\n  📝 ファイルの最初の3行:")
            for i, line in enumerate(lines[:3]):
                if len(line) > 80:
                    print(f"    {i+1}: {line[:80]}...")
                else:
                    print(f"    {i+1}: {line}")
    
    # web_display_finalファイルの分析
    web_file = source_dir / "medical_exam_web_display_final.txt"
    if web_file.exists():
        print(f"\n\n🌐 完成形ファイル: {web_file.name}")
        print("=" * 60)
        
        with open(web_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
            # 問題IDを抽出
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            web_ids = sorted(set(re.findall(pattern, content)))
            
            print(f"  ファイルサイズ: {web_file.stat().st_size:,} bytes")
            print(f"  行数: {len(lines):,}")
            print(f"  検出された問題ID数: {len(web_ids)}")
            
            if web_ids[:10]:
                print(f"  最初の問題ID: {web_ids[:10]}")
            if web_ids[-10:]:
                print(f"  最後の問題ID: {web_ids[-10:]}")
            
            # 内容のサンプル表示
            print(f"\n  📝 ファイルの最初の5行:")
            for i, line in enumerate(lines[:5]):
                if len(line) > 100:
                    print(f"    {i+1}: {line[:100]}...")
                else:
                    print(f"    {i+1}: {line}")
    
    # 統計情報
    print("\n\n📊 総合統計")
    print("=" * 60)
    print(f"  元データ (medical_exam_11x): {total_questions}問")
    print(f"  完成形データ (web_display): {len(web_ids)}問")
    print(f"  Notionデータベース: 1750問")
    
    # 欠番の可能性を分析
    all_unique = sorted(set(all_question_ids))
    print(f"\n  全ユニーク問題ID: {len(all_unique)}問")
    
    # 年度別の分析
    years = {}
    for qid in all_unique:
        year = qid[:3]
        if year not in years:
            years[year] = []
        years[year].append(qid)
    
    print("\n  年度別問題数:")
    for year in sorted(years.keys()):
        print(f"    第{year}回: {len(years[year])}問")
    
    return all_unique, web_ids

if __name__ == "__main__":
    analyze_medical_exam_files()