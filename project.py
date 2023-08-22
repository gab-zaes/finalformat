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
        self.font1 = ""
        self.font1_path = ""
        self.font1_italic = ""
        self.font2 = ""
        self.font2_path = ""
        self.indent = 6

    def footer(self):
        if self.footer_state:
            # Go to 1 cm from bottom
            self.set_y(-12)
            # Select Arial italic 8
            self.set_font(self.font1, "", 6)
            # Print page number
            if self.page_no() % 2 == 0:
                place = "L"
            else:
                place = "R"
            self.cell(0, 10, '%s' % self.page_no(), 0, 0, place)

    # def multi_cell(self, w, h, txt='', border=0, align='J', fill=0, split_only=False):
    #     ...


    def assign_fonts(self, font1, font2):
        match font1:
            case "0":
                self.font1 = "PT_Serif"
                self.font1_path = "./fonts/PT_Serif/PTSerif-Regular.ttf"
                self.font1_italic = "./fonts/PT_Serif/PTSerif-Italic.ttf"
            case "1":
                self.font1 = "EB_Garamond"
                self.font1_path = "./fonts/EB_Garamond/EBGaramond-Regular.ttf"
                self.font1_italic = "./fonts/EB_Garamond/EBGaramond-Italic.ttf"
            case "2":
                self.font1 = "Fira_Sans"
                self.font1_path = "./fonts/Fira_Sans/FiraSans-Regular.ttf"
                self.font1_italic = "./fonts/Fira_Sans/FiraSans-Italic.ttf"
            case _:
                self.font1 = "PT_Serif"
                self.font1_path = "./fonts/PT_Serif/PTSerif-Regular.ttf"
                self.font1_italic = "./fonts/PT_Serif/PTSerif-Italic.ttf"

        match font2:
            case "0":
                self.font2 = "Playfair"
                self.font2_path = "./fonts/Playfair_Display/PlayfairDisplay-Medium.ttf"
            case "1":
                self.font2 = "DMSans"
                self.font2_path = "./fonts/DM_Sans/DMSans-Medium.ttf"
            case "2":
                self.font2 = "Raleway"
                self.font2_path = "./fonts/Raleway/Raleway-Medium.ttf"
            case "3":
                self.font2 = "PlayfairSC"
                self.font2_path = "./fonts/Playfair_Display_SC/PlayfairDisplaySC-Regular.ttf"
            case _:
                self.font2 = "Playfair"
                self.font2_path = "./fonts/Playfair_Display/PlayfairDisplay-Medium.ttf"



# Global variables
INDENTATION_SPACES = 4
SMALL_SIZE = (125, 180)
REGULAR_SIZE = (140, 210)
LINE_SPACING = 4.6


def main():
    # in the main function, ingest the cli arguments with argparse
    parser = argparse.ArgumentParser(
        prog="finalformat",
        description="This program transforms docx and html files into formatted pdfs",
        epilog="Remember to input a docx or html file with a Title followed by Paragraphs sctructure!\n",
    )

    # add arguments to parser
    parser.add_argument("path", type=str, help="path to the docx or html file you want to format into pdf")
    parser.add_argument("-s", "--size", type=str, help="size of the page: expected Regular or Small. If omitted, defaults to Regular")
    parser.add_argument("-f", "--font_body", type=str, help="Pick one of the available fonts. 0: PT Serif; 1: EB Garamond; 2: Fira Sans. Defaults to 0 if omitted.")
    parser.add_argument("-t", "--font_title", type=str, help="0: Playfair Display; 1: DM Sans; 2: Raleway; 3: Playfair Display SC. Defaults to 0 if omitted.")
    parser.add_argument("-ta", "--title_align", type=str, help="write L for Left, R for Right, C for Center alignment of the title. Defaults to Left")

    # read the arguments into variable
    args = parser.parse_args()
   
    try:
        # returns list of Chapter objects
        chapters = read_file(args.path)
    except ValueError:
        sys.exit("File extension not supported! Try html or docx file")
        
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
            answer = input("\nWould you like to change the order of chapters(Y/N):").lower()
        except EOFError:
            sys.exit("Program interruptef by keyboard.")

        if answer in ["yes", "y", "sim", "s"]:
            swap = input("Which chapters, described as pairs of positive integer numbers separated by spaces \n \
    (ex: 1 5 3 7 10 9 => this will swap chapter 1 with 5, 3 with 7, and so on), would you like to swap? ").strip()
            if change_index(book, swap):
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
    """
    Reads the docx or html file and separates it into several strings (Title and Body), returning a list of Chapter objects.
    """
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
            body = re.sub("</p>", "\n", re.sub(r'<p>', "", body)).strip()
            body = " " * INDENTATION_SPACES + replace_tags(body).replace("\n", "\n" + " " * INDENTATION_SPACES)
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


def change_index(book, swap):
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
    if not path or not path.endswith(".pdf") or not book:
        raise ValueError

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

    # call assign fonts to consolidate fonts
    pdf.assign_fonts(book.font1, book.font2)

    # load custom fonts into memory
    load_fonts(pdf)  
    font = pdf.font1
    font2 = pdf.font2

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

    # empty page
    if pdf.page_no() % 2:
        pdf.add_page()

    # creat body of text from chapters. Always start at an odd number
    for chapter in book.index:
        pdf.add_page()
        # set footer_state as True so the numbers appear in the footer
        pdf.footer_state = True
        # make title cell
        pdf.set_font(font2, "", 20)
        pdf.cell(0, 0, chapter.title, align=title_align)

        # make paragraphs
        pdf.set_x(0)
        pdf.set_y(60)
        pdf.set_font(font, "", 8)
        pdf.multi_cell(0, LINE_SPACING, chapter.body)


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
    pdf.set_font(font, "", 7)
    pdf.set_y(book.size[1] / 3)
    pdf.multi_cell(0, 3, book.bio, align="C")

    pdf.set_y(20 + book.size[1] / 2)
    pdf.cell(0, 3, "Published in " + book.date, align="C")

    pdf.image("png/FinalFormat..png", x=(book.size[0] / 2) - 12.5, y=book.size[1] - 10, w=25, h=0, type="PNG")


    # save pdf to file
    try:
        pdf.output(path).encode("latin-1")
    except (MemoryError, OSError):
        return False
    
    return True


def load_fonts(pdf):
    """
    Loads the custom fonts into memory, exiting in case they are not found
    """
    try:
        pdf.add_font(pdf.font1, "", pdf.font1_path, uni=True)
        pdf.add_font(pdf.font1, "I", pdf.font1_italic, uni=True)
        pdf.add_font(pdf.font2, "", pdf.font2_path, uni=True)
    except RuntimeError:
        sys.exit("Unable to load fonts")

    return True


if __name__ == "__main__":
    main()