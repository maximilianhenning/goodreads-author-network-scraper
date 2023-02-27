# goodreads-author-network-scraper
This is a tool that allows you to scrape data about the books you've read and about the authors who wrote them, and about their influences, from Goodreads.

It has the following dependencies:

- pandas
- requests
- json
- re
- datetime
- collections
- bs4
- ast

The way it works is like this: You get the four Python scrips in this repository and put them into a folder. Then, you export your personal Goodreads library (the exported file should helpfully be called "goodreads_library_export".) You put this file into the folder with the Python scripts and execute them one after the other in the correct order. This will take a while, as the data for every book and author need to be scraped individually because Goodreads shut down their API.

At the end, you should have several CSV files. Out of those:

- "book_data" has data on all books in your library
- "author_data" has data on all authors who wrote those books
- "nodes" and "edges" can be plugged into Gephi to generate a network of these authors, the authors who influenced them (according to Goodreads) and the authors who influenced those authors (also according to Goodreads).

I've not really had a lot of success with the network graph, since mine just looks really chaotic. In case anyone ever reads this and finds out a way to make them actually useful, let me know and I'll fix this tool accordingly. Same for all other suggestions you might have for it.