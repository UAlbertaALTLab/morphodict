"""
These functions are for interactive use by `weighting.ipynb`.
"""

import json
from functools import cache
from pathlib import Path

import pandas as pd
import numpy as np

SEARCH_QUALITY_DIR = Path(__file__).parent
BASE_DIR = SEARCH_QUALITY_DIR.parent


def dataframe_from_featuredump(filename):
    rows = []
    with open(filename, "rt") as f:
        for line in f:
            try:
                if json.loads(line) != []:
                    rows.append(json.loads(line))
                try:
                    print(int(line))
                except:
                    continue
            except:
                continue
    
    all_keys = set(list(k for row in rows for k in row.keys()))
    data = {}
    for key in all_keys:
        data[key] = {i: r.get(key, None) for i, r in enumerate(rows)}

    return pd.DataFrame(data)


@cache
def survey():
    return pd.read_csv(SEARCH_QUALITY_DIR / "sample.csv")


@cache
def survey_for_join():
    return tidy_survey_for_join(survey())


def tidy_survey_for_join(survey_df):
    """Tidy input survey for joining to results

    Melts, and adds survey_rank, survey_items_for_query columns.
    """
    survey_df = (
        survey_df.melt(id_vars=["Query"]).rename(
            columns={
                "variable": "survey_rank",
                "value": "wordform_text",
                "Query": "query",
            }
        )
    )[
        # this is to rearrange the column order
        ["query", "wordform_text", "survey_rank"]
    ]
    for i in [1, 2, 3]:
        survey_df.loc[survey_df["survey_rank"] == f"Nêhiyawêwin {i}", "survey_rank"] = i
    survey_df = survey_df.dropna()

    survey_items_for_query = (
        survey_df.groupby("query")["wordform_text"]
        .count()
        .rename("survey_items_for_query")
    )

    return survey_df.merge(survey_items_for_query, on="query")


def to_list_without_na(row):
    return sorted(list(row[~pd.isnull(row)]))


def top3_and_310_stats(result_data, rank_column="result_rank", survey_for_join_df=None):
    """Return top3 and 310 stats for result_data, using "result_rank" column"""

    # Use default survey if none specified
    if survey_for_join_df is None:
        survey_for_join_df = survey_for_join()

    joined = (
        survey_for_join_df.merge(result_data, how="left", on=["query", "wordform_text"])
        .sort_values(["query", "survey_rank"])
        .drop_duplicates(subset=["query", "survey_rank"])
    )

    joined = (
        joined.merge(
            joined.pivot(index=["query"], columns=["survey_rank"], values=[rank_column])
            .apply(to_list_without_na, axis=1)
            .rename("actual_result_ranks"),
            on="query",
        )
        .drop_duplicates("query")
        .reset_index()
    )

    def add_top3_and_310(df):
        def count_le_ten(l):
            """How many items in l are <= 10?"""
            l = np.array(l)
            return l[l <= 10].size

        return df.assign(
            top3=100 * df["actual_result_ranks"].map(len) / df["survey_items_for_query"]
        ).assign(
            three10=100
            * df["actual_result_ranks"].map(count_le_ten)
            / df["survey_items_for_query"]
        )

    return add_top3_and_310(joined)


def top3_and_310_stats_summary(*args, **kwargs):
    return top3_and_310_stats(*args, **kwargs)[["top3", "three10"]].mean()


def has_col_as_int(df, column_name):
    "Return a Series of values, 0 if column_name is NaN else 1"
    return (~pd.isnull(df[column_name])).astype(int)


@cache
def survey_wordforms_for_query():
    df = survey().copy().set_index("Query")
    rows = df.apply(to_list_without_na, axis=1)

    ret = {}
    for query, results in rows.iteritems():
        ret[query] = results
    return ret


def is_in_survey(df):
    """Helper function for adding column with whether a result is in the survey or not.

    UIse as `df.apply(is_in_survey, axis=1)`
    """
    return 1 if df["wordform_text"] in survey_wordforms_for_query()[df["query"]] else 0


def rank_by_predictor(df, model):
    df = df.assign(score=model.predict(df))
    return df.assign(
        result_rank=df[["query", "score"]]
        .groupby("query")
        .rank(ascending=False, method="first", na_option="bottom")
    ).sort_values(["query", "result_rank"])
