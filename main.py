import os

from bs4 import BeautifulSoup
import requests
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def get_book_title(book_id):
    url = f"https://tululu.org/b{book_id}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('h1')
    title_text = title_tag.text
    title, author = title_text.split('::')
    # image_url = (soup.find(class_='bookimage').find('img')['src'])
    return title.strip()


def download_txt(url, filename, folder='books/'):
    try:
        os.makedirs(f"./{folder}")
    except FileExistsError:
        pass
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file:
        file.write(url.content)

    return path


url = "https://tululu.org/txt.php"
for book_id in range(1, 11):
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        title = get_book_title(book_id)
        filename = f'{book_id}.{title}.txt'
        download_txt(response, filename, folder='books/')
    except requests.exceptions.HTTPError:
        pass
