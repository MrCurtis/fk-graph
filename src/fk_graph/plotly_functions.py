import dataclasses
import os

import itertools

import networkx as nx

import pandas as pd
import numpy as np

from typing import Tuple, Any, Union, Collection, Mapping, NamedTuple, NewType, TypedDict

import plotly.express as px
from plotly import graph_objects as go

from fk_graph.graph import Node

import flask



# @dataclasses.dataclass
# class NodeCollection:
#     nodes:list[Node]
#

class XYValues(NamedTuple):
    x: list[float | None]
    y: list[float | None]

NodeLayout = NewType('NodeLayout', dict[Node, tuple[float, float]])


class DataDict(TypedDict):
    layout: NodeLayout = None
    node_xy: XYValues = None
    edge_xy: XYValues = None

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

from dash import dash, dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.html import Div

def color_cycler():
    i = itertools.cycle(px.colors.qualitative.Pastel1)
    yield next(i)

class TableColors:
    def __init__(
            self,
            nodes:list[Node],
            palette:list[str] = px.colors.qualitative.Pastel1
    ):
        tables = set([n.table for n in nodes])

        self.table_colors = dict(zip(
            tables,
            itertools.cycle(palette)
        ))

    def get_color(self, node:Node):
        return self.table_colors[
            node.table
        ]

    def __getitem__(self, node):
        return self.get_color(node)

def add_annotations(
        fig, nodes, layout, show_data, table_colors,
        max_rows=10, max_row_len=20):

    fig.layout.annotations = []
    for node in nodes:
        node:Node
        annotation = f"<b>{node.str()}</b>"
        if show_data:
            if node.data is not None:
                annotation += '<br>' + node.str_data(
                    max_rows=max_rows,
                    max_row_length=max_row_len
                )

        fig.add_annotation(
            text=annotation,
            yanchor='bottom',
            bgcolor=table_colors[node],
            x=layout[node][0],
            y=layout[node][1],
            ax=layout[node][0],
            ay=layout[node][1],
        )
    return fig

BLOCK = dict(display='block')
INLINEBLK = dict(display='inline-block')
def run_app(db_graph:nx.Graph, host=os.getenv("HOST", "127.0.0.1")):

    #Interactivities:
    # - hide specific tables
    # - alter node max rows


    width, height = 800, 900
    default_input_values = {'height':height, 'width':width, 'max rows':10,
                            'max row length':25}

    layout, nodes, node_xy, edge_xy = process_graph(db_graph)

    table_colors = TableColors(
        nodes
    )

    fig = plot_v2(layout, nodes, node_xy, edge_xy)

    fig.update_layout(
        width=width,
        height=height,
    )

    dash_graph = dcc.Graph(
        id=f'dash-graph',
        config={},
        figure=fig,
    )


    # **CONTROLS**
    max_len_row, max_rows = [
        html.Div([
            html.Label(f"{hw}:  ", htmlFor=f'{hw}-input', style=dict(display='block')),
            dcc.Input(id=f'{hw}-input', value=default_input_values[hw], type='number'),

        ], style=dict(display='inline-block'))
        for hw in ('max rows', 'max row length')
    ]


    # show hide Node.data information
    show_data_button = dcc.Checklist(['Show table values'], ['Show table values'], id='show-data')
    @callback(
        Output('dash-graph', 'figure'),
        Input('show-data', 'value'),
        Input('max rows-input', 'value'),
        Input('max row length-input', 'value'),
        #State('dash-graph', 'figure'),
    )
    def show_hide_annotations(show_data, max_rows, max_row_len):
        figure = add_annotations(fig, nodes, layout, show_data, table_colors, max_rows, max_row_len)

        return figure

    # control for figure height, width
    height_input, width_input = [
        html.Div([
            html.Label(f"{hw}:  ", htmlFor=f'{hw}-input', style=dict(display='block')),
            dcc.Input(id=f'{hw}-input', value=default_input_values[hw], type='number'),

        ], style=dict(display='inline-block'))
        for hw in ('width', 'height')
    ]

    @callback(
        Output('dash-graph', 'figure', allow_duplicate=True, ),
        Input('height-input', 'value'),
        Input('width-input', 'value'),
        prevent_initial_call=True
    )
    def update_height_width(h, w):
        if (h < 10) or (w < 10):
            raise PreventUpdate
        fig.update_layout(
            height=h,
            width=w,
        )
        return fig

    server = flask.Flask(__name__)

    app = dash.Dash(
        'relational-graph',
        server=server,
        prevent_initial_callbacks='initial_duplicate',

    )

    app.layout = Div([
        html.Div([
            show_data_button,
            Div([height_input, width_input], style=BLOCK),
            Div([max_rows, max_len_row], style=BLOCK),
        ], style=INLINEBLK),
        dash_graph
    ])

    app.run(host=host, port=8050, debug=True)

def process_graph(graph) -> (NodeLayout, list[Node], XYValues, XYValues):
    layout = NodeLayout(nx.spring_layout(graph))
    nodes = list(layout.keys())
    node_xy = get_nodes_xy(layout)
    edge_xy = get_edge_xy(graph, layout)
    return layout, nodes, node_xy, edge_xy


def plot_v2(layout, nodes, node_xy, edge_xy):
    """With graph object of table/row relationships,
    plot those as a network graph"""

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

    fig = add_annotations(
        fig, nodes, layout, True, TableColors(nodes),
    )

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

    return fig


def basic_graph(data=(('A', 'B'), ('B', 'C'), ('C', 'A'))) -> nx.Graph:
    """Get a nx.Graph with some edges and nodes."""
    G = nx.Graph()
    G.add_edges_from(data)
    return G


def _get_test_graph() -> nx.Graph:
    from fk_graph.data_setup import setup_data
    from fk_graph.graph import get_graph
    from sqlalchemy import create_engine
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    setup_data(engine)
    G = get_graph(engine, 'table_a', 1)
    return G


def basic_test():
    G = _get_test_graph()
    args = process_graph(G)

    f = plot_v2(*args)
    print(f.to_json()[:50], '... etc.')
    f.show()


def dash_app():
    G = _get_test_graph()
    run_app(G, host='10.0.0.8')


if __name__ == '__main__':
    dash_app()
    pass
