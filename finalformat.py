import mammoth
import argparse
import re
import sys
from fpdf import FPDF



class Book():
    """
    The Book class holds a index of Chapter instances in a list.
    It also holds extra information about the book, and the fonts that
    are going to be used in pdf formatting later.
    """
    def __init__(self, chapters: list, font1: str, font2: str, **meta):
        self.index = chapters

        self.title = meta["title"]
        self.author = meta["author"]
        self.date = meta["date"]
        self.contact = meta["contact"]
        self.license = meta["license"]
        self.quote = meta["quote"]
        self.bio = meta["bio"]

        self.font1 = font1
        self.font2 = font2       


class Chapter():
    def __init__(self, title: str, body: str):
        self.title = title
        self._body = body

    def __str__(self):
        return "\n    " + self._title + "\n\n    " + self._body

    # getter
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def body(self):
        return self._body


def main():
    # in the main function, ingest the cli arguments with argparse
    parser = argparse.ArgumentParser(
        prog="finalformat",
        description="This program transforms docx and html files into formatted pdfs",
        epilog="Remember to input a docx or html file with a Title and Paragraphs sctructure!\n",
    )

    # add arguments to parser
    parser.add_argument("path", type=str, help="path to the file you want to format into pdf")
    parser.add_argument("-s", "--size", type=str, help="size of the page: expected Regular or Small. If ommitted, defaults to Regular")
    parser.add_argument("-f", "--font_body", type=int, help="Pick one of the available fonts. 0: Libre Baskerville; 1: PT Serif; 2: Lato; 3: Fira Sans; 4: Helvetica. Defaults to 0.")
    parser.add_argument("-t", "--font_title", type=int, help="0: <same font as font_body>; 1: Baskerville Old Face; 2: Raleway; 3: DM Sans; 4: Helvetica. Defaults to 1.")

    # read the arguments into variable
    args = parser.parse_args()
   
    try:
        # returns list of Chapter objects
        chapters = read_file(args.path)
    except ValueError:
        sys.exit("File extension not supported! Try html or docx file with title and paragraphs")
        
    # call function to add metadata (title, author, year, contact info, copywright, quote, bio) prompting the user first
    meta = get_meta()

    # create Book object
    book = Book(chapters, args.font_body, args.font_title, **meta)

    # ask the user if he/she wants to change the order of chapters. If so, call change_index() to sort chapters in Book instance
    # return another version of Book object


    # output the return value to consolidate() saving it to pdf by calling a function
    # we must check for <em> and <strong> tags

    # returns FPDF object to be outputted
    return 0


def read_file(path: str):
    # variable for mammoth html convertion
    style_map = """
    p[style-name='Title'] => h1:fresh
    p[style-name='Section Title'] => h1:fresh
    p[style-name='Subsection Title'] => h1:fresh
    p[style-name='Heading 1'] => h1:fresh
    p[style-name='Heading 2'] => h1:fresh
    p[style-name='Heading 3'] => h1:fresh
    p[style-name='Heading 4'] => h1:fresh
    p[style-name='Heading 5'] => h1:fresh
    p[style-name='Heading 6'] => h1:fresh
    p[style-name='Comment'] => !
    """
    l = []

    if not path.endswith((".docx", ".docx/", ".html", ".html/")):
        raise ValueError

    elif path.endswith((".docx", ".docx/")):
        # first, lets find all the titles and replace then with separators "///"
        with open(path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, style_map=style_map)
            html = result.value
            html = re.sub(r'<a(\w|"|=| )+></a>', "", html)

    splitted = re.split("<h1>", html)
    
    for s in splitted:
        if match := re.search(r'^(.+)</h1>(.*)', s):
            title, body = match.groups()
            body = re.sub("</p>", "\n", re.sub(r'<p>', "", body))
            l.append(create_chapter(title, body))
    return l

        
def get_meta():
    print("\n\n    Now let's add some information about your book!\n\n")

    # empty fields here will be ignored in the future
    meta = {
        "title": "",
        "author": "",
        "date": "",
        "contact": "",
        "license": "",
        "quote": "",
        "bio": ""
    }       

    for key in meta:
        meta[key] = input(f"Add {key}: ")

    return meta


def create_chapter(title: str, body: str):
    return Chapter(title, body)




if __name__ == "__main__":
    main()