import mammoth
import argparse
import re
from fpdf import FPDF


class Book():
    def __init__(self, chapters: list, font1: str, font2: str, **meta):
        self.index = chapters

        self.title = meta["title"]
        self.author = meta["author"]
        self.date = meta["date"]
        self.contact = meta["contact"]
        self.copy = meta["copy"]
        self.quote = meta["quote"]
        self.bio = meta["bio"]

        self.font1 = font1
        self.font2 = font2       


class Chapter():
    def __init__(self, name: str, body: str):
        self._name = name
        self._body = body

    # getter
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.name = name

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

    #add arguments to parser
    parser.add_argument("path", type=str, help="path to the file you want to format into pdf")
    parser.add_argument("-s", "--size", type=str, help="size of the page: expected Regular or Small. If ommitted, defaults to Regular")
    parser.add_argument("-f", "--font_body", type=int, help="Pick one of the available fonts. 0: Libre Baskerville; 1: PT Serif; 2: Lato; 3: Fira Sans; 4: Helvetica. Defaults to 0.")
    parser.add_argument("-t", "--font_title", type=int, help="0: <same font as font_body>; 1: Baskerville Old Face; 2: Raleway; 3: DM Sans; 4: Helvetica. Defaults to 1.")

    #read the arguments into variable
    args = parser.parse_args()

    print(args.path)


    # call function to read html or docx file into memory
    # returns list of Chapter objects


    # call function to add metadata (title, author, year, contact info, copywright, quote, bio) prompting the user first
    # returns Meta dictionary


    # call function to consolidate() the Book and Chapters structure
    # returns the complete Book instance


    # ask the user if he/she wants to change the order of chapters. If so, call change_index() to sort chapters in Book instance
    # return another version of Book object


    # output the return value to consolidate() saving it to pdf by calling a function
    # returns FPDF object to be outputted
    return 0
    

if __name__ == "__main__":
    main()