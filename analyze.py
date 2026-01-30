from SPARQLWrapper import SPARQLWrapper, JSON
import json
import networkx as nx
import sys
import time

# ウィキデータの公式エンドポイント
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# 【重要】連絡先入りUser-Agent（ウィキデータの推奨ルールに従う）
# これで「怪しいロボット」ではなく「身元のしっかりしたツール」として扱われます
sparql.addCustomHttpHeader("User-Agent", "DietPowerMap/1.0 (https://github.com/YOUR-ACCOUNT/diet-power-map)")
sparql.setReturnFormat(JSON)

# クエリ：日本の衆議院議員(Q17505613)
# タイムアウトを防ぐため、少し期間を限定するなどの工夫も可能ですが、まずは標準でいきます
query = """
SELECT DISTINCT ?human ?humanLabel ?partyLabel ?committeeLabel WHERE {
  ?human p:P39 ?statement .
  ?statement ps:P39 wd:Q17505613 . 
  FILTER NOT EXISTS { ?statement pq:P582 ?endTime } . # 現職のみ
  
  OPTIONAL { ?human wdt:P102 ?party . }
  OPTIONAL { ?human wdt:P39 ?role . ?role wdt:P279 wd:Q17554522 . } # 委員会
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
}
LIMIT 1000
"""

sparql.setQuery(query)

print("データを収集しています(SPARQLWrapper使用)...")
data = None

# リトライ処理
for i in range(5):
    try:
        results = sparql.query().convert()
        data = results
        print(f"データ取得成功！")
        break
    except Exception as e:
        print(f"試行 {i+1}回目 失敗: {e}")
        time.sleep(5) # 5秒待って再トライ

# 失敗時の処理
if not data or 'results' not in data:
    print("エラー: データの取得に完全に失敗しました。")
    # サイトに「取得失敗」と出すためのダミー
    nodes = [{"id": "Error", "name": "データ取得エラー\n(時間をおいて再実行してください)", "category": "エラー", "symbolSize": 50}]
    links = []
    categories = [{"name": "エラー"}]
else:
    # 成功時の処理
    raw_results = data['results']['bindings']
    print(f"取得件数: {len(raw_results)}件")
    
    nodes_dict = {}
    committees = {}

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
        # 委員会メンバー同士をつなぐ
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                if G.has_edge(members[i], members[j]):
                    G[members[i]][members[j]]['weight'] += 1
                else:
                    G.add_edge(members[i], members[j], weight=1)

    # PageRank計算（失敗しても止まらないようにする）
    try:
        centrality = nx.pagerank(G, max_iter=100)
        for name, score in centrality.items():
            nodes_dict[name]['symbolSize'] = 5 + (score * 5000)
            if score > 0.003: 
                nodes_dict[name]['label'] = {"show": True}
    except:
        pass

    nodes = list(nodes_dict.values())
    links = [{"source": u, "target": v, "value": d['weight']} for u, v, d in G.edges(data=True) if d['weight'] >= 1]
    categories = [{"name": p} for p in set(n['category'] for n in nodes)]

# ファイル保存
output = {"nodes": nodes, "links": links, "categories": categories}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)
    
print("完了")
