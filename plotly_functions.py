import networkx as nx

import pandas as pd
import numpy as np

from typing import Tuple, Any, Union, Collection, Mapping

from plotly import graph_objects as go

from graph import Node

def get_edges_df(graph:nx.Graph, node_xy:pd.DataFrame):
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = node_xy.loc[edge[0], ['X', 'Y']]
        x1, y1 = node_xy.loc[edge[1], ['X', 'Y']]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    df = pd.DataFrame(dict(X=edge_x, Y=edge_y))
    return df


def get_nodes_df(graph:nx.Graph) -> pd.DataFrame:
    df = pd.DataFrame([
        {'Node':node, 'X':x, 'Y':y}
        for (node, (x, y)) in nx.spring_layout(graph).items()
    ]).set_index('Node')

    #df.index = [str(i) for i in df.index]

    return df


def get_info_dicts(nodes_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Dicts, keyed by index (node) then column."""
    return nodes_df.drop(['X', 'Y', 'AnnotationText'], axis=1, errors='ignore').to_dict('index')


def textify_additional_data(
        data: dict[str, dict[str, Any]],
        max_length:int=25,
) -> dict[str, str]:
    """Take data in form of {nodeID:{dataKey:dataValue}} and return text string for annotation."""

    out = {}

    for nodeid, values in data.items():
        #todo truncate long strings
        s = '\n'.join([f"{k}:{v}" for k, v in values.items()])
        out[nodeid]  = s

    return out



def process_graph(graph:nx.Graph) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Turn graph obj into DF used by plotting function"""
    nodes = get_nodes_df(graph)
    edges = get_edges_df(graph, nodes)
    
    return nodes, edges

def plot_v1(
        nodes:pd.DataFrame,
        edges:pd.DataFrame
):
    """Plot some simple data."""

    node_fmt = dict(
        size=2,
        color='white',
        line=dict(
            color='lightslategrey',
            width=2,
        )
    )

    nodes_go = go.Scatter(
        x=nodes.X,
        y=nodes.Y,
        ids=nodes.index.map(str),
        mode='markers',
        marker=node_fmt,
    )

    edges_go = go.Scatter(
        x=edges.X,
        y=edges.Y,
        mode='lines'
    )

    fig = go.Figure()
    fig.add_trace(edges_go)
    fig.add_trace(nodes_go)

    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        )
    )

    for k, row in nodes.iterrows():
        annotation = f"<b>{k}</b>"

        if 'AnnotationText' in row.index:
            more = row.AnnotationText
            annotation = f"<br>{more}"

        fig.add_annotation(
            text=annotation,
            yanchor='bottom',
            bgcolor='lightgrey',
            x=row.X,
            y=row.Y,
            ax=row.X,
            ay=row.Y
        )

    return fig


def basic_graph(data=(('A', 'B'), ('B', 'C'), ('C', 'A'))) -> nx.Graph:
    """Get a nx.Graph with some edges and nodes."""
    G = nx.Graph()
    G.add_edges_from(data)
    return G


def basic_test():
    G = basic_graph()
    nodes_df = get_nodes_df(G)
    nodes_df.loc[:, 'Table'] = ['TableA', 'TableB', 'TableB']
    nodes_df.loc[:, 'OtherInfo'] = ['Something', 'Some longish text oadijwoidjaodjw ad', np.nan]
    nodes_df.loc[:, 'AnnotationText'] = textify_additional_data(get_info_dicts(nodes_df))

    edges_xy = get_edges_df(G, nodes_df)

    f = plot_v1(nodes_df, edges_xy)
    f.show()




if __name__ == '__main__':
    basic_test()