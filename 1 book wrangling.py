import pandas as pd

df = pd.read_csv("./goodreads_library_export.csv")
df = df.loc[df["Read Count"] == 1].reset_index()

def get_year_month(date):
    return date[:-3]
df["Year-Month Added"] = df["Date Added"].apply(get_year_month)

def get_year(date):
    return date[:-6]
df["Year Added"] = df["Date Added"].apply(get_year)

def convert_str(date):
    return str(date)[:-2]
df["Original Publication Year"] = df["Original Publication Year"].apply(convert_str)

df.to_csv("./book_data.csv", index = False)