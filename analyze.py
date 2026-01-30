import requests
import json
import networkx as nx
import time
import sys
import os

headers = {
    'User-Agent': 'PoliticalPowerMapBot/1.0 (https://github.com/)'
}

# クエリ修正：より単純にして、確実にデータを取る
# 「日本の衆議院議員(Q17505613)」の職にあったことがある人全員を取得（現職フィルタを外す）
url = 'https://query.wikidata.org/sparql'
query = """
SELECT DISTINCT ?human ?humanLabel ?partyLabel ?committeeLabel WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
LIMIT 300
"""

print("データを収集しています...")
data = None

for i in range(3):
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        break 
    except Exception as e:
        print(f"再試行中...: {e}")
        time.sleep(2)

# データが取れなかった場合の緊急回避用ダミーデータ
if not data or 'results' not in data or len(data['results']['bindings']) == 0:
    print("警告: データ取得に失敗しました。ダミーデータを生成します。")
    # これがあればエラーで止まらない
    nodes = [{"id": "データ取得失敗", "name": "データ取得失敗", "category": "エラー", "symbolSize": 30}]
    links = []
    categories = [{"name": "エラー"}]
else:
    # 正常にデータ処理
    nodes_dict = {}
    committees = {}
    raw_results = data['results']['bindings']
    print(f"取得成功: {len(raw_results)}件")

    for item in raw_results:
        name = item['humanLabel']['value']
        if name.startswith("Q"): continue # IDそのままの場合はスキップ
        
        party = item.get('partyLabel', {}).get('value', '無所属')
        committee = item.get('committeeLabel', {}).get('value', None)
        
        if name not in nodes_dict:
            nodes_dict[name] = {
                "id": name, "name": name, "category": party, 
                "symbolSize": 10, "label": {"show": False} # 初期状態はラベル非表示
            }
        
        if committee:
            if committee not in committees: committees[committee] = []
            committees[committee].append(name)

    # グラフ構築
    G = nx.Graph()
    for name in nodes_dict: G.add_node(name)
    
    # 関係性（委員会が同じ）
    for com_name, members in committees.items():
        members = [m for m in members if m in nodes_dict]
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                if G.has_edge(members[i], members[j]):
                    G[members[i]][members[j]]['weight'] += 1
                else:
                    G.add_edge(members[i], members[j], weight=1)
    
    # PageRank計算（scipy必須だがtryで囲む）
    try:
        centrality = nx.pagerank(G, max_iter=50)
        for name, score in centrality.items():
            nodes_dict[name]['symbolSize'] = 5 + (score * 3000)
            # スコアが高い人だけ名前を表示
            if score > 0.005:
                nodes_dict[name]['label'] = {"show": True}
    except:
        pass

    nodes = list(nodes_dict.values())
    links = [{"source": u, "target": v, "value": d['weight']} for u, v, d in G.edges(data=True) if d['weight'] >= 1]
    categories = [{"name": p} for p in set(n['category'] for n in nodes)]

# ファイル書き出し（必ず実行される）
output = {"nodes": nodes, "links": links, "categories": categories}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)
print("data.json を生成しました")
