from plotly_functions import plot_v2
import networkx as nx
import plotly as ply

def plot(graph:nx.Graph) -> ply.graph_objs.Figure:
    fig = plot_v2(graph)
    return fig