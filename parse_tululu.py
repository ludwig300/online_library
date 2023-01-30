import argparse
import logging
import os
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(page_response):
    soup = BeautifulSoup(page_response.text, 'lxml')
    title_tag = soup.select_one('body h1')
    title_text = title_tag.text
    title, author = title_text.split('::')
    image_url = urllib.parse.urljoin(
        page_response.url,
        soup.select_one('.bookimage img')['src']
    )
    comments = [comment.text for comment in soup.select('.texts .black')]
    genres_set = soup.select_one(
        '.d_book:-soup-contains("Жанр книги:")'
    ).select('a')
    genres = [genre.text for genre in genres_set]
    return {
        'title': title.strip(),
        'author': author.strip(),
        'image_url': image_url,
        'comments': comments,
        'genres': genres
    }


def download_comments(filename, comments, folder='./comments/'):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'w') as file:
        comments = map(lambda x: x + '\n', comments)
        file.writelines(comments)


def download_txt(url, filename, book_id, folder='./books/'):
    os.makedirs(folder, exist_ok=True)
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
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


def download_image(url, filename, folder='./images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(
        folder,
        sanitize_filename(filename)
    )
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def create_parser():
    parser = argparse.ArgumentParser(
        description='Download books, covers, comments'
    )
    parser.add_argument(
        '--start_id',
        default=1,
        help='book id. Default 1',
        type=int
    )
    parser.add_argument(
        '--end_id',
        default=10,
        help='book id. Default 10',
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
        page_url = f"https://tululu.org/b{book_id}/"
        page_response = requests.get(page_url)
        try:
            page_response.raise_for_status()
            check_for_redirect(page_response)
            book_page = parse_book_page(page_response)
            image_url = book_page['image_url']
            title = book_page['title']
            comments = book_page['comments']
            filename = f'{book_id}.{title}.txt'
            filename_img = f'{book_id}{get_extension(image_url)}'
            print('Название:', book_page['title'])
            print('Автор:', book_page['author'])
            download_txt(url, filename, book_id)
            download_image(image_url, filename_img)
            if comments:
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
