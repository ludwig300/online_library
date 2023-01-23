from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("book_description.json", "r", encoding="utf8") as book_file:
        books_descriptions_json = book_file.read()
    books_descriptions = json.loads(books_descriptions_json)
    rendered_page = template.render(books=books_descriptions)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
