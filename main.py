import os

from bs4 import BeautifulSoup
import requests
from pathvalidate import sanitize_filename
import urllib.parse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def get_book_cover(book_id):
    url = f"https://tululu.org/b{book_id}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('h1')
    title_text = title_tag.text
    title, author = title_text.split('::')
    image_url = urllib.parse.urljoin(
        'https://tululu.org',
        soup.find(class_='bookimage').find('img')['src']
    )

    return title.strip(), image_url


def download_txt(url, filename, folder='books/'):
    try:
        os.makedirs(f"./{folder}")
    except FileExistsError:
        pass
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file:
        file.write(response.content)

    return path


def get_extension(urlstring):
    scheme, netloc, path_file, *others = urllib.parse.urlsplit(
        urlstring,
        scheme='',
        allow_fragments=True
    )
    unquoted_filename = urllib.parse.unquote(
        path_file,
        encoding='utf-8',
        errors='replace'
    )
    path, file = os.path.split(unquoted_filename)
    filename, extension = os.path.splitext(file)
    return extension


def download_image(url, filename, folder='images/'):
    try:
        os.makedirs(f"./{folder}")
    except FileExistsError:
        pass
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(
        folder,
        filename
    )
    with open(path, 'wb') as file:
        file.write(response.content)


def main():
    url = "https://tululu.org/txt.php"
    for book_id in range(1, 11):
        payload = {'id': book_id}
        response = requests.get(url, params=payload)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            title, image_url = get_book_cover(book_id)
            filename = f'{book_id}.{title}.txt'
            filename_img = f'{book_id}{get_extension(image_url)}'
            download_txt(response.url, filename)
            download_image(image_url, filename_img)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
