import random
import string

import httpx


def get_random_lower_string():
    return "".join(random.choices(string.ascii_lowercase, k=32))


def get_random_pdf():
    candidate_urls = [
        "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/Dart.pdf",
        "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/Petresume.pdf",
        "https://raw.githubusercontent.com/pymupdf/PyMuPDF-Utilities/master/text-extraction/demo1.pdf",
    ]
    filename = get_random_lower_string() + ".pdf"
    resp = httpx.get(random.choice(candidate_urls))

    return filename, resp.read()
