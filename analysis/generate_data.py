"""Generate js/network_data.js — precomputed spring layout + degree data."""

import networkx as nx
import pandas as pd
import json, os

DATA = "/Users/aliafif/Desktop/data"
OUT  = "/Users/aliafif/marvel-network/js/network_data.js"

nodes_df = pd.read_csv(f"{DATA}/week1_nodes.tsv", sep="\t", comment="#")
edges_df = pd.read_csv(f"{DATA}/week1_edges.tsv", sep="\t", comment="#",
                       header=None, names=["source", "target"])

G = nx.DiGraph()
G.add_nodes_from(nodes_df["node_id"])
G.add_edges_from(zip(edges_df["source"], edges_df["target"]))

name_map = dict(zip(nodes_df["node_id"], nodes_df["name"]))

pos = nx.spring_layout(G.to_undirected(), seed=42, k=0.55, iterations=250)

nodes_out = []
for node in G.nodes():
    x, y = pos.get(node, (0.0, 0.0))
    nodes_out.append({
        "id":   node,
        "name": name_map.get(node, node),
        "in":   G.in_degree(node),
        "out":  G.out_degree(node),
        "x":    round(float(x), 4),
        "y":    round(float(y), 4),
    })

links_out = [{"s": str(s), "t": str(t)} for s, t in G.edges()]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(f"const NODES={json.dumps(nodes_out)};\n")
    f.write(f"const LINKS={json.dumps(links_out)};\n")

print(f"Done: {len(nodes_out)} nodes, {len(links_out)} edges → {OUT}")
