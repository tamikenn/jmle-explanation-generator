#!/usr/bin/env python3
"""
web_displayで追加された150問の詳細分析
"""
import re
from pathlib import Path
from collections import defaultdict

def analyze_added_questions():
    """追加された150問の詳細分析"""
    print("🔍 追加された150問の詳細分析")
    print("=" * 60)
    
    source_dir = Path("/workspaces/jmle-explanation-generator/raw_data/source_texts")
    
    # 1. 元データから問題ID抽出
    source_files = sorted([f for f in source_dir.glob("medical_exam_11*.txt") 
                          if "web_display" not in f.name])
    
    all_source_ids = []
    source_by_year = defaultdict(list)
    
    print("📁 元データ（medical_exam_11~）から問題ID抽出:")
    for file in source_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            ids = sorted(set(re.findall(pattern, content)))
            
            all_source_ids.extend(ids)
            for qid in ids:
                year = qid[:3]
                source_by_year[year].append(qid)
            
            print(f"  {file.name}: {len(ids)}問")
    
    all_source_ids = sorted(set(all_source_ids))
    
    # 2. 完成形データから問題ID抽出
    web_file = source_dir / "medical_exam_web_display_final.txt"
    web_ids = []
    web_content = ""
    
    if web_file.exists():
        with open(web_file, 'r', encoding='utf-8') as f:
            web_content = f.read()
            pattern = r'\b(\d{3}[A-Z]\d{1,3})\b'
            web_ids = sorted(set(re.findall(pattern, web_content)))
    
    print(f"\n📁 完成形データ（web_display）: {len(web_ids)}問")
    
    # 3. 追加された問題を特定
    added_questions = sorted(set(web_ids) - set(all_source_ids))
    missing_questions = sorted(set(all_source_ids) - set(web_ids))
    
    print(f"\n🔍 差分分析:")
    print(f"  元データ: {len(all_source_ids)}問")
    print(f"  完成形: {len(web_ids)}問")
    print(f"  追加された問題: {len(added_questions)}問")
    print(f"  欠落した問題: {len(missing_questions)}問")
    
    # 4. 追加問題の年度別分析
    if added_questions:
        print(f"\n📊 追加問題の年度別分析:")
        added_by_year = defaultdict(list)
        for qid in added_questions:
            year = qid[:3]
            added_by_year[year].append(qid)
        
        for year in sorted(added_by_year.keys()):
            year_questions = sorted(added_by_year[year])
            print(f"  第{year}回: {len(year_questions)}問")
            print(f"    問題ID例: {year_questions[:10]}")
            
            # セクション別分析
            sections = defaultdict(list)
            for qid in year_questions:
                section = qid[3]
                sections[section].append(qid)
            
            for section in sorted(sections.keys()):
                section_questions = sorted(sections[section])
                print(f"    セクション{section}: {len(section_questions)}問 {section_questions[:5]}")
    
    # 5. 追加問題の内容分析
    if added_questions and web_content:
        print(f"\n📝 追加問題の内容サンプル分析:")
        
        sample_count = 0
        for qid in added_questions[:5]:  # 最初の5問をサンプル分析
            # 該当問題の内容を抽出
            pattern = fr'{re.escape(qid)}.*?(?=\d{{3}}[A-Z]\d{{1,3}}|$)'
            match = re.search(pattern, web_content, re.DOTALL)
            
            if match:
                content = match.group(0)
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                print(f"\n  【問題ID: {qid}】")
                for i, line in enumerate(lines[:10]):  # 最初の10行を表示
                    if len(line) > 100:
                        print(f"    {i+1}: {line[:100]}...")
                    else:
                        print(f"    {i+1}: {line}")
                
                sample_count += 1
                if sample_count >= 3:  # 最大3問まで
                    break
    
    # 6. 品質評価指標
    print(f"\n📈 追加問題の品質評価:")
    
    if added_questions:
        # 問題番号の連続性チェック
        for year in sorted(added_by_year.keys()):
            year_questions = sorted(added_by_year[year])
            numbers = []
            for qid in year_questions:
                match = re.search(r'(\d+)$', qid)
                if match:
                    numbers.append(int(match.group(1)))
            
            if numbers:
                numbers = sorted(numbers)
                print(f"  第{year}回:")
                print(f"    番号範囲: {min(numbers)} - {max(numbers)}")
                
                # 連続性チェック
                gaps = []
                for i in range(len(numbers)-1):
                    if numbers[i+1] - numbers[i] > 1:
                        gaps.append((numbers[i], numbers[i+1]))
                
                if gaps:
                    print(f"    番号の飛び: {gaps[:5]}")
                else:
                    print(f"    番号の連続性: 良好")
    
    # 7. 推奨アクション
    print(f"\n💡 追加150問に関する推奨アクション:")
    
    if len(added_questions) == 150:
        print("  ✅ 予想通り150問が追加されている")
        print("  🔍 各年度30問ずつの均等な追加パターン")
        print("  📝 内容の詳細確認が必要")
        
        if missing_questions:
            print(f"  ⚠️  同時に{len(missing_questions)}問が欠落している")
            print(f"     欠落例: {missing_questions[:5]}")
        else:
            print("  ✅ 元データから欠落した問題はなし")
        
        print("\n  【次のステップ】")
        print("  1. 追加問題の内容品質を詳細評価")
        print("  2. 医学的妥当性の確認")
        print("  3. 統合データセットへの組み込み判断")
    else:
        print(f"  ⚠️  予想と異なる追加数: {len(added_questions)}問")
    
    return {
        'source_ids': all_source_ids,
        'web_ids': web_ids, 
        'added_questions': added_questions,
        'missing_questions': missing_questions,
        'added_by_year': dict(added_by_year)
    }

if __name__ == "__main__":
    analyze_added_questions()