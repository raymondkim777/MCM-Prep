import pandas as pd


def perc_list_to_rankings(perc_list: list):
    series = pd.Series(perc_list)
    return series.rank(method='min').tolist()


example = [0.1834862385321101,
0.11926605504587157,
0.1651376146788991,
0.1834862385321101,
0.1834862385321101,
0.1651376146788991]

print(perc_list_to_rankings(example))