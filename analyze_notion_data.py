#!/usr/bin/env python3
"""
Notionデータベースの分析スクリプト
"""
import os
import csv
import json
from pathlib import Path

def analyze_csv_files():
    """CSVファイルを分析"""
    
    # raw_data/notionディレクトリのCSVファイルを探す
    notion_dir = Path("/workspaces/jmle-explanation-generator/raw_data/notion")
    csv_files = list(notion_dir.glob("*.csv"))
    
    print(f"発見したCSVファイル: {len(csv_files)}個")
    
    for csv_file in csv_files:
        print(f"\n=== ファイル: {csv_file.name} ===")
        print(f"ファイルサイズ: {csv_file.stat().st_size:,} bytes")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # 最初の数行を読む
                lines = []
                for i, line in enumerate(f):
                    if i < 5:
                        lines.append(line.strip())
                    else:
                        break
                
                print("\n最初の5行:")
                for i, line in enumerate(lines):
                    print(f"  {i+1}: {line[:100]}{'...' if len(line) > 100 else ''}")
                
                # CSVとして解析
                f.seek(0)
                reader = csv.DictReader(f)
                
                # カラム名を取得
                fieldnames = reader.fieldnames
                print(f"\nカラム: {fieldnames}")
                
                # データを読み込み
                rows = list(reader)
                print(f"データ行数: {len(rows)}")
                
                # 問題番号を抽出
                problem_numbers = []
                for row in rows:
                    # 番号が含まれるカラムを探す
                    for key in row.keys():
                        if '問題' in str(key) or '番号' in str(key) or 'number' in str(key).lower():
                            try:
                                # 数字を抽出
                                import re
                                match = re.search(r'\d+', str(row[key]))
                                if match:
                                    problem_numbers.append(int(match.group()))
                                    break
                            except:
                                pass
                
                if problem_numbers:
                    problem_numbers = sorted(set(problem_numbers))
                    print(f"\n問題番号範囲: {min(problem_numbers)} - {max(problem_numbers)}")
                    
                    # 欠番を検出
                    missing = []
                    for i in range(min(problem_numbers), max(problem_numbers) + 1):
                        if i not in problem_numbers:
                            missing.append(i)
                    
                    print(f"欠番数: {len(missing)}個")
                    if missing[:20]:
                        print(f"欠番例: {missing[:20]}")
                
                # 最初の数行のデータを表示
                print("\n最初の3行のデータ:")
                for i, row in enumerate(rows[:3]):
                    print(f"\n行 {i+1}:")
                    for key, value in list(row.items())[:5]:
                        print(f"  {key}: {value[:50] if value else '(空)'}{'...' if value and len(value) > 50 else ''}")
                
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    analyze_csv_files()