import requests
import json
import networkx as nx
import time

# ヘッダー（名刺）を追加：これがないと拒否されることがあります
headers = {
    'User-Agent': 'PoliticalPowerMap/1.0 (mailto:your_email@example.com)'
}

url = 'https://query.wikidata.org/sparql'
query = """
SELECT ?human ?humanLabel ?partyLabel ?committeeLabel ?winCount WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  FILTER NOT EXISTS { ?statement pq:P582 ?endTime } . 
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
"""

print("データを収集しています...")
try:
    # ヘッダー付きでリクエスト
    r = requests.get(url, params={'format': 'json', 'query': query}, headers=headers)
    r.raise_for_status() # エラーならここでストップ
    data = r.json()
except Exception as e:
    print(f"エラーが発生しました: {e}")
    exit(1) # 強制終了

# 2. データの整理
nodes = {}
committees = {}

print(f"取得件数: {len(data['results']['bindings'])}")

for item in data['results']['bindings']:
    name = item['humanLabel']['value']
    party = item.get('partyLabel', {}).get('value', '無所属')
    committee = item.get('committeeLabel', {}).get('value', None)
    
    if name not in nodes:
        nodes[name] = {
            "id": name,
            "name": name,
            "category": party,
            "symbolSize": 10,
            "roles": []
        }
    
    if committee:
        if committee not in committees:
            committees[committee] = []
        committees[committee].append(name)

# 3. 関係性の構築
G = nx.Graph()
for name in nodes:
    G.add_node(name)

links = []
print("関係性を分析しています...")
for com_name, members in committees.items():
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            if G.has_edge(members[i], members[j]):
                G[members[i]][members[j]]['weight'] += 1
            else:
                G.add_edge(members[i], members[j], weight=1)

# パワーバランス計算
centrality = nx.pagerank(G)
for name, score in centrality.items():
    nodes[name]['symbolSize'] = 10 + (score * 5000)

for u, v, d in G.edges(data=True):
    if d['weight'] >= 1: 
        links.append({"source": u, "target": v, "value": d['weight']})

# 4. 書き出し
output = {
    "nodes": list(nodes.values()),
    "links": links,
    "categories": [{"name": p} for p in set(n['category'] for n in nodes.values())]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)

print("完了: data.jsonを作成しました")
