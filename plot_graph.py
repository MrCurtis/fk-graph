from plotly_functions import process_graph, plot_v1
import networkx as nx
import plotly as ply

def plot(graph:nx.Graph) -> ply.graph_objs.Figure:
    fig = plot_v1(*process_graph(graph))
    return fig