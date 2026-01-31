import pandas as pd
import json
import networkx as nx
import re
import sys
from typing import List, Dict, Tuple
import time

def extract_election_count(text: str) -> int:
    """当選回数を抽出する"""
    if pd.isna(text):
        return 1
    nums = re.findall(r'(\d+)', str(text))
    return int(nums[0]) if nums else 1

def normalize_party_name(party: str) -> str:
    """政党名を正規化"""
    if pd.isna(party) or party == '':
        return "無所属"
    # 改行や余分な空白を削除
    party = str(party).replace('\n', '').strip()
    # よくある略称を統一
    replacements = {
        '自民': '自由民主党',
        '立憲': '立憲民主党',
        '公明': '公明党',
        '共産': '日本共産党',
        '維新': '日本維新の会',
        '国民': '国民民主党',
    }
    for short, full in replacements.items():
        if short in party and full not in party:
            return full
    return party

def fetch_diet_members() -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Wikipediaから議員データを取得"""
    
    url = 'https://ja.wikipedia.org/wiki/%E8%A1%86%E8%AD%B0%E9%99%A2%E8%AD%B0%E5%93%A1%E4%B8%80%E8%A6%A7'
    
    print("Wikipediaから衆議院議員リストを取得中...")
    
    nodes = []
    links = []
    parties = {}
    
    try:
        # User-Agentを設定してアクセス
        dfs = pd.read_html(
            url, 
            match='氏名',
            encoding='utf-8'
        )
        
        print(f"取得したテーブル数: {len(dfs)}")
        
        # 最も行数が多いテーブルを選択（通常は議員一覧のメインテーブル）
        df = max(dfs, key=len)
        print(f"使用するテーブル: {len(df)}行 × {len(df.columns)}列")
        print(f"カラム名: {df.columns.tolist()}")
        
        # カラム名の柔軟な検出
        name_col = None
        party_col = None
        election_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if '氏名' in col_str or '名前' in col_str:
                name_col = col
            elif '会派' in col_str or '政党' in col_str or '党派' in col_str:
                party_col = col
            elif '当選' in col_str or '回数' in col_str:
                election_col = col
        
        if name_col is None:
            raise ValueError("氏名カラムが見つかりません")
        
        print(f"検出されたカラム - 氏名: {name_col}, 政党: {party_col}, 当選回数: {election_col}")
        
        processed_count = 0
        for index, row in df.iterrows():
            try:
                name = str(row[name_col]).strip()
                
                # 無効な名前をスキップ
                if not name or name == 'nan' or len(name) < 2:
                    continue
                
                # 政党の取得
                party = "無所属"
                if party_col:
                    party = normalize_party_name(row[party_col])
                
                # 当選回数の取得
                wins = 1
                if election_col:
                    wins = extract_election_count(row[election_col])
                
                # ノードを追加
                nodes.append({
                    "id": name,
                    "name": name,
                    "category": party,
                    "symbolSize": 15 + (wins * 5),  # 当選回数に応じてサイズ変更
                    "value": wins,
                    "label": {
                        "show": wins >= 5,  # 5回以上当選者は常に表示
                        "fontSize": 10 + wins
                    }
                })
                
                # 政党ごとにグループ化
                if party not in parties:
                    parties[party] = []
                parties[party].append(name)
                
                processed_count += 1
                
            except Exception as e:
                print(f"行 {index} の処理中にエラー: {e}")
                continue
        
        print(f"処理完了: {processed_count}名の議員データを取得")
        print(f"政党数: {len(parties)}")
        for party, members in sorted(parties.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {party}: {len(members)}名")
        
        # ネットワークの構築
        G = nx.Graph()
        
        # 同じ政党内でのつながりを作成
        for party, members in parties.items():
            if len(members) > 1:
                # 小規模政党はフルメッシュ、大規模政党はリング+ハブ構造
                if len(members) <= 5:
                    # フルメッシュ
                    for i, member1 in enumerate(members):
                        for member2 in members[i+1:]:
                            links.append({
                                "source": member1,
                                "target": member2,
                                "value": 2,
                                "lineStyle": {"width": 2}
                            })
                else:
                    # リング構造 + 最多当選者をハブに
                    # ハブとなる議員を選出（当選回数が多い順）
                    member_wins = []
                    for member in members:
                        node = next((n for n in nodes if n['id'] == member), None)
                        wins = node['value'] if node else 1
                        member_wins.append((member, wins))
                    
                    member_wins.sort(key=lambda x: x[1], reverse=True)
                    hub_count = min(3, len(members) // 10 + 1)  # 10人に1人をハブに
                    hubs = [m[0] for m in member_wins[:hub_count]]
                    
                    # リング構造
                    for i in range(len(members)):
                        target = members[(i + 1) % len(members)]
                        links.append({
                            "source": members[i],
                            "target": target,
                            "value": 1,
                            "lineStyle": {"width": 1}
                        })
                    
                    # ハブへの接続
                    for hub in hubs:
                        for member in members:
                            if member != hub and member not in hubs:
                                # 一定確率で接続（密度調整）
                                if hash(member + hub) % 5 == 0:
                                    links.append({
                                        "source": hub,
                                        "target": member,
                                        "value": 1,
                                        "lineStyle": {"width": 1, "opacity": 0.3}
                                    })
        
        # 連立与党間のつながり（例：自民党と公明党）
        coalition_pairs = [
            ('自由民主党', '公明党'),
        ]
        
        for party1, party2 in coalition_pairs:
            if party1 in parties and party2 in parties:
                # 各党のハブ同士を接続
                for member1 in parties[party1][:3]:  # 上位3名
                    for member2 in parties[party2][:3]:
                        links.append({
                            "source": member1,
                            "target": member2,
                            "value": 1,
                            "lineStyle": {"width": 2, "type": "dashed", "color": "#ff9800"}
                        })
        
        categories = [{"name": party} for party in sorted(parties.keys())]
        
        return nodes, links, categories
        
    except Exception as e:
        print(f"データ取得エラー: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """メイン処理"""
    try:
        nodes, links, categories = fetch_diet_members()
        
        if len(nodes) == 0:
            print("エラー: 議員データが取得できませんでした")
            sys.exit(1)
        
        # 統計情報の追加
        stats = {
            "total_members": len(nodes),
            "total_parties": len(categories),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "party_sizes": {}
        }
        
        for category in categories:
            party_name = category['name']
            party_members = [n for n in nodes if n['category'] == party_name]
            stats["party_sizes"][party_name] = len(party_members)
        
        # JSON出力
        output = {
            "nodes": nodes,
            "links": links,
            "categories": categories,
            "stats": stats
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ data.json を生成しました")
        print(f"  議員数: {stats['total_members']}名")
        print(f"  政党数: {stats['total_parties']}")
        print(f"  更新日時: {stats['last_updated']}")
        
    except Exception as e:
        print(f"致命的なエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
