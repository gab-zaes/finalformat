from project import read_file, change_index, consolidate_pdf, Book, Chapter
import pytest

meta = {
        "title": "",
        "author": "",
        "date": "",
        "contact": "",
        "license": "",
        "quote": "",
        "bio": ""
    }

def test_read_file():
    with pytest.raises(ValueError):
        read_file("files/Teste_maior.pdf")

    with pytest.raises(ValueError):
        read_file("files/foo")

    assert read_file("files/Teste.docx")


def test_change_index():
    chapters = [Chapter(f"{i}", f"{i}" * 100) for i in range(3)]
    book = Book(chapters, "0", "0", (100, 100), **meta)

    assert change_index(book, "1 2") == True

    assert change_index(book, "1 2 1 3 3 2") == True

    assert change_index(book, "1 3 2") == False

    assert change_index(book, "1 cat") == False

    assert change_index(book, "2 18") == False


def test_consolidate_pdf():
    chapters = [Chapter(f"{i}", f"{i}" * 100) for i in range(3)]
    book = Book(chapters, "0", "0", (100, 100), **meta)

    assert consolidate_pdf(book, "files/testing.pdf", "R") == True

    assert consolidate_pdf(book, "files/testing.pdf", "43") == True

    with pytest.raises(ValueError):
        consolidate_pdf(book, "", "R")

    with pytest.raises(ValueError):
        consolidate_pdf(book, "files/testing.html", "R")

    book = []
    with pytest.raises(ValueError):
        consolidate_pdf(book, "files/testing.pdf", "R")
