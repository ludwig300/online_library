import os

import requests


try:
    os.makedirs("./books")
except FileExistsError:
    # directory already exists
    pass

for book_id in range(1, 11):
    url = f"https://tululu.org/txt.php?id={book_id}"

    response = requests.get(url)
    response.raise_for_status()

    filename = f'./books/book_{book_id}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)
