from typing import List
from config import VibesterConfig
from dash import dcc

def loading(name:str, page: str, children:List=None) -> dcc.Loading:
    if children is None:
        children = []
    return dcc.Loading(
        children=children,
        id={"name": name, "type": "dot-loading", "page": page},
        type="dot",
        color='#339c40',
        style={
            "margin": "auto",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        },

    )

