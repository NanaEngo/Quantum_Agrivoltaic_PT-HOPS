"""FMO complex network graph and coupling visualization using NetworkX."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import matplotlib.figure
    import networkx as nx

from ..config_loader import ConfigModel
from ..constants import (
    FMO_COUPLINGS_CM,
    FMO_NSITES,
    FMO_SITE_ENERGIES_CM,
    PLASMON_COUPLING_SITES,
    TRAPPING_SITES,
    NPoM_REFERENCE_COUPLING_CM,
    NPoM_REFERENCE_MODE_VOLUME_NM3,
)
from ..logging_config import get_logger

logger = get_logger("fmo_network")

# FMO site labels (bacteriochlorophyll-a numbering)
SITE_LABELS = {i: f"BChl {i + 1}" for i in range(FMO_NSITES)}

# Spatial layout (approximate geometry from Adolphs & Renger, 2006)
# x, y coordinates in arbitrary units
FMO_POSITIONS = {
    0: (0.0, 1.0),  # BChl 1
    1: (0.8, 0.6),  # BChl 2
    2: (0.5, -0.8),  # BChl 3 (trapping)
    3: (-0.5, -0.8),  # BChl 4 (trapping)
    4: (-0.8, 0.2),  # BChl 5
    5: (-0.4, 0.8),  # BChl 6
    6: (0.4, 0.8),  # BChl 7
    7: (0.0, 0.0),  # BChl 8
}


def build_fmo_graph(config: ConfigModel) -> "nx.Graph":
    """Build a networkx graph of the FMO complex with site energies and couplings.

    Returns a weighted undirected graph where:
    - Node attributes: site_energy_cm, label, is_trapping
    - Edge attributes: coupling_cm (inter-site coupling strength)
    """
    import networkx as nx

    G = nx.Graph()
    G.name = "FMO_BChl_a"

    # Add FMO site nodes
    for i in range(FMO_NSITES):
        G.add_node(
            i,
            site_energy_cm=FMO_SITE_ENERGIES_CM[i],
            label=SITE_LABELS[i],
            is_trapping=(i in TRAPPING_SITES),
            pos=FMO_POSITIONS[i],
            node_type="fmo",
        )

    # Add coupling edges
    for (i, j), val in FMO_COUPLINGS_CM.items():
        G.add_edge(i, j, coupling_cm=val, edge_type="fmo_coupling")

    logger.info(
        "FMO graph built: %d nodes, %d edges, trapping sites=%s",
        G.number_of_nodes(),
        G.number_of_edges(),
        TRAPPING_SITES,
    )
    return G


def add_plasmon_coupling(
    G: "nx.Graph",
    config: ConfigModel,
    mode_volume_nm3: float | None = None,
) -> float:
    """Add NPoM plasmon as an extra node coupled to PLASMON_COUPLING_SITES.

    Returns the effective plasmon coupling strength g0 in cm^-1.
    """

    if mode_volume_nm3 is None:
        mode_volume_nm3 = config.npom.mode_volume_nm3

    if mode_volume_nm3 < 1e-6:
        logger.warning(
            "Mode volume %.2e nm3 below guardrail; plasmon node skipped", mode_volume_nm3
        )
        return 0.0

    g0 = NPoM_REFERENCE_COUPLING_CM * np.sqrt(NPoM_REFERENCE_MODE_VOLUME_NM3 / mode_volume_nm3)

    G.add_node(
        PLASMON_INDEX := FMO_NSITES,
        site_energy_cm=0.0,
        label="NPoM",
        is_trapping=False,
        pos=(0.0, 1.8),
        node_type="plasmon",
    )

    for site_idx in PLASMON_COUPLING_SITES:
        G.add_edge(PLASMON_INDEX, site_idx, coupling_cm=g0, edge_type="plasmon_coupling")

    logger.info(
        "Plasmon node added: g0=%.1f cm-1, coupled to sites=%s, V=%.2f nm3",
        g0,
        PLASMON_COUPLING_SITES,
        mode_volume_nm3,
    )
    return float(g0)


def get_coupling_matrix(G: "nx.Graph") -> np.ndarray:
    """Extract the coupling matrix from the FMO graph (excluding plasmon node if present)."""
    n = FMO_NSITES
    H = np.zeros((n, n), dtype=complex)
    for i, j, data in G.edges(data=True):
        if i < n and j < n:
            c = data.get("coupling_cm", 0.0)
            H[i, j] = c
            H[j, i] = c
    for i in range(n):
        H[i, i] = FMO_SITE_ENERGIES_CM[i]
    return H


def get_degree_summary(G: "nx.Graph") -> dict[int, dict]:
    """Return per-node degree and total coupling strength for analysis."""
    summary = {}
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        total_coupling = sum(abs(G.edges[node, nbr].get("coupling_cm", 0.0)) for nbr in neighbors)
        summary[node] = {
            "label": G.nodes[node].get("label", str(node)),
            "degree": len(neighbors),
            "total_coupling_cm": total_coupling,
            "is_trapping": G.nodes[node].get("is_trapping", False),
        }
    return summary


def plot_fmo_network(
    G: "nx.Graph",
    *,
    save_path: str | None = None,
    show_plasmon: bool = True,
    figsize: tuple[int, int] = (8, 6),
    dpi: int = 150,
    title: str = "FMO Complex Coupling Network",
) -> "matplotlib.figure.Figure":
    """Render a publication-quality network diagram of the FMO complex.

    Nodes: size proportional to site energy, color by trapping/FMO/plasmon.
    Edges: width proportional to |coupling|, color by sign (blue=negative, red=positive).
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    pos = nx.get_node_attributes(G, "pos")
    if not pos:
        pos = nx.spring_layout(G, seed=42)

    # Filter plasmon if not requested
    if not show_plasmon:
        nodes_to_draw = [n for n in G.nodes() if G.nodes[n].get("node_type") != "plasmon"]
        G_draw = G.subgraph(nodes_to_draw).copy()
    else:
        G_draw = G

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Node properties
    node_colors = []
    node_sizes = []
    for n in G_draw.nodes():
        nt = G_draw.nodes[n].get("node_type", "fmo")
        energy = G_draw.nodes[n].get("site_energy_cm", 0)
        if nt == "plasmon":
            node_colors.append("#FF6B35")  # terracotta for plasmon
            node_sizes.append(1200)
        elif G_draw.nodes[n].get("is_trapping", False):
            node_colors.append("#2E8B57")  # sea green for trapping
            node_sizes.append(900 + energy * 2)
        else:
            node_colors.append("#4682B4")  # steel blue for regular FMO
            node_sizes.append(700 + energy * 2)

    # Edge properties
    edge_colors = []
    edge_widths = []
    for _u, _v, data in G_draw.edges(data=True):
        c = data.get("coupling_cm", 0.0)
        edge_colors.append("#2563EB" if c < 0 else "#DC2626")  # blue=neg, red=pos
        edge_widths.append(0.5 + abs(c) / 30.0)

    # Draw
    nx.draw_networkx_edges(
        G_draw,
        pos,
        ax=ax,
        edge_color=edge_colors,
        width=edge_widths,
        alpha=0.6,
        style="solid",
    )
    nx.draw_networkx_nodes(
        G_draw,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors="black",
        linewidths=1.2,
    )

    # Labels
    labels = {n: G_draw.nodes[n].get("label", str(n)) for n in G_draw.nodes()}
    nx.draw_networkx_labels(G_draw, pos, labels, ax=ax, font_size=8, font_weight="bold")

    # Edge labels (coupling values) for strong couplings only
    edge_labels = {}
    for u, v, data in G_draw.edges(data=True):
        c = data.get("coupling_cm", 0.0)
        if abs(c) > 20:
            edge_labels[(u, v)] = f"{c:.0f}"
    nx.draw_networkx_edge_labels(G_draw, pos, edge_labels, ax=ax, font_size=6)

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#4682B4",
            markersize=10,
            label="FMO BChl a",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#2E8B57",
            markersize=10,
            label="Trapping (RC)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#FF6B35",
            markersize=10,
            label="NPoM Plasmon",
        ),
        Line2D([0], [0], color="#2563EB", linewidth=2, label="J < 0 (negative)"),
        Line2D([0], [0], color="#DC2626", linewidth=2, label="J > 0 (positive)"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8, framealpha=0.9)

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")
        logger.info("FMO network figure saved: %s", save_path)

    return fig


def print_coupling_table(G: "nx.Graph") -> str:
    """Print a formatted table of all couplings in the graph."""
    lines = ["Site i | Site j | Coupling (cm-1) | Type", "-" * 50]
    for u, v, data in sorted(
        G.edges(data=True), key=lambda e: abs(e[2].get("coupling_cm", 0)), reverse=True
    ):
        c = data.get("coupling_cm", 0.0)
        etype = data.get("edge_type", "unknown")
        label_u = G.nodes[u].get("label", str(u))
        label_v = G.nodes[v].get("label", str(v))
        lines.append(f"{label_u:>8} | {label_v:>8} | {c:>14.1f} | {etype}")
    table = "\n".join(lines)
    logger.info("Coupling table:\n%s", table)
    return table
