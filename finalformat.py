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
    def __init__(self, chapters: list, font1: str, font2: str, size: tuple, **meta):
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
        self.size = size     

    def change_chapters(self, n1: int, n2: int):
        length = len(self.index)
        if length >= n1 > 0 and length >= n2 > 0:
            # swap values using tmp variable
            tmp = self.index[n1 - 1]
            self.index[n1 - 1] = self.index[n2 - 1]
            self.index[n2 - 1] = tmp
        else:
            raise ValueError


class Chapter():
    def __init__(self, title: str, body: str):
        self.title = title
        self.body = body

    def __str__(self):
        return "\n    " + self._title + "\n\n    " + self._body


class PDF(FPDF):
    def __init__(self, orientation, unit, format):
        super().__init__(orientation, unit, format)
        self.footer_state = False

    def footer(self):
        if self.footer_state:
            # Go to 1 cm from bottom
            self.set_y(-12)
            # Select Arial italic 8
            self.set_font('Helvetica', '', 6)
            # Print page number
            if self.page_no() % 2 == 0:
                place = "L"
            else:
                place = "R"
            self.cell(0, 10, '%s' % self.page_no(), 0, 0, place)


# Global variables
INDENTATION_SPACES = 4
SMALL_SIZE = (125, 180)
REGULAR_SIZE = (140, 210)


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
    parser.add_argument("-f", "--font_body", type=str, help="Pick one of the available fonts. 0: Helvetica; 1: Times New Roman. Defaults to 1.")
    parser.add_argument("-t", "--font_title", type=str, help="0: <same font as font_body>; 0: Helvetica, 1: Times New Roman. Defaults to 0.")
    parser.add_argument("-ta", "--title_align", type=str, help="write L for Left, R for Right, C for Center alignment of the title")

    # read the arguments into variable
    args = parser.parse_args()
   
    try:
        # returns list of Chapter objects
        chapters = read_file(args.path)
    except ValueError:
        sys.exit("File extension not supported! Try html or docx file with title and paragraphs")
        
    # call function to add metadata (title, author, year, contact info, copywright, quote, bio) prompting the user first
    meta = get_meta()

    if args.size:
        match args.size.lower():
            case "regular":
                size = REGULAR_SIZE
            case "small":
                size = SMALL_SIZE
    
    else:
        size = REGULAR_SIZE

    # create Book object
    book = Book(chapters, args.font_body, args.font_title, size, **meta)

    # ask the user if he/she wants to change the order of chapters. If so, call change_index() to sort chapters in Book instance
    while True:
        try:
            answer = input("Would you like to change the order of chapters(Y/N):").lower()
        except EOFError:
            sys.exit("Program interruptef by keyboard.")

        if answer in ["yes", "y", "sim", "s"]:
            if change_index(book):
                print("\nSuccess! You changed the chapters order\n")
                break
            else:
                print("Failed to change the order.")
        elif answer in ["no", "n", "não"]:
            break

    # output the return value to consolidate() saving it to pdf by calling a function
    output_path = args.path.replace(".docx", ".pdf").replace(".html", ".pdf")
    if consolidate_pdf(book, output_path, args.title_align):
        print("\nSuccess! You have created a .pdf file\n")


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

    else:
        with open(path, "r") as html_file:
            html = html_file.read   

    splitted = re.split("<h1>", html)
    
    for s in splitted:
        if match := re.search(r'^(.+)</h1>(.*)', s):
            title, body = match.groups()
            body = re.sub("</p>", "\n", re.sub(r'<p>', "", body))
            body = replace_tags(body).replace("\n", f"\n{' ' * INDENTATION_SPACES}")
            l.append(Chapter(title, body))
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


def change_index(book):
    swap = input("Which chapters, described as pairs of positive integer numbers separated by spaces \n \
    (ex: 1 5 3 7 10 9 => this will swap chapter 1 with 5, 3 with 7, and so on), would you like to swap? ").strip()

    swap = swap.split(" ")

    # check for even number
    if not len(swap) % 2 == 0:
        print("error 0")
        return False

    # convert then to integers
    for i, n in enumerate(swap):
        try:
            swap[i] = int(n)
        except ValueError:
            print("error 1")
            return False
            
    # iterate over pairs to swap then
    for j in range(0, len(swap), 2):
        try:
            book.change_chapters(swap[j], swap[j + 1])
        except ValueError:
            print("error 2")
            return False

    return True


def replace_tags(string):
    string = re.sub(r'<em>', '"', string)
    string = re.sub(r'</em>', '"', string)
    string = re.sub(r'<strong>', '', string)
    string = re.sub(r'</strong>', '', string)
    return string


def consolidate_pdf(book, path, title_align):
    # create PDF instance
    pdf = PDF('P', 'mm', book.size)
    # set margins and page break
    m = book.size[0] / 8.5
    pdf.set_margins(m, m)
    pdf.set_auto_page_break(True, m - 2)

    # check for title alignment
    if title_align and title_align.upper() in ["R", "L", "C"]:
        title_align = title_align.upper()
    else:
        #default title alignment
        title_align = "L"

    # call match fonts to consolidate fonts
    font, font2 = match_fonts(book)

    # small title page
    pdf.add_page()
    pdf.set_font(font2, "", 8)
    pdf.set_y(book.size[1] / 2)
    pdf.cell(0, 3, book.title.upper(), align="R")

    # empty page
    pdf.add_page()

    # logo, author and title page
    pdf.add_page()
    pdf.set_y(10 + book.size[1] / 3)
    pdf.set_font(font2, "", 8)
    pdf.cell(0, 3, book.author.upper(), align="L")
    # a cell for the title
    pdf.set_y(20 + book.size[1] / 3)
    pdf.set_font(font2, "", 22)
    pdf.cell(0, 4, book.title.upper(), align="L")
    # another cell
    pdf.set_y(30 + book.size[1] / 3)
    pdf.set_font(font, "I", 8)
    pdf.cell(0, 3, "1st edition", align="R")
    # add finalformat. logo
    pdf.set_y(book.size[1])
    pdf.image("png/FinalFormat..png", x=book.size[0] - m - 30 , y=10 + book.size[1] / 2, w=30, h=0, type="PNG")


    # create page for metadata, formating a string from data
    data = f"    {book.title} / {book.author} ; \npowered by finalformat.\n\n    {book.date}\n    {book.contact}\n{book.license}\n"
    pdf.add_page()
    pdf.set_font(font, "", 5)
    pdf.set_y(book.size[1] - 60)
    pdf.multi_cell(pdf.get_string_width(book.title + book.author + book.license), 3, data, align="L", border=1)

    # create quote page (if it has a quote)
    pdf.add_page()
    if book.quote:
        try:
            quote, author = book.quote.rsplit('"', maxsplit=1)
            quote = quote.strip() + '"'
            author = author.strip()
        except (ValueError, IndexError):
            quote = book.quote
            author = ""

        pdf.add_page()
        pdf.set_font(font, "", 8)
        pdf.set_y(book.size[1] / 2)
        pdf.cell(0, 3, quote, align="R")

        pdf.set_font(font, "I", 8)
        pdf.set_y(4 + book.size[1] / 2)
        pdf.cell(0, 3, author, align="R")


    # creat body of text from chapters. 
    for chapter in book.index:
        # make title cell
        pdf.add_page()
        # set footer_state as True so the numbers appear in the footer
        pdf.footer_state = True
        pdf.set_font(font2, "", 20)
        pdf.cell(0, 0, chapter.title, align=title_align)

        # make paragraphs
        pdf.set_x(0)
        pdf.set_y(60)
        pdf.set_font(font, "", 8)
        pdf.multi_cell(0, 5.2, chapter.body)

    pdf.add_page()
    pdf.footer_state = False

    # calculate empty pages
    if pdf.page_no() % 2:
        empty_pages = 2
    else:
        empty_pages = 1

    for _ in range(empty_pages):
        pdf.add_page()

    # add bio page at the end (counter-folder)
    pdf.add_page()
    pdf.set_font(font2, "", 7)
    pdf.set_y(book.size[1] / 3)
    pdf.multi_cell(book.size[0] - (m + 10), 3, book.bio, align="C")

    pdf.set_y(20 + book.size[1] / 2)
    pdf.cell(0, 3, "Published in " + book.date, align="C")

    pdf.image("png/FinalFormat..png", x=(book.size[0] / 2) - 12.5, y=book.size[1] - 10, w=25, h=0, type="PNG")


    # save pdf to file
    try:
        pdf.output(path).encode("latin-1")
    except (MemoryError, OSError):
        return False
    
    return True


def match_fonts(book):
    match book.font1:
        case "0":
            font = "Helvetica"
        case "1":
            font = "Times"
        case _:
            font = "Times"

    match book.font2:
        case "0":
            font2 = "Helvetica"
        case "1":
            font2 = "Times"
        case _:
            font2 = "Helvetica" 
    return [font, font2]


if __name__ == "__main__":
    main()