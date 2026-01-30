import requests
import json
import networkx as nx
import time
import sys

# 1. データ収集設定
# ユーザーエージェント（名刺）を少し詳細にして拒否されにくくする
headers = {
    'User-Agent': 'PoliticalPowerMapBot/1.0 (https://github.com/your_account/diet-power-map)'
}

url = 'https://query.wikidata.org/sparql'

# クエリ：現職の衆議院議員を取得
# もし「取得件数0」が続く場合、一時的に FILTER NOT EXISTS を外すと全期間取れますが、まずは標準設定で
query = """
SELECT DISTINCT ?human ?humanLabel ?partyLabel ?committeeLabel ?winCount WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  FILTER NOT EXISTS { ?statement pq:P582 ?endTime } . 
  
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
"""

print("データを収集しています...")
data = None

# リトライ処理（最大3回試す）
for i in range(3):
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        break # 成功したらループを抜ける
    except Exception as e:
        print(f"試行 {i+1}回目 失敗: {e}")
        time.sleep(2) # 2秒待って再トライ

if not data or 'results' not in data or len(data['results']['bindings']) == 0:
    print("エラー: データを取得できませんでした（件数0）。")
    sys.exit(0) # エラーにはせず、今回は何もしないで終了（サイトを壊さないため）

# 2. データの整理
nodes = {}
committees = {}

raw_results = data['results']['bindings']
print(f"取得件数: {len(raw_results)}件")

for item in raw_results:
    name = item['humanLabel']['value']
    party = item.get('partyLabel', {}).get('value', '無所属')
    committee = item.get('committeeLabel', {}).get('value', None)
    
    # 除外ワード（QIDなどが名前になってしまうのを防ぐ）
    if name.startswith("Q"): continue 

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

# ノードが少なすぎる場合はグラフを作らない
if len(nodes) < 5:
    print("データが少なすぎるため更新を中止します")
    sys.exit(0)

# 3. 関係性の構築
G = nx.Graph()
for name in nodes:
    G.add_node(name)

links = []
print("関係性を分析しています...")
for com_name, members in committees.items():
    members = [m for m in members if m in nodes] # 念のため存在確認
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            if G.has_edge(members[i], members[j]):
                G[members[i]][members[j]]['weight'] += 1
            else:
                G.add_edge(members[i], members[j], weight=1)

# パワーバランス計算
# 孤立したノード（誰ともつながっていない人）が多いとエラーになる場合があるのでtryで囲む
try:
    centrality = nx.pagerank(G, max_iter=100)
    for name, score in centrality.items():
        nodes[name]['symbolSize'] = 10 + (score * 5000)
except Exception as e:
    print(f"PageRank計算エラー（簡易モードに切り替えます）: {e}")
    # 計算できない場合はサイズを一律にする
    for name in nodes:
        nodes[name]['symbolSize'] = 15

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
