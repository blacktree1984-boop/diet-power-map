import requests
import json
import networkx as nx

# 1. データ収集（SPARQLでウィキデータから取得）
# 取得内容：現職衆議院議員、政党、所属委員会、当選回数
url = 'https://query.wikidata.org/sparql'
query = """
SELECT ?human ?humanLabel ?partyLabel ?committeeLabel ?winCount WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  FILTER NOT EXISTS { ?statement pq:P582 ?endTime } . 
  
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . } # 委員会の所属
  OPTIONAL { ?human wdt:P1556 ?winCount . } # 注：当選回数はデータがない場合もあるため本来は別ソース推奨

  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
"""

print("データを収集しています...")
r = requests.get(url, params={'format': 'json', 'query': query})
data = r.json()

# 2. データの整理
nodes = {}
committees = {}

for item in data['results']['bindings']:
    name = item['humanLabel']['value']
    party = item.get('partyLabel', {}).get('value', '無所属')
    committee = item.get('committeeLabel', {}).get('value', None)
    
    # ノード（議員）情報の登録
    if name not in nodes:
        nodes[name] = {
            "id": name,
            "name": name,
            "category": party,
            "symbolSize": 10, # 初期値
            "roles": []
        }
    
    # 委員会（関係性の元）の登録
    if committee:
        if committee not in committees:
            committees[committee] = []
        committees[committee].append(name)

# 3. 関係性の構築とパワー計算（ネットワーク分析）
G = nx.Graph()

# ノード追加
for name in nodes:
    G.add_node(name)

# エッジ追加（同じ委員会に所属している人同士をつなぐ）
links = []
print("関係性を分析しています...")
for com_name, members in committees.items():
    # 同じ委員会のメンバー総当たりで線をつなぐ
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            # エッジの重み（複数の委員会で一緒なら絆が強い）
            if G.has_edge(members[i], members[j]):
                G[members[i]][members[j]]['weight'] += 1
            else:
                G.add_edge(members[i], members[j], weight=1)

# パワーバランス計算（PageRankアルゴリズム：Google検索の順位付けと同じ理論）
# 「重要人物と繋がっている人は重要」というロジックでスコア化
centrality = nx.pagerank(G)

# 分析結果をノードに反映
for name, score in centrality.items():
    # スコアを5000倍して見やすいサイズにする
    nodes[name]['symbolSize'] = 10 + (score * 5000)
    nodes[name]['powerScore'] = round(score * 1000, 2)

# リンクデータの整形
for u, v, d in G.edges(data=True):
    # あまりに弱い繋がりは表示しない（軽量化）
    if d['weight'] >= 1: 
        links.append({"source": u, "target": v, "value": d['weight']})

# 4. ファイル書き出し
output = {
    "nodes": list(nodes.values()),
    "links": links,
    "categories": [{"name": p} for p in set(n['category'] for n in nodes.values())]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)

print("分析完了。data.jsonを作成しました。")
