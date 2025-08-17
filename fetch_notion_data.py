#!/usr/bin/env python3
"""
Notion データベースからデータを取得するスクリプト
使用方法:
1. Notion Integration を作成してトークンを取得
2. データベースをIntegrationと共有
3. 環境変数を設定して実行
"""

import os
import json
import csv
from datetime import datetime

def export_notion_instructions():
    """Notionからデータをエクスポートする手順"""
    
    print("""
╔════════════════════════════════════════════════╗
║     Notionデータベース エクスポート手順        ║
╚════════════════════════════════════════════════╝

📥 手動エクスポート方法:

1. Notionでデータベースを開く
   https://www.notion.so/252c2ad5eaab8086aaace4f93d2312e6

2. 右上の「...」メニューから「Export」を選択

3. エクスポート設定:
   - Export format: 「Markdown & CSV」を選択
   - Include content: 「Everything」を選択
   - Include subpages: チェックを入れる
   - Create folders for subpages: チェックを入れる

4. 「Export」をクリックしてダウンロード

5. ダウンロードしたZIPファイルをこのディレクトリに配置

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔌 API経由でアクセスする場合:

1. Notion Integrationを作成:
   https://www.notion.so/my-integrations
   
2. 「New integration」をクリック
   - Name: "JMLE Data Recovery"
   - Associated workspace: あなたのワークスペース
   - Capabilities: Read contentにチェック

3. 「Submit」→ トークンをコピー

4. データベースをIntegrationと共有:
   - データベースページの右上「Share」
   - 「Invite」に作成したIntegrationを追加

5. 環境変数を設定:
   export NOTION_TOKEN="secret_xxxxx..."
   export NOTION_DATABASE_ID="252c2ad5eaab8086aaace4f93d2312e6"

6. このスクリプトを実行:
   python fetch_notion_data.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def parse_exported_csv(csv_file):
    """エクスポートされたCSVファイルを解析"""
    
    problems = []
    missing_numbers = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                problems.append(row)
                
        # 問題番号を抽出して欠番を特定
        problem_numbers = []
        for p in problems:
            # 番号フィールドを探す（Name, Title, 問題番号 など）
            for key in p.keys():
                if '番号' in key or 'number' in key.lower() or 'id' in key.lower():
                    try:
                        num = int(''.join(filter(str.isdigit, str(p[key]))))
                        problem_numbers.append(num)
                    except:
                        pass
        
        if problem_numbers:
            problem_numbers.sort()
            # 欠番を検出
            for i in range(min(problem_numbers), max(problem_numbers) + 1):
                if i not in problem_numbers:
                    missing_numbers.append(i)
        
        print(f"\n✅ 読み込み完了:")
        print(f"   - 総問題数: {len(problems)}")
        print(f"   - 問題番号範囲: {min(problem_numbers) if problem_numbers else 'N/A'} - {max(problem_numbers) if problem_numbers else 'N/A'}")
        print(f"   - 欠番: {len(missing_numbers)}個")
        
        if missing_numbers:
            print(f"\n⚠️  欠番リスト:")
            for i in range(0, len(missing_numbers), 10):
                print(f"   {missing_numbers[i:i+10]}")
        
        # 結果をJSONで保存
        with open('notion_data_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total_problems': len(problems),
                'problem_numbers': problem_numbers,
                'missing_numbers': missing_numbers,
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 分析結果を保存: notion_data_analysis.json")
        
        return problems, missing_numbers
        
    except FileNotFoundError:
        print(f"\n❌ ファイルが見つかりません: {csv_file}")
        print("   Notionからエクスポートしたファイルを配置してください。")
        return None, None

def create_recovery_plan(missing_numbers):
    """復旧計画を作成"""
    
    if not missing_numbers:
        print("\n✨ 欠番がありません！データは完全です。")
        return
    
    print(f"""
╔════════════════════════════════════════════════╗
║            データ復旧計画                      ║
╚════════════════════════════════════════════════╝

📊 現状:
   - 欠番数: {len(missing_numbers)}個
   - 復旧必要な問題番号: {missing_numbers[:5]}{'...' if len(missing_numbers) > 5 else ''}

📝 復旧手順:
   1. 既存データのパターンを分析
   2. 欠番部分のテンプレートを生成
   3. 自動生成スクリプトで補完
   4. 手動レビューと修正
   5. 完全なデータセットを構築

🚀 次のステップ:
   python generate_missing_problems.py
    """)
    
    # 復旧スクリプトのテンプレートを生成
    with open('generate_missing_problems.py', 'w', encoding='utf-8') as f:
        f.write(f'''#!/usr/bin/env python3
"""欠番問題を生成するスクリプト"""

missing_numbers = {missing_numbers}

def generate_problem(number):
    """問題を生成"""
    # ここに生成ロジックを実装
    return {{
        "number": number,
        "title": f"問題 {{number}}",
        "content": "生成された内容",
        "answer": "解答",
        "explanation": "解説"
    }}

# 欠番を生成
for num in missing_numbers:
    problem = generate_problem(num)
    print(f"生成: 問題 {{num}}")
    # ここで保存処理を実装

print(f"\\n✅ {{len(missing_numbers)}}個の問題を生成しました")
''')
    
    print("   ✅ 復旧スクリプトを作成: generate_missing_problems.py")

if __name__ == "__main__":
    export_notion_instructions()
    
    # CSVファイルが存在する場合は解析
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        print(f"\n📁 CSVファイルを発見: {csv_files}")
        for csv_file in csv_files:
            problems, missing = parse_exported_csv(csv_file)
            if missing is not None:
                create_recovery_plan(missing)
    else:
        print("\n⏳ CSVファイルをアップロードしてください...")