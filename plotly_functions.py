import dataclasses

import networkx as nx

import pandas as pd
import numpy as np

from typing import Tuple, Any, Union, Collection, Mapping, NamedTuple, NewType

from plotly import graph_objects as go

from graph import Node

# @dataclasses.dataclass
# class NodeCollection:
#     nodes:list[Node]
#

class XYValues(NamedTuple):
    x: list[float | None]
    y: list[float | None]

NodeLayout = NewType('NodeLayout', dict[Node, tuple[float, float]])

def get_edge_xy(
        graph:nx.Graph,
        layout:NodeLayout
) -> XYValues:
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = layout[edge[0]]
        x1, y1 = layout[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    return XYValues(x=edge_x, y=edge_y)


def get_nodes_xy(layout:NodeLayout) -> XYValues:
    xs = []
    ys = []
    for (node, (x, y)) in layout.items():
        xs.append(x)
        ys.append(y)

    return XYValues(x=xs, y=ys)


def get_info_dicts(nodes_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Dicts, keyed by index (node) then column."""
    return nodes_df.drop(['X', 'Y', 'AnnotationText'], axis=1, errors='ignore').to_dict('index')


# def process_graph(graph:nx.Graph) -> Tuple[NodeLayout, XYValues, XYValues]:
#     """Turn graph obj into DF used by plotting function"""
#
#
#     return layout, node_xy, edge_xy


def plot_v2(
        graph
):
    """With graph object of table/row relationships,
    plot those as a network graph"""

    #todo show hide additional data
    #todo colour by table
    #todo hide tables

    layout = NodeLayout(nx.spring_layout(graph))
    nodes = list(layout.keys())
    node_xy = get_nodes_xy(layout)
    edge_xy = get_edge_xy(graph, layout)

    node_fmt = dict(
        size=2,
        color='white',
        line=dict(
            color='lightslategrey',
            width=2,
        )
    )

    nodes_go = go.Scatter(
        x=node_xy.x,
        y=node_xy.y,

        mode='markers',
        marker=node_fmt,
    )

    edges_go = go.Scatter(
        x=edge_xy.x,
        y=edge_xy.y,
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
        ),
        showlegend=False,
    )

    for node in nodes:
        annotation = f"<b>{node.str()}</b>"

        if node.data is not None:
            annotation += '<br>'+node.str_data()

        fig.add_annotation(
            text=annotation,
            yanchor='bottom',
            bgcolor='lightgrey',
            x=layout[node][0],
            y=layout[node][1],
            ax=layout[node][0],
            ay=layout[node][1],
        )

    return fig

# def plot_v1(
#         nodes:pd.DataFrame,
#         edges:pd.DataFrame
# ):
#     """Plot some simple data."""
#
#     node_fmt = dict(
#         size=2,
#         color='white',
#         line=dict(
#             color='lightslategrey',
#             width=2,
#         )
#     )
#
#     print(nodes.x, nodes.y)
#
#     nodes_go = go.Scatter(
#         x=nodes.X,
#         y=nodes.Y,
#         ids=nodes.index.map(str),
#         mode='markers',
#         marker=node_fmt,
#     )
#
#     edges_go = go.Scatter(
#         x=edges.X,
#         y=edges.Y,
#         mode='lines'
#     )
#
#     fig = go.Figure()
#     fig.add_trace(edges_go)
#     fig.add_trace(nodes_go)
#
#     fig.update_layout(
#         xaxis=dict(
#             showticklabels=False,
#             showgrid=False,
#             zeroline=False
#         ),
#         yaxis=dict(
#             showticklabels=False,
#             showgrid=False,
#             zeroline=False
#         )
#     )
#
#     for k, row in nodes.iterrows():
#         annotation = f"<b>{k}</b>"
#
#         if 'AnnotationText' in row.index:
#             more = row.AnnotationText
#             annotation = f"<br>{more}"
#
#         fig.add_annotation(
#             text=annotation,
#             yanchor='bottom',
#             bgcolor='lightgrey',
#             x=row.X,
#             y=row.Y,
#             ax=row.X,
#             ay=row.Y
#         )
#
#     return fig


def basic_graph(data=(('A', 'B'), ('B', 'C'), ('C', 'A'))) -> nx.Graph:
    """Get a nx.Graph with some edges and nodes."""
    G = nx.Graph()
    G.add_edges_from(data)
    return G


def basic_test():
    #G = basic_graph()
    from data_setup import setup_data
    from graph import get_graph
    from sqlalchemy import create_engine
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    setup_data(engine)
    G = get_graph(engine, 'table_a', 1)


    f = plot_v2(G)
    print(f.to_json()[:50], '... etc.')
    f.show()




if __name__ == '__main__':
    basic_test()