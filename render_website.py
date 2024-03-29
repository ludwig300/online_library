import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    parser = create_parser()
    args = parser.parse_args()
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open(args.json_path, "r", encoding="utf8") as book_file:
        books_descriptions_json = book_file.read()
    books_descriptions = json.loads(books_descriptions_json)
    books_number_per_page = 20
    number_of_columns = 2
    chunked_pages = list(chunked(books_descriptions, books_number_per_page))
    count_pages = len(chunked_pages)
    for id, chunked_books in enumerate(chunked_pages, 1):
        chunked_books_descriptions = list(
            chunked(chunked_books, number_of_columns)
        )
        rendered_page = template.render(
            books=chunked_books_descriptions,
            current_page=id,
            count_pages=count_pages
        )
        path = os.path.join('pages', f'index{id}.html')
        with open(path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def create_parser():
    parser = argparse.ArgumentParser(
        description='HTML page generator for a website with books'
    )
    parser.add_argument(
        "--json_path",
        default="book_description.json",
        help="Path to .json database. Default='book_description.json'"
    )
    return parser


def main():
    os.makedirs('pages', exist_ok=True)
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
