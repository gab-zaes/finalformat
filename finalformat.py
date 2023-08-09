import mammoth
import argparse
from fpdf import FPDF


class Book():
    def __init__(self, chapters: list, font: str, font2: str, **meta):
        self.index = chapters

        self.title = meta["title"]
        self.author = meta["author"]
        self.date = meta["date"]
        self.contact = meta["contact"]
        self.copy = meta["copy"]

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


    # call function to read html or docx file into memory
    # returns list of Chapter objects


    # call function to add metadata (title, author, year, contact info, copywright) prompting the user first
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