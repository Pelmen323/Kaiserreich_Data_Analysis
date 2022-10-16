from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os
import glob


app = Dash(__name__)
colors = {
    'background': '#2b2b2b',
    'text': '#abb6c5'
}

########################
### Common functions ###
########################

def sort_files_by_month(source, target, month):
    for i in source:
        if month in i:
            target.append(i)
    return target


def get_dropdown_options() -> list:
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, 'input')
    list_of_files = []
    sorted_list_of_files = []

    for filename in glob.iglob(filepath + '**/*.csv', recursive=True):
        list_of_files.append(os.path.basename(filename))

    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="December")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="November")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="October")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="September")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="August")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="July")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="June")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="May")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="April")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="March")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="February")
    sorted_list_of_files = sort_files_by_month(source=list_of_files, target=sorted_list_of_files, month="January")

    return sorted_list_of_files

def generate_mock_graph() -> object:
    d = {'col1': [1, 2], 'col2': [3, 4]}
    mock = pd.DataFrame(data=d)
    return px.line(data_frame=mock, x='col1', y='col2', title="No data found in this file. Please select other file from the dropdown.")

app.layout = html.Div(
    style={'backgroundColor': colors["background"], 'padding': 10, 'flex': 1},
    children=[
        html.Label(children='Argentina Winrate Over Time'),
        dcc.Dropdown(id='argentina-winrate-options', options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id='argentina-winrate-graph'),

        html.Label(children='Spanish Civil War Winrate'),
        dcc.Dropdown(id='scw-winrate-options', options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id='scw-winrate-graph'),

        html.Label(children='American Civil War Winrate'),
        dcc.Dropdown(id='acw-winrate-options', options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id='acw-winrate-graph'),
    ],
)

########################
### Functions for separate questions ###
########################

@app.callback(
    Output('argentina-winrate-graph', 'figure'),
    Input('argentina-winrate-options', 'value'))
def create_argentina_winrate_graph(input_file):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, f'input//{input_file}')
    import_doc = pd.read_csv(filepath)

    if "When did the Argentinian-Chilean War end?" in import_doc.columns and "Who won the Argentinian-Chilean war?" in import_doc.columns:    
        import_doc_wr_over_time = pd.DataFrame(columns=["Year", "Argentina", "Chile", "Peaceful Reunification", "Nobody"])

        for i in import_doc["When did the Argentinian-Chilean War end?"].value_counts().index:
            arg = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == 'Argentina'])
            chl = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == 'Chile'])
            peace = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == 'Peaceful Reunification'])
            nobody = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == 'Nobody'])
            new_row = pd.Series({"Year": i, "Argentina": arg, "Chile": chl, "Peaceful Reunification": peace, "Nobody": nobody})
            import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        prepared_data = import_doc_wr_over_time.sort_values('Year')
        fig = px.line(data_frame=prepared_data, x='Year', y=['Argentina', 'Chile', 'Peaceful Reunification', 'Nobody'], labels={'x':'Date', 'y':"Country"}, title="ARG war balance (wins per year)")


        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )

        return fig
    else:
        return generate_mock_graph()

@app.callback(
    Output('scw-winrate-graph', 'figure'),
    Input('scw-winrate-options', 'value'))
def create_scw_winrate_graph(input_file):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, f'input//{input_file}')
    import_doc = pd.read_csv(filepath)

    if "Who won the Spanish Civil War?" in import_doc.columns:    
        import_doc = import_doc["Who won the Spanish Civil War?"].value_counts()
        df = pd.DataFrame({"Country": import_doc.index, "Value": import_doc.values})
        fig = px.pie(data_frame=df, values="Value", names="Country", color_discrete_sequence=px.colors.qualitative.G10)

        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
        )

        return fig
    else:
        return generate_mock_graph()


@app.callback(
    Output('acw-winrate-graph', 'figure'),
    Input('acw-winrate-options', 'value'))
def create_acw_winrate_graph(input_file):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, f'input//{input_file}')
    import_doc = pd.read_csv(filepath)
    import_doc_wr_over_time = pd.DataFrame(data=pd.read_csv(filepath), columns=["Year", "USA", "CSA", "TEX", "PSA", "NEE", "Nobody"])

    if "When did the American Civil War end?" in import_doc.columns:
        for i in import_doc["When did the American Civil War end?"].value_counts().index:
            usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'USA'])
            csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'CSA'])
            tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'TEX'])
            psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'PSA'])
            nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'NEE'])
            nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == 'Nobody'])
            new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee,  "Nobody": nobody})
            import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        df = import_doc_wr_over_time.sort_values('Year')
        fig = px.line(data_frame=df , x='Year', y=["USA", "CSA", "TEX", "PSA", "NEE", "Nobody"], labels={'x':'Date', 'y':"Country"}, title="ACW war balance (wins per year)")

        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
        )

        return fig
    else:
        return generate_mock_graph()

if __name__ == '__main__':
    app.run_server(debug=True)