#!/usr/bin/env python3
"""
analyze.pyのテストスクリプト
ローカル環境で実行してWikipediaからのデータ取得を検証
"""

import sys
import os

def test_imports():
    """必要なライブラリがインストールされているか確認"""
    print("=" * 60)
    print("📦 ライブラリのインポートテスト")
    print("=" * 60)
    
    required_libs = [
        ('pandas', 'pandas'),
        ('networkx', 'networkx'),
        ('requests', 'requests (オプション)'),
    ]
    
    all_ok = True
    for module, name in required_libs:
        try:
            __import__(module)
            print(f"✓ {name} ... OK")
        except ImportError:
            print(f"✗ {name} ... NG (インストールが必要)")
            all_ok = False
    
    print()
    return all_ok

def test_wikipedia_access():
    """Wikipediaへのアクセステスト"""
    print("=" * 60)
    print("🌐 Wikipediaアクセステスト")
    print("=" * 60)
    
    import pandas as pd
    
    url = 'https://ja.wikipedia.org/wiki/%E8%A1%86%E8%AD%B0%E9%99%A2%E8%AD%B0%E5%93%A1%E4%B8%80%E8%A6%A7'
    
    try:
        print(f"URL: {url}")
        print("データ取得中...")
        
        dfs = pd.read_html(url, match='氏名', encoding='utf-8')
        print(f"✓ 取得成功: {len(dfs)}個のテーブルを検出")
        
        # 最大のテーブルを選択
        df = max(dfs, key=len)
        print(f"✓ 使用するテーブル: {len(df)}行 × {len(df.columns)}列")
        print(f"✓ カラム: {df.columns.tolist()}")
        
        # サンプルデータの表示
        print("\n📋 サンプルデータ（最初の3行）:")
        print(df.head(3).to_string())
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyze_script():
    """analyze.pyの実行テスト"""
    print("\n" + "=" * 60)
    print("🔧 analyze.py 実行テスト")
    print("=" * 60)
    
    try:
        # analyze.pyを実行
        import analyze
        
        if os.path.exists('data.json'):
            import json
            with open('data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ data.json 生成成功")
            print(f"  - ノード数: {len(data.get('nodes', []))}")
            print(f"  - リンク数: {len(data.get('links', []))}")
            print(f"  - カテゴリ数: {len(data.get('categories', []))}")
            
            if 'stats' in data:
                print(f"\n📊 統計情報:")
                for key, value in data['stats'].items():
                    if key != 'party_sizes':
                        print(f"  - {key}: {value}")
            
            return True
        else:
            print("✗ data.jsonが生成されませんでした")
            return False
            
    except Exception as e:
        print(f"✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("\n" + "=" * 60)
    print("🧪 国会パワーバランス可視化システム - テストスイート")
    print("=" * 60 + "\n")
    
    results = []
    
    # テスト1: ライブラリ
    results.append(("ライブラリ", test_imports()))
    
    # テスト2: Wikipedia アクセス
    if results[-1][1]:
        results.append(("Wikipedia", test_wikipedia_access()))
    else:
        print("\n⚠️  必要なライブラリがインストールされていないため、以降のテストをスキップします")
        results.append(("Wikipedia", False))
    
    # テスト3: スクリプト実行
    if results[-1][1]:
        results.append(("スクリプト実行", test_analyze_script()))
    else:
        print("\n⚠️  Wikipediaアクセスに失敗したため、スクリプト実行テストをスキップします")
        results.append(("スクリプト実行", False))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📋 テスト結果サマリー")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 すべてのテストが成功しました！")
        print("次のステップ:")
        print("1. index.htmlをブラウザで開いて表示を確認")
        print("2. GitHubにプッシュしてGitHub Actionsを実行")
    else:
        print("⚠️  一部のテストが失敗しました")
        print("エラーメッセージを確認して修正してください")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
