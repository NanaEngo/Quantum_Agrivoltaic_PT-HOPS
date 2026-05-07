import matplotlib.pyplot as plt
import networkx as nx
import os
import scienceplots

# Apply publication-grade styling
plt.style.use(['science'])

def draw_fmo_schematic():
    G = nx.Graph()
    # FMO 7-site bacteriochlorophylls
    sites = range(1, 8)
    G.add_nodes_from(sites)
    
    # Major couplings (approximate Adolphs-Renger layout for visual)
    edges = [
        (1, 2, 100), (2, 3, 30), (3, 4, 55), (4, 5, 70),
        (5, 6, 85), (6, 7, 40), (1, 6, 35), (3, 7, -20)
    ]
    for u, v, w in edges:
        G.add_edge(u, v, weight=abs(w))
        
    pos = {
        1: (0, 2),
        2: (1, 2.5),
        3: (2, 2.2),
        4: (3, 1.5),
        5: (2.5, 0.5),
        6: (1.5, 1),
        7: (2, -0.5)
    }
    
    plt.figure(figsize=(8, 6), dpi=600)
    
    # Draw edges with width proportional to coupling
    edge_weights = [G[u][v]['weight'] / 15.0 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color="gray", alpha=0.6)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color="#2ca02c", node_size=1500, edgecolors="white", linewidths=2)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=16, font_color="white", font_weight="bold")
    
    # Add excitation arrow
    plt.annotate('Excitation\nPulse', xy=(0, 2.2), xytext=(-1, 2.5),
                 arrowprops=dict(facecolor='red', shrink=0.05),
                 fontsize=14, color='red', fontweight='bold')
                 
    # Add reaction center target
    plt.annotate('To Reaction\nCenter', xy=(2, -0.7), xytext=(2.5, -1.2),
                 arrowprops=dict(facecolor='blue', shrink=0.05),
                 fontsize=14, color='blue', fontweight='bold')

    plt.title("FMO Complex Energy Transfer Schematic", fontsize=18, fontweight='bold', pad=20)
    plt.axis("off")
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "reproducibility", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "FMO_Schematic_JPCL.png")
    plt.savefig(out_path, format="png", bbox_inches="tight", dpi=600)
    print(f"✅ Schematic successfully generated at: {out_path}")

if __name__ == "__main__":
    draw_fmo_schematic()
