"""Week 1 analysis: Marvel Wikipedia network — degree distributions, components."""

import networkx as nx
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from collections import Counter

DATA = "/Users/aliafif/Desktop/data"
FIGS = "/Users/aliafif/marvel-network/figures"

# ── Load ──────────────────────────────────────────────────────────────────────
nodes = pd.read_csv(f"{DATA}/week1_nodes.tsv", sep="\t", comment="#")
edges = pd.read_csv(f"{DATA}/week1_edges.tsv", sep="\t", comment="#",
                    header=None, names=["source", "target"])

G = nx.DiGraph()
G.add_nodes_from(nodes["node_id"])
G.add_edges_from(zip(edges["source"], edges["target"]))

name = dict(zip(nodes["node_id"], nodes["name"]))

print(f"Nodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")
print(f"Isolated nodes: {len(list(nx.isolates(G)))}")

# ── Degree sequences ──────────────────────────────────────────────────────────
in_deg  = sorted([d for _, d in G.in_degree()],  reverse=True)
out_deg = sorted([d for _, d in G.out_degree()], reverse=True)

# ── Figure 1: linear degree distributions ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
fig.patch.set_facecolor("#0d0d0d")

for ax in axes:
    ax.set_facecolor("#16213e")
    ax.tick_params(colors="#888", labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a3a")

in_counts  = Counter(in_deg)
out_counts = Counter(out_deg)

ax0, ax1 = axes
ax0.bar(in_counts.keys(),  in_counts.values(),  color="#e8212a", alpha=.85, width=1)
ax1.bar(out_counts.keys(), out_counts.values(), color="#4a90d9", alpha=.85, width=1)

ax0.set_title("In-degree distribution",  color="#e0e0e0", fontsize=11)
ax1.set_title("Out-degree distribution", color="#e0e0e0", fontsize=11)
for ax in axes:
    ax.set_xlabel("Degree", color="#888", fontsize=9)
    ax.set_ylabel("Count",  color="#888", fontsize=9)

plt.tight_layout(pad=2)
plt.savefig(f"{FIGS}/week1_degree_linear.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: week1_degree_linear.png")

# ── Figure 2: log–log degree distributions ───────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
fig.patch.set_facecolor("#0d0d0d")

for ax in axes:
    ax.set_facecolor("#16213e")
    ax.tick_params(colors="#888", labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a3a")
    ax.grid(True, which="both", color="#1f1f3a", linewidth=.6, linestyle="--")

ax0, ax1 = axes

def plot_loglog(ax, counts, color, title):
    xs = np.array(sorted(counts.keys()))
    ys = np.array([counts[x] for x in xs])
    xs, ys = xs[xs > 0], ys[xs > 0]
    ax.scatter(xs, ys, color=color, s=28, alpha=.85, zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title(title, color="#e0e0e0", fontsize=11)
    ax.set_xlabel("Degree (log)", color="#888", fontsize=9)
    ax.set_ylabel("Count (log)",  color="#888", fontsize=9)

plot_loglog(ax0, in_counts,  "#e8212a", "In-degree  (log–log)")
plot_loglog(ax1, out_counts, "#4a90d9", "Out-degree (log–log)")

plt.tight_layout(pad=2)
plt.savefig(f"{FIGS}/week1_degree_loglog.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: week1_degree_loglog.png")

# ── Figure 3: network drawing (giant component) ───────────────────────────────
Gu = G.to_undirected()
components = sorted(nx.connected_components(Gu), key=len, reverse=True)
GC = G.subgraph(components[0]).copy()

in_deg_map = dict(G.in_degree())
node_size  = [max(20, in_deg_map[n] * 12) for n in GC.nodes()]
node_color = [in_deg_map[n] for n in GC.nodes()]

fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor("#0d0d0d")
ax.set_facecolor("#0d0d0d")
ax.axis("off")

pos = nx.spring_layout(GC, seed=42, k=0.45)

nx.draw_networkx_edges(GC, pos, ax=ax,
                       edge_color="#1f1f3a", alpha=0.35, width=0.4,
                       arrows=False)

nodes_drawn = nx.draw_networkx_nodes(GC, pos, ax=ax,
                                     node_size=node_size,
                                     node_color=node_color,
                                     cmap=plt.cm.YlOrRd,
                                     alpha=0.9)

# label top-15 by in-degree
top15 = sorted(GC.nodes(), key=lambda n: in_deg_map[n], reverse=True)[:15]
labels = {n: name.get(n, n) for n in top15}
nx.draw_networkx_labels(GC, pos, labels=labels, ax=ax,
                        font_size=7, font_color="#ffffff", font_weight="bold")

sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd,
                            norm=plt.Normalize(vmin=min(node_color), vmax=max(node_color)))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.02, pad=0.01)
cbar.set_label("In-degree", color="#888", fontsize=9)
cbar.ax.yaxis.set_tick_params(color="#888")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#888", fontsize=8)

ax.set_title("Marvel Wikipedia Network — Giant Component", color="#e0e0e0",
             fontsize=13, pad=10)
plt.tight_layout()
plt.savefig(f"{FIGS}/week1_network.png", dpi=130, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: week1_network.png")

# ── Stats printout ────────────────────────────────────────────────────────────
print(f"\n── Component breakdown ──")
print(f"Giant component: {len(components[0])} nodes")
print(f"Other components ({len(components)-1} total): sizes = {sorted([len(c) for c in components[1:]], reverse=True)}")

print(f"\n── Top 10 by in-degree ──")
top_in = sorted(G.nodes(), key=lambda n: G.in_degree(n), reverse=True)[:10]
for n in top_in:
    print(f"  {name.get(n,n):35s}  in={G.in_degree(n):3d}  out={G.out_degree(n):3d}")

print(f"\n── Top 10 by out-degree ──")
top_out = sorted(G.nodes(), key=lambda n: G.out_degree(n), reverse=True)[:10]
for n in top_out:
    print(f"  {name.get(n,n):35s}  out={G.out_degree(n):3d}  in={G.in_degree(n):3d}")

print(f"\n── Isolated nodes ──")
isolates = list(nx.isolates(G))
for n in isolates:
    print(f"  {name.get(n,n)}")
