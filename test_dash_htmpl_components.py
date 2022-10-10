from dash import Dash
from dash import html, dcc
import plotly.express as px
import pandas as pd


app = Dash(__name__)

colors = {
    'background': '#2b2b2b',
    'text': '#abb6c5'
}

markdown_text = '''
### This is a test block in Markdown

Let's try it!
'''


df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(data_frame=df, x="Fruit", y="Amount", color="City", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(
    style={'backgroundColor': colors["background"], 'padding': 10, 'flex': 1},
    children=[
        html.Label(children='Dropdown'),
        dcc.Dropdown(options=['New York City', 'Montréal', 'San Francisco'], value='New York City'),

        html.Br(),
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(options=['New York City', 'Montréal', 'San Francisco'], value=['Montréal', 'San Francisco'], multi=True),

        html.Br(),
        html.Label('Radio Items'),
        dcc.RadioItems(options=['New York City', 'Montréal', 'San Francisco'], value='Montréal'),
    ],
)

if __name__ == '__main__':
    app.run_server(debug=True)