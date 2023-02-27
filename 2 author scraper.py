import pandas as pd
import requests
import json
import re
import datetime as dt
from collections import Counter
from bs4 import BeautifulSoup

df_books = pd.read_csv("./goodreads_library_export.csv")
df_books = df_books.loc[df_books["Read Count"] == 1].reset_index()
book_id_list = df_books["Book Id"].tolist()

author_id_list = []
def author_id_scraper(book_id):
    print("Working on book ID:", book_id)
    response = requests.get(str("https://www.goodreads.com/book/show/" + str(book_id)))
    html_string = response.text
    doc = BeautifulSoup(html_string, "html.parser")
    json_script = doc.find("script", attrs = {"type": "application/ld+json"})
    if json_script:
        json_content = json_script.text
        json_loaded = json.loads(json_content)
        author_id = json_loaded["author"][0]["url"].split("/")[-1].split(".")[0]
        return author_id
    else:
        return None
# Test book list
# author_id_list = [author_id_scraper(book_id) for book_id in [77040, 29847086, 86320, 35458, 61215351]]
# Full book list
author_id_list = [author_id_scraper(book_id) for book_id in book_id_list]
author_id_dict = Counter(author_id_list)

# Scrape all of additional author detail from author page

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
for author_id in author_id_dict:
    author_id_dict[author_id] = author_info_scraper(author_id, author_id_dict[author_id])

# Convert to dataframe, save to CSV

df = pd.DataFrame.from_dict(author_id_dict, orient = "index", columns = ["name",
                                                                        "book_number",
                                                                        "born_date", 
                                                                        "died_date",
                                                                        "genres",
                                                                        "influence_names",
                                                                        "influence_ids",
                                                                        "gender"])
df.reset_index(inplace = True)
df.rename(columns = {"index": "id"}, inplace = True)
df = df.loc[df["id"] != "nan"]
df["id"] = df["id"].astype("Int64")
print(df.head())
df.to_csv("./author_data.csv", index = False)