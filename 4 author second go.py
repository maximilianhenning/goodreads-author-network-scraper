import pandas as pd
import requests
import re
import ast
import datetime as dt
from bs4 import BeautifulSoup

edges_df = pd.read_csv("./edges_incomplete.csv")
nodes_df = pd.read_csv("./nodes_incomplete.csv")

edges_sources = edges_df["Source"].tolist()
edges_targets = edges_df["Target"].tolist()
edges_ids = list(set(edges_sources + edges_targets))
nodes_ids = nodes_df["id"].tolist()
nodes_ids = [int(id) for id in nodes_ids if str(id) != "nan"]
# Test author list
# second_ids = [656983]
# Actual author list
second_ids = [id for id in edges_ids if id not in nodes_ids]
second_ids_dict = dict([(id, 0) for id in second_ids])

# Scrape for the second time

def author_info_scraper(author_id, book_number):
    print("Working on author ID:", author_id)
    response = requests.get(str("https://www.goodreads.com/author/show/" + str(author_id)))
    html_string = response.text
    doc = BeautifulSoup(html_string, "html.parser")
    data_divs = doc.find_all("div", attrs = {"class": "dataItem"})
    genre_divs = []
    influence_divs = []
    for div in data_divs:
        if "genres" in str(div):
            genre_divs.append(div)
        if "author/show" in str(div):
            influence_divs.append(div)
    # Name
    name_div = doc.find("h1", attrs = {"class": "authorName"})
    if name_div:
        name = name_div.text.replace("\\n", "").strip()
    else:
        name = "nan"
    # Born date
    born_div = doc.find("div", attrs = {"itemprop": "birthDate"})
    if born_div:
        born_date_text = born_div.text.replace("\\n", "").strip()
        born_date_datetime = dt.datetime.strptime(born_date_text, "%B %d, %Y")
        born_date = born_date_datetime.strftime("%Y-%m-%d")
    else:
        born_date = "nan"
    # Born place
    # Died
    died_div = doc.find("div", attrs = {"itemprop": "deathDate"})
    if died_div:
        died_date_text = died_div.text.replace("\\n", "").strip()
        died_date_datetime = dt.datetime.strptime(died_date_text, "%B %d, %Y")
        died_date = died_date_datetime.strftime("%Y-%m-%d")
    else:
        died_date = "nan"
    # Genres
    genres = []
    for div in genre_divs:
        genre_text = div.text.replace("\\n", "").strip()
        genres.append(genre_text)
    # Influence names
    influence_names = []
    for div in influence_divs:
        influence_name = div.text.replace("\\n", "").strip()
        influence_names.append(influence_name)
    # Influence IDs
    influence_ids = []
    for div in influence_divs:
        influence_list = str(div).split(",")
        for div in influence_list:
            if "author/show" in div:
                influence_id = re.sub("[^0-9]", "", div)
                if len(influence_id) < 10:
                    influence_ids.append(influence_id)
    # Gender
    text_div = doc.find("div", attrs = {"class": "aboutAuthorInfo"})
    if text_div:
        text_tokenized = text_div.text.lower().split(" ")
        she_counter = 0
        he_counter = 0
        for token in text_tokenized:
            if token == "she":
                she_counter += 1
            if token == "he":
                he_counter += 1
        if she_counter > he_counter:
            gender = "female"
        else:
            gender = "male"
    else:
        gender = "nan"
    return [name, book_number, born_date, died_date, genres, influence_names, influence_ids, gender]
for author_id in second_ids_dict:
    second_ids_dict[author_id] = author_info_scraper(author_id, second_ids_dict[author_id])
second_df = pd.DataFrame.from_dict(second_ids_dict, orient = "index", columns = ["name",
                                                                        "book_number",
                                                                        "born_date", 
                                                                        "died_date",
                                                                        "genres",
                                                                        "influence_names",
                                                                        "influence_ids",
                                                                        "gender"])
second_df.reset_index(inplace = True)
second_df.rename(columns = {"index": "id"}, inplace = True)
second_df = second_df.loc[second_df["id"] != "nan"]
second_df["id"] = second_df["id"].astype("Int64")

# Get dictionary of IDs not in first or second interest level

second_ids = second_df["id"].tolist()
done_ids = second_ids + nodes_ids + edges_ids
done_ids = list(set(done_ids))
second_influences = []
second_influences_lists = second_df["influence_ids"].tolist()
for list in second_influences_lists:
    for id in list:
        second_influences.append(id)
third_ids = [id for id in second_influences if id not in done_ids]
third_ids_dict = dict([(id, 0) for id in third_ids])

# Scrape for the third time

for author_id in third_ids_dict:
    third_ids_dict[author_id] = author_info_scraper(author_id, third_ids_dict[author_id])
third_df = pd.DataFrame.from_dict(second_ids_dict, orient = "index", columns = ["name",
                                                                        "book_number",
                                                                        "born_date", 
                                                                        "died_date",
                                                                        "genres",
                                                                        "influence_names",
                                                                        "influence_ids",
                                                                        "gender"])
third_df.reset_index(inplace = True)
third_df.rename(columns = {"index": "id"}, inplace = True)
third_df = third_df.loc[third_df["id"] != "nan"]
third_df["id"] = third_df["id"].astype("Int64")

# Create final df

author_df = pd.read_csv("./author_data.csv")
final_df = pd.concat([author_df, second_df, third_df])

# Create edges

edges_table = []
edges_list = []
memberships_dict = {}

def edge_creator(id, influence_ids):
    edges_list = []
    if influence_ids == []:
        return edges_list
    influence_ids = str(influence_ids)
    influence_ids = ast.literal_eval(influence_ids)
    for influence in influence_ids:
        if influence:
            edges_list.append([int(influence), int(id)])
    return edges_list
edges_table = final_df.apply(lambda x: edge_creator(x.id, x.influence_ids), axis = 1)

for line in edges_table:
    for list in line:
        edges_list.append(list)

# Save edges

edges_list = [edge for edge in edges_list]
edges_df = pd.DataFrame(edges_list, columns = ["Source", "Target"])
edges_df["Type"] = "Directed"
edges_df.to_csv("./edges.csv", index = False)

# Get rid of unnedded columns, combine all dataframes and save complete node file

final_df = final_df[["id", "book_number", "name", "born_date", "died_date", "genres", "gender"]]
final_df.rename(columns = {"name": "Label"}, inplace = True)
final_df["id"] = final_df["id"].astype("Int64")
print(final_df.head())
final_df.to_csv("./nodes.csv", index = False, sep = ";")