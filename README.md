# Parser online library [tululu.org](https://tululu.org/)

## This is parser can download:

- books
- covers
- comments
- science fiction books

### Requirements

* beautifulsoup4==4.11.1
* lxml==4.9.1
* requests==2.28.1
* pathvalidate==2.5.2

Remember, it is recommended to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for better isolation.
Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```
pip install -r requirements.txt
```

## Application launch

### Open project directory from cmd

```
$ python parse_tululu.py --start_id <START_ID> --end_id <END_ID>
```

`<START_ID>` - Specify the id of the book from which the download will start

`<END_ID>` - Specify the id of the book from which the download will end
This is an optional argument, by default from 1 to 10.

#### For download science fiction books

```
$ python parse_tululu_category.py
```

options:

  `-h, --help` show this help message and exit

  `--start_page START_PAGE` number page for start download. Default 1

  `--end_page END_PAGE`   number page for end download. Default 702

  `--dest_folder DEST_FOLDER`  folder of parsed data

  `--skip_imgs` skip download images

  `--skip_txt` skip download books

  `--json_path JSON_PATH`  path to *.json, default = book_description.json

## HTML page generator for a website with books

### Open project directory from cmd

```
$ python render_website.py
```

options:
  `-h, --help`            show this help message and exit
  `--json_path JSON_PATH`
                        Path to .json database. Default='book_description.json'

HTML pages will be generated in the `pages` folder

## You can see my [site](https://ludwig300.github.io/online_library)

![Desktop Screenshot 2023 01 29 - 21 26 32 10 (2)](https://user-images.githubusercontent.com/105148929/215333100-b39f412c-8065-4496-8769-8469616fb042.png)

*Project Goals*
Code for writing research on an online course for web developers [dvmn.org](https://dvmn.org/)
