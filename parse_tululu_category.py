import logging
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
    meta_books = soup.find_all(class_='d_book')
    for meta_book in meta_books:
        url_book = urllib.parse.urljoin(
            response.url,
            meta_book.find('a')['href']
        )
        urls.append(url_book)
    return urls


def get_book_id(url):
    scheme, netloc, path, *others = urllib.parse.urlparse(url)
    empty, path = path.split('/b')
    book_id = path.split('/')
    return book_id[0]


def main():
    logging.basicConfig(
        filename='app.log',
    )
    urls = list()
    book_description = list()
    book_url = "https://tululu.org/txt.php"
    for page in range(1, 4):
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
            print('Название:', book_page['title'])
            print('Автор:', book_page['author'])
            book_id = get_book_id(url)
            book_path = download_txt(book_url, filename, book_id)
            download_image(image_url, filename_img)
            book_page['book_path'] = book_path
            book_description.append(book_page)
            if comments:
                download_comments(filename, comments)
        except requests.exceptions.HTTPError:
            sys.stderr.write('HTTP Error \n')
            logging.exception('HTTP Error \n')

        except requests.exceptions.ConnectionError:
            sys.stderr.write('Connection Error \n')
            logging.exception('Connection Error \n')
            time.sleep(10)

    with open("book_description.json", "w", encoding='utf8') as my_file:
        json.dump(book_description, my_file, ensure_ascii=False)

    sys.exit()


if __name__ == '__main__':
    main()
