import argparse
import logging
import os
import sys
import time

from bs4 import BeautifulSoup
import requests
from pathvalidate import sanitize_filename
import urllib.parse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def check_for_connection(response):
    if response.raise_for_status():

        raise requests.exceptions.ConnectionError


def parse_book_page(soup):
    title_tag = soup.find('body').find('h1')
    title_text = title_tag.text
    title, author = title_text.split('::')
    image_url = urllib.parse.urljoin(
        'https://tululu.org',
        soup.find(class_='bookimage').find('img')['src']
    )
    comments = [comment.text for comment in soup.select('.texts .black')]
    genres = [genre.text for genre in soup.select_one(
        '.d_book:-soup-contains("Жанр книги:")'
    ).find_all('a')]
    return {
        'title': title.strip(),
        'author': author.strip(),
        'image_url': image_url,
        'comments': comments,
        'genres': genres
    }


def download_comments(filename, comments, folder='comments/'):
    try:
        os.makedirs(f"./{folder}")
    except FileExistsError:
        pass
    path = os.path.join(folder, sanitize_filename(filename))
    if comments:
        with open(path, 'w') as file:
            comments = map(lambda x: x + '\n', comments)
            file.writelines(comments)
    else:
        pass


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


def create_parser():
    parser = argparse.ArgumentParser(
        description='Download books, covers, comments'
    )
    parser.add_argument(
        '--start_id',
        default=1,
        help='Book id. Default 1',
        type=int
    )
    parser.add_argument(
        '--end_id',
        default=10,
        help='Book id. Default 10',
        type=int
    )
    return parser


def main():
    logging.basicConfig(
        filename='app.log',
    )
    parser = create_parser()
    args = parser.parse_args()
    url = "https://tululu.org/txt.php"
    for book_id in range(args.start_id, args.end_id):
        payload = {'id': book_id}
        page_url = f"https://tululu.org/b{book_id}/"
        page_response = requests.get(page_url)
        response = requests.get(url, params=payload)
        try:
            response.raise_for_status()
            page_response.raise_for_status()
            check_for_redirect(page_response)
            check_for_redirect(response)
            page_soup = BeautifulSoup(page_response.text, 'lxml')
            book_page = parse_book_page(page_soup)
            image_url = book_page['image_url']
            title = book_page['title']
            comments = book_page['comments']
            filename = f'{book_id}.{title}.txt'
            filename_img = f'{book_id}{get_extension(image_url)}'
            print('Название:', book_page['title'])
            print('Автор:', book_page['author'])
            download_txt(response.url, filename)
            download_image(image_url, filename_img)
            download_comments(filename, comments)
        except requests.exceptions.HTTPError:
            sys.stderr.write('HTTP Error \n')
            logging.exception('HTTP Error \n')

        except requests.exceptions.ConnectionError:
            sys.stderr.write('Connection Error \n')
            logging.exception('Connection Error \n')
            time.sleep(10)

    sys.exit()


if __name__ == '__main__':
    main()
