from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

import os
import glob
import flask
import json
from flask_caching import Cache

server = flask.Flask(__name__)
app = Dash(server=server)
cache = Cache(app.server, config={ 'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache-directory'})
TIMEOUT = 300

colors = { "background": "#2b2b2b", "text": "#abb6c5", "grid": "#abb6c5"}
line_widths = {"plot_line": 3, "grid_xaxis": 0.5, "grid_yaxis": 0.5}

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
    Output("2wk-winrate-pie", "figure"),
    Input("2wk-winrate-data-source", "value"),
    Input("2wk-winrate-war-configuration", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_2wk_winrate_pie(input_file, war_configuration):
    """The Second Weltkrieg winrate pie

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)


    if "Who won the Franco-German part of the 2nd Weltkrieg?" in import_doc.columns:
        if war_configuration == "Germany-France":
            import_doc = import_doc["Who won the Franco-German part of the 2nd Weltkrieg?"].value_counts()
        elif war_configuration == "Germany-Russia":
            import_doc = import_doc["Who won the Russo-German part of the 2nd Weltkrieg?"].value_counts()
        else:
            return generate_mock_graph()
        df = pd.DataFrame({"Country": import_doc.index, "Value": import_doc.values})
        fig = px.pie(
            data_frame=df,
            values="Value",
            names="Country",
            title="2WK winrate pie",
            color="Country",
            color_discrete_map={
                "Reichspakt": "rgb(93,93,61)",
                "Internationale": "rgb(10,54,175)",
                "Russia": "rgb(0,127,14)",
                "Socialist Russia": "rgb(175,13,0)",
                "Nobody": "grey",
            },
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
    Output("2wk-winrate-graph", "figure"),
    Input("2wk-winrate-data-source", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_2wk_winrate_graph(input_file):
    """2WK winrate graph

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)

    if "If the Reichspakt lost the 2nd Weltkrieg, when did they fall?" in import_doc.columns and "Who won the Franco-German part of the 2nd Weltkrieg?" in import_doc.columns:
        import_doc_wr_over_time = pd.DataFrame(columns=["Year", "Internationale", "Reichspakt", "Nobody"])
        x = import_doc["If the Reichspakt lost the 2nd Weltkrieg, when did they fall?"]
        # Create a single Series with war ending date - since the question is split in 2, we need to unify data to create a graph
        for i, value in enumerate(x):
            if pd.isnull(value):
                if pd.isnull(import_doc["If the Internationale lost the 2nd Weltkrieg, when did France fall?"][i]):
                    x[i] = "Did not end"
                else:
                    x[i] = import_doc["If the Internationale lost the 2nd Weltkrieg, when did France fall?"][i]

        # Convert float values to int
        for i, value in enumerate(x):
            if isinstance(value, float):
                x[i] = int(x[i])

        # Convert series data type to str
        x = pd.Series(data=x, dtype="string")

        for i in x.value_counts().index:
            internationale = len(import_doc[import_doc["If the Reichspakt lost the 2nd Weltkrieg, when did they fall?"] == i][import_doc["Who won the Franco-German part of the 2nd Weltkrieg?"] == 'Internationale'])
            reichspakt = len(import_doc[import_doc["If the Reichspakt lost the 2nd Weltkrieg, when did they fall?"] == i][import_doc["Who won the Franco-German part of the 2nd Weltkrieg?"] == 'Reichspakt'])
            nobody = len(import_doc[import_doc["If the Reichspakt lost the 2nd Weltkrieg, when did they fall?"] == i][import_doc["Who won the Franco-German part of the 2nd Weltkrieg?"] == 'Nobody'])
            new_row = pd.Series({"Year": i, "Internationale": internationale, "Reichspakt": reichspakt, "Nobody": nobody})
            import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        prepared_data = import_doc_wr_over_time.sort_values(by="Year")
        px.line(data_frame=prepared_data, x='Year', y=['Internationale', 'Reichspakt', 'Nobody'], labels={'x':'Date', 'y':"Country"})
        fig = px.line(
            data_frame=prepared_data,
            x="Year",
            y=['Internationale', 'Reichspakt'],
            labels={"x": "Date", "y": "Country"},
            title="FRA-GER winrate graph",
            color="variable",
            color_discrete_map={
                "Reichspakt": "rgb(93,93,61)",
                "Internationale": "rgb(10,54,175)",
                "Nobody": "grey",
            },
        )

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )
        fig.update_traces(line=dict(width=line_widths["plot_line"]))
        fig.update_xaxes(showgrid=True, gridwidth=line_widths["grid_xaxis"], gridcolor=colors["grid"])
        fig.update_yaxes(showgrid=True, gridwidth=line_widths["grid_yaxis"], gridcolor=colors["grid"])

        return fig
    else:
        return generate_mock_graph()


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
                "Nobody": "grey",
            },
        )

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )
        fig.update_traces(line=dict(width=line_widths["plot_line"]))
        fig.update_xaxes(showgrid=True, gridwidth=line_widths["grid_xaxis"], gridcolor=colors["grid"])
        fig.update_yaxes(showgrid=True, gridwidth=line_widths["grid_yaxis"], gridcolor=colors["grid"])

        return fig
    else:
        return generate_mock_graph()


@app.callback(
    Output("scw-winrate-pie", "figure"),
    Input("scw-winrate-data-source", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_scw_winrate_pie(input_file):
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
                "Nobody": "grey",
            },
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
    Output("acw-winrate-pie", "figure"),
    Input("acw-winrate-data-source", "value"),
    Input("acw-winrate-war-configuration", "value"))
@cache.memoize(timeout=TIMEOUT)
def create_acw_winrate_pie(input_file, war_configuration):
    """American Civil War winrate pie

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value
        war_configuration (str): Graph option

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)

    if "When did the American Civil War end?" in import_doc.columns:
        if war_configuration == "All":
            if "Who won the American Civil War?" in import_doc.columns:
                import_doc = import_doc["Who won the American Civil War?"].value_counts()
            else:
                return generate_mock_graph()
        elif war_configuration == "2-Way War":
            import_doc = import_doc["If the American Civil War was a two-way, who won it?"].value_counts()
        elif war_configuration == "3-Way War":
            import_doc = import_doc["If the American Civil War was a three-way, who won it?"].value_counts()
        elif war_configuration == "Mac Goes East":
            import_doc = import_doc["If MacArthur retreated EAST, who won the ACW?"].value_counts()
        elif war_configuration == "Mac Goes West":
            import_doc = import_doc["If MacArthur retreated WEST, who won the ACW?"].value_counts()
        elif war_configuration == "Mac Doesn't Retreat":
            import_doc = import_doc["If MacArthur did NOT retreat, who won the ACW?"].value_counts()

        df = pd.DataFrame({"Country": import_doc.index, "Value": import_doc.values})
        fig = px.pie(
            data_frame=df,
            values="Value",
            names="Country",
            title="ACW winrate pie",
            color="Country",
            color_discrete_map={
                "USA": "rgb(20,133,237)",
                "CSA": "rgb(178,34,52)",
                "TEX": "rgb(60,59,110)",
                "PSA": "rgb(242,205,94)",
                "NEE": "rgb(0,107,51)",
                "Nobody": "grey",
            },
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
def create_acw_winrate_graph(input_file, war_configuration):
    """American Civil War winrate graph

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value
        war_configuration (str): Graph option

    Returns:
        fig: graph object
    """
    import_doc = read_csv_file(input_file)
    import_doc_wr_over_time = pd.DataFrame(data=import_doc, columns=["Year", "USA", "CSA", "TEX", "PSA", "NEE", "Nobody"])

    if "When did the American Civil War end?" in import_doc.columns:
        if war_configuration == "All":
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

        elif war_configuration == "2-Way War":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a two-way, who won it?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif war_configuration == "3-Way War":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If the American Civil War was a three-way, who won it?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif war_configuration == "Mac Goes East":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated EAST, who won the ACW?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif war_configuration == "Mac Goes West":
            for i in import_doc["When did the American Civil War end?"].value_counts().index:
                usa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'USA'])
                csa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'CSA'])
                tex = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'TEX'])
                psa = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'PSA'])
                nee = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'NEE'])
                nobody = len(import_doc[import_doc["When did the American Civil War end?"] == i][import_doc["If MacArthur retreated WEST, who won the ACW?"] == 'Nobody'])
                new_row = pd.Series({"Year": i, "USA": usa, "CSA": csa, "TEX": tex, "PSA": psa, "NEE": nee, "Nobody": nobody})
                import_doc_wr_over_time = import_doc_wr_over_time.append(new_row, ignore_index=True)

        elif war_configuration == "Mac Doesn't Retreat":
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
        fig.update_traces(line=dict(width=line_widths["plot_line"]))
        fig.update_xaxes(showgrid=True, gridwidth=line_widths["grid_xaxis"], gridcolor=colors["grid"])
        fig.update_yaxes(showgrid=True, gridwidth=line_widths["grid_yaxis"], gridcolor=colors["grid"])

        return fig
    else:
        return generate_mock_graph()

@app.callback(
    Output("map-graph", "figure"),
    Input("map-data-source", "value"))
def create_map(input_file):
    """Spanish Civil War winrate pie

    Args:
        input_file (_type_): .csv file name imported by the function. Is defined by the dropdown value

    Returns:
        fig: graph object
    """
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, "input//map.geojson")
    with open(filepath, 'r', encoding="UTF-8") as file:
        json_obj = file.read()
    geojson = json.loads(json_obj)
    import_doc = read_csv_file(input_file)

    if "Num of divisions" in import_doc.columns:
        # import_doc = import_doc["Who won the Spanish Civil War?"].value_counts()
        df = pd.DataFrame({"Country": ["USA", "DEU", "FRA", "ARG"], "Divisions number": [100, 150, 125, 0]})
        fig = px.choropleth(
            df, geojson=geojson, locations="Country", featureidkey="properties.adm0_a3", color="Divisions number")

        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            legend_title="Country",
        )
        # Map - specific tweaks
        fig.update_layout(
            autosize=False,
            margin = dict(l=0, r=0, b=0, t=0, pad=4, autoexpand=True),
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
        html.Label(children="Links to items", id="contents-header"),
        html.Br(),
        html.A(children="The Second Weltkrieg", href="#2wk-section", className="contents-link"),
        html.Br(),
        html.A(children="Argentina-Chile", href="argentina-section", className="contents-link"),
        html.Br(),
        html.A(children="Spanish Civil War", href="#scw-section", className="contents-link"),
        html.Br(),
        html.A(children="American Civil War", href="#acw-section", className="contents-link"),
        html.Br(),

        html.Label(children="The Second Weltkrieg", id="2wk-section"),
        dcc.Dropdown(id="2wk-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Dropdown(id="2wk-winrate-war-configuration", options=["Germany-France", "Germany-Russia"], value="Germany-France", clearable=False),
        dcc.Graph(id="2wk-winrate-pie"),
        dcc.Graph(id="2wk-winrate-graph"),
        
        html.Label(children="Argentinean-Chilean War", id="argentina-section"),
        dcc.Dropdown(id="argentina-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id="argentina-winrate-graph"),
        html.Br(),

        html.Label(children="Spanish Civil War", id="scw-section"),
        dcc.Dropdown(id="scw-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id="scw-winrate-pie"),
        html.Br(),

        html.Label(children="American Civil War", id="acw-section"),
        dcc.Dropdown(id="acw-winrate-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Dropdown(id="acw-winrate-war-configuration", options=["All", "2-Way War", "3-Way War", "Mac Goes West", "Mac Goes East", "Mac Doesn't Retreat"], value="All", clearable=False),
        dcc.Graph(id="acw-winrate-pie"),
        dcc.Graph(id="acw-winrate-graph"),

        html.Br(),
        html.Label(children="Test Map", id="map-section"),
        dcc.Dropdown(id="map-data-source", options=get_dropdown_options(), value=get_dropdown_options()[0], clearable=False),
        dcc.Graph(id="map-graph"),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
