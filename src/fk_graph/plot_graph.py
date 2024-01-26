from fk_graph.plotly_functions import plot_v2, process_graph
import networkx as nx
import plotly as ply

def plot(graph:nx.Graph) -> ply.graph_objs.Figure:
    args = process_graph(graph)
    fig = plot_v2(*args)
    return fig
