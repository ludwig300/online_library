import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked


def on_reload():
    os.makedirs('pages', exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("book_description.json", "r", encoding="utf8") as book_file:
        books_descriptions_json = book_file.read()
    books_descriptions = json.loads(books_descriptions_json)
    chunked_pages = list(chunked(books_descriptions, 20))

    for id, chunked_books in enumerate(chunked_pages, 1):
        chunked_books_descriptions = list(chunked(chunked_books, 2))
        rendered_page = template.render(books=chunked_books_descriptions)
        path = os.path.join('pages', f'index{id}.html')
        with open(path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
