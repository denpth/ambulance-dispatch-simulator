import csv
import networkx as nx
import matplotlib.pyplot as plt

from dispatch import NETWORK_FILE


def load_edges():
    """Load graph edges with travel time weights from the CSV file."""
    edges = []
    with open(NETWORK_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            weight = float(row['Travel Time']) + float(row['Traffic Delay'])
            edges.append((row['Start'], row['End'], {'weight': weight}))
    return edges


def visualize():
    """Display the network graph using networkx and matplotlib."""
    edges = load_edges()
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.show()


if __name__ == '__main__':
    visualize()