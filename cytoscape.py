import networkx as nx
import dash
import dash_cytoscape
import pandas as pd

def basic_graph(data=(('A', 'B'), ('B', 'C'), ('C', 'A'))) -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from(data)
    return G

def elements_from_networkx(graph:nx.Graph) -> list[dict]:
    elements = []
    for node in graph.nodes:
        elements.append(
            dict(
                data=dict(
                    id=node,
                    label=node,
                )
            )
        )
    for source, target in graph.edges():
        elements.append(
            dict(
                data=dict(
                    source=source,
                    target=target,
                )
            )
        )
    return elements

def launch_cytoscape(elements):
    from dash import Dash, html
    import dash_cytoscape as cyto

    app = Dash(__name__)
    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape-layout-1',
            elements=elements,
            style={'width': '100%', 'height': '350px'},
            layout={
                'name': 'cose'
            }
        )
    ])

    if __name__ == '__main__':
        app.run(debug=True, )