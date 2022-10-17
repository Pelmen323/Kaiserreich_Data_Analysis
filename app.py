from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

import os
import glob
import flask
from flask_caching import Cache

server = flask.Flask(__name__)
app = Dash(server=server)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 300
colors = {
    "background": "#2b2b2b",
    "text": "#abb6c5"
}

####################
# Common functions #
####################


def sort_files_by_month(source, target, month):
    for i in source:
        if month in i:
            target.append(i)
    return target


def get_dropdown_options() -> list:
    """Extracts all .scv files from /input and returns a list with their names where the files are sorted based on the month in the filename.
    E.g. file with December in name will be placed earlier than July and so on

    Returns:
        list: Sorted list of files to use in graph dropdowns
    """
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, "input")
    list_of_files = []
    sorted_list_of_files = []

    for filename in glob.iglob(filepath + "**/*.csv", recursive=True):
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
    """Returns blank graph object to display if target file doesn't have required data

    Returns:
        object: blank px.line graph
    """
    d = {"col1": [0], "col2": [0]}
    mock = pd.DataFrame(data=d)
    fig = px.line(data_frame=mock, x="col1", y="col2", title="No data found in this file. Please select other file from the dropdown.")
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"]
    )
    return fig


def read_csv_file(input_file: str) -> pd.DataFrame:
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, f"input//{input_file}")
    return pd.read_csv(filepath)

####################################
# Functions for separate questions #
####################################


@app.callback(
    Output("argentina-winrate-graph", "figure"),
    Input("argentina-winrate-data-source", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_argentina_winrate_graph(input_file):
    """ARG-CHL winrate graph

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)

    if "When did the Argentinian-Chilean War end?" in import_doc.columns and "Who won the Argentinian-Chilean war?" in import_doc.columns:
        import_doc_wr_over_time = pd.DataFrame(columns=["Year", "Argentina", "Chile", "Peaceful Reunification", "Nobody"])

        for i in import_doc["When did the Argentinian-Chilean War end?"].value_counts().index:
            arg = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == "Argentina"])
            chl = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == "Chile"])
            peace = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == "Peaceful Reunification"])
            nobody = len(import_doc[import_doc["When did the Argentinian-Chilean War end?"] == i][import_doc["Who won the Argentinian-Chilean war?"] == "Nobody"])
            new_row = pd.Series({"Year": i, "Argentina": arg, "Chile": chl, "Peaceful Reunification": peace, "Nobody": nobody})
            import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        prepared_data = import_doc_wr_over_time.sort_values("Year")
        fig = px.line(
            data_frame=prepared_data,
            x="Year",
            y=["Argentina", "Chile", "Peaceful Reunification", "Nobody"],
            labels={"x": "Date", "y": "Country"},
            title="ARG-CHL winrate graph",
            color="variable",
            color_discrete_map={
                "Argentina": "rgb(153,217,234)",
                "Chile": "rgb(150,71,71)",
                "Peaceful Reunification": "rgb(180,217,214)",
                "Nobody": "white",
            }
        )

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )

        return fig
    else:
        return generate_mock_graph()


@app.callback(
    Output("scw-winrate-graph", "figure"),
    Input("scw-winrate-data-source", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_scw_winrate_graph(input_file):
    """Spanish Civil War winrate pie

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)

    if "Who won the Spanish Civil War?" in import_doc.columns:
        import_doc = import_doc["Who won the Spanish Civil War?"].value_counts()
        df = pd.DataFrame({"Country": import_doc.index, "Value": import_doc.values})
        fig = px.pie(
            data_frame=df,
            values="Value",
            names="Country",
            title="SCW winrate pie",
            color="Country",
            color_discrete_map={
                "CNT-FAI": "rgb(204,0,0)",
                "Kingdom of Spain": "rgb(242,205,94)",
                "Carlistis": "rgb(200,100,31)",
                "Nobody": "white",
            }
        )

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )

        return fig
    else:
        return generate_mock_graph()


@app.callback(
    Output("acw-winrate-graph", "figure"),
    Input("acw-winrate-data-source", "value"),
    Input("acw-winrate-war-configuration", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_acw_winrate_graph(input_file, acw_war_configuration):
    """American Civil War winrate graph

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)
    import_doc_wr_over_time = pd.DataFrame(data=import_doc, columns=["Year", "USA", "CSA", "TEX", "PSA", "NEE", "Nobody"])

    if "When did the American Civil War end?" in import_doc.columns:
        if acw_war_configuration == "All":
            if "Who won the American Civil War?" in import_doc.columns:
                for i in import_doc["When did the American Civil War end?"].value_counts().index:
                    usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "USA"])
                    csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "CSA"])
                    tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "TEX"])
                    psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "PSA"])
                    nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "NEE"])
                    nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["Who won the American Civil War?"] == "Nobody"])
                    new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                    import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)
            else:
                return generate_mock_graph()

        elif acw_war_configuration == "2-Way War":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif acw_war_configuration == "3-Way War":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif acw_war_configuration == "Mac Goes East":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif acw_war_configuration == "Mac Goes West":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif acw_war_configuration == "Mac Doesn't Retreat":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur did NOT retreat, who won the ACW?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        df = import_doc_wr_over_time.sort_values("Year")
        fig = px.line(
            data_frame=df,
            x="Year",
            y=["USA", "CSA", "TEX", "PSA", "NEE"],
            labels={"x": "Date", "y": "Country"},
            title="ACW winrate graph",
            color="variable",
            color_discrete_map={
                "USA": "rgb(20,133,237)",
                "CSA": "rgb(178,34,52)",
                "TEX": "rgb(60,59,110)",
                "PSA": "rgb(242,205,94)",
                "NEE": "rgb(0,107,51)",
                "Nobody": "grey",
            }
        )

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )

        return fig
    else:
        return generate_mock_graph()

###############
# Application #
###############


app.layout = html.Div(
    style={"backgroundColor": colors["background"], "padding": 10, "flex": 1},
    children=[
        html.Label(children="Argentinean-Chilean War"),
        dcc.Dropdown(id="argentina-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id="argentina-winrate-graph"),

        html.Label(children="Spanish Civil War"),
        dcc.Dropdown(id="scw-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id="scw-winrate-graph"),

        html.Label(children="American Civil War"),
        dcc.Dropdown(id="acw-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Dropdown(id="acw-winrate-war-configuration", options=["All", "2-Way War", "3-Way War", "Mac Goes West", "Mac Goes East", "Mac Doesn't Retreat"], value="All", clearable=False),
        dcc.Graph(id="acw-winrate-graph"),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
