import os
import glob
import pandas as pd
from collections import Counter

questions_list = [
    '## Europe',
    'Who won the Franco-German part of the 2nd Weltkrieg?',
    'Who won the Russo-German part of the 2nd Weltkrieg?',
    'Who won the Spanish Civil War?',
    'Who controls most of the Italian peninsula?',
    '## America',
    'Did the Entente collapse?',
    "Who won the American Civil War?",
    'Who won the Argentinian-Chilean war?',
    '## Asia',
    'Who was the victor of the League War?',
    'How far did Japan push into China (if they attacked)?',
    'Who controls most of the Indian subcontinent?',
]


def read_csv_file() -> pd.DataFrame:
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, "input//")
    for filename in glob.iglob(filepath + '**/*.csv', recursive=True):
        print(filename)
        return pd.read_csv(filename)


def extract_question_data(question_name: str, df: pd.DataFrame):
    # Convert dataframe to series that includes answers to only one question
    series = df[question_name]
    # Convert series to list
    data_list = series.tolist()
    # Dict with counted values
    data_dict = dict(Counter(data_list))
    sorted_dict = dict(sorted(data_dict.items(), key=lambda x:x[1], reverse=True))
    return sorted_dict
        


def main():
    csv_df = read_csv_file()
    for q in questions_list:
        ## Is header
        if "##" in q:
            print(q)
        ## Is a normal question
        else:
            dict_as_str = str(extract_question_data(q, csv_df))[1:-1].replace("'", "")
            print(f'- *{q}*\n{dict_as_str}')


if __name__ == "__main__":
    main()
