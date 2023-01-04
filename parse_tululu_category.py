import argparse
import logging
import os
import sys
import json
import time

from parse_tululu import (
    check_for_redirect,
    download_comments,
    download_image,
    download_txt,
    get_extension,
    parse_book_page
)

from bs4 import BeautifulSoup
import requests
import urllib.parse


def parse_page(response, urls):
    soup = BeautifulSoup(response.text, 'lxml')
    url_select = 'body .d_book .bookimage a'
    meta_books = soup.select(url_select)
    for meta_book in meta_books:
        url_book = urllib.parse.urljoin(
            response.url,
            meta_book['href']
        )
        urls.append(url_book)
    return urls


def get_book_id(url):
    scheme, netloc, path, *others = urllib.parse.urlparse(url)
    empty, path = path.split('/b')
    book_id = path.split('/')
    return book_id[0]


def create_parser():
    parser = argparse.ArgumentParser(
        description='Download books, covers, comments'
    )
    parser.add_argument(
        '--start_page',
        default=1,
        help='Number page for start download. Default 1',
        type=int
    )
    parser.add_argument(
        '--end_page',
        default=702,
        help='Number page for end download. Default 702',
        type=int
    )
    parser.add_argument(
        '--dest_folder',
        default='./',
        help='Folder of parsed data',
        type=str
    )
    parser.add_argument(
        '--skip_imgs',
        action="store_true",
        help='Skip download images',
    )
    parser.add_argument(
        '--skip_txt',
        action="store_true",
        help='Skip download images',
    )
    parser.add_argument(
        '--json_path',
        default='book_description.json',
        help='Path to *.json, default = book_description.json',
        type=str
    )
    return parser


def main():
    logging.basicConfig(
        filename='app.log',
    )
    parser = create_parser()
    args = parser.parse_args()
    dest_folder = args.dest_folder
    json_path = args.json_path
    urls = list()
    book_description = list()
    book_url = "https://tululu.org/txt.php"
    for page in range(args.start_page, args.end_page):
        url = f"https://tululu.org/l55/{page}"
        response = requests.get(url)
        response.raise_for_status()
        urls = parse_page(response, urls)

    for url in urls:
        page_response = requests.get(url)
        try:
            page_response.raise_for_status()
            check_for_redirect(page_response)
            book_page = parse_book_page(page_response)
            image_url = book_page['image_url']
            title = book_page['title']
            comments = book_page['comments']
            filename = f'{title}.txt'
            filename_img = f'{title}{get_extension(image_url)}'
            print(url)
            book_id = get_book_id(url)
            if not args.skip_txt:
                book_path = download_txt(
                    book_url,
                    filename,
                    book_id,
                    os.path.join(dest_folder, 'books/')
                )
                book_page['book_path'] = book_path
            if not args.skip_imgs:
                download_image(
                    image_url,
                    filename_img,
                    os.path.join(dest_folder, 'images/')
                )
            book_description.append(book_page)
            if comments:
                download_comments(
                    filename,
                    comments,
                    os.path.join(dest_folder, 'comments/')
                )
        except requests.exceptions.HTTPError:
            sys.stderr.write('HTTP Error \n')
            logging.exception('HTTP Error \n')

        except requests.exceptions.ConnectionError:
            sys.stderr.write('Connection Error \n')
            logging.exception('Connection Error \n')
            time.sleep(10)

    os.makedirs(dest_folder, exist_ok=True)
    with open(os.path.join(
        dest_folder,
        json_path
    ), "w", encoding='utf8') as my_file:
        json.dump(book_description, my_file, ensure_ascii=False)

    sys.exit()


if __name__ == '__main__':
    main()
