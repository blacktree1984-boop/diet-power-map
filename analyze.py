import requests
import json
import networkx as nx
import time
import sys

# 【重要】ブラウザのふりをする設定（ステルスモード）
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

url = 'https://query.wikidata.org/sparql'

# クエリ：日本の衆議院議員(Q17505613)を取得
query = """
SELECT DISTINCT ?human ?humanLabel ?partyLabel ?committeeLabel WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
LIMIT 500
"""

print("データを収集しています...")
data = None

# リトライ処理（最大5回、間隔を空けて試す）
for i in range(5):
    try:
        print(f"接続試行 {i+1}回目...")
        r = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=60)
        
        if r.status_code == 429:
            print("アクセス過多(429)のため待機します...")
            time.sleep(10)
            continue
            
        r.raise_for_status()
        data = r.json()
        print("データ取得成功！")
        break 
    except Exception as e:
        print(f"エラー: {e}")
        time.sleep(5)

# それでもダメだった場合の非常用ダミー（表示テスト用）
if not data or 'results' not in data or len(data['results']['bindings']) == 0:
    print("警告: どうしてもデータが取れません。サンプルデータを生成します。")
    nodes = [
        {"id": "取得エラー", "name": "取得エラー(再実行してください)", "category": "エラー", "symbolSize": 50},
        {"id": "サンプル太郎", "name": "サンプル太郎", "category": "与党", "symbolSize": 30},
        {"id": "サンプル花子", "name": "サンプル花子", "category": "野党", "symbolSize": 30}
    ]
    links = [{"source": "サンプル太郎", "target": "サンプル花子", "value": 1}]
    categories = [{"name": "エラー"}, {"name": "与党"}, {"name": "野党"}]
else:
    # 正常処理
    nodes_dict = {}
    committees = {}
    raw_results = data['results']['bindings']
    print(f"取得件数: {len(raw_results)}件")

    for item in raw_results:
        name = item['humanLabel']['value']
        if name.startswith("Q") or "http" in name: continue 
        
        party = item.get('partyLabel', {}).get('value', '無所属')
        committee = item.get('committeeLabel', {}).get('value', None)
        
        if name not in nodes_dict:
            nodes_dict[name] = {
                "id": name, "name": name, "category": party, 
                "symbolSize": 10, "label": {"show": False}
            }
        
        if committee:
            if committee not in committees: committees[committee] = []
            committees[committee].append(name)

    # グラフ構築
    G = nx.Graph()
    for name in nodes_dict: G.add_node(name)
    
    for com_name, members in committees.items():
        members = [m for m in members if m in nodes_dict]
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                if G.has_edge(members[i], members[j]):
                    G[members[i]][members[j]]['weight'] += 1
                else:
                    G.add_edge(members[i], members[j], weight=1)
    
    # PageRank（scipyがない場合も想定してnetworkx標準機能を使う）
    try:
        centrality = nx.pagerank(G, max_iter=100)
        for name, score in centrality.items():
            nodes_dict[name]['symbolSize'] = 5 + (score * 5000)
            if score > 0.003: # 上位層のみ名前表示
                nodes_dict[name]['label'] = {"show": True}
    except:
        pass

    nodes = list(nodes_dict.values())
    links = [{"source": u, "target": v, "value": d['weight']} for u, v, d in G.edges(data=True) if d['weight'] >= 1]
    categories = [{"name": p} for p in set(n['category'] for n in nodes)]

output = {"nodes": nodes, "links": links, "categories": categories}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)
